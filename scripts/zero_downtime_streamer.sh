#!/bin/bash

# Varta Pravah - Zero-Downtime Live Stream System
# This script ensures the YouTube RTMP connection NEVER drops.
# It uses a named pipe to feed a continuous FFmpeg process.

VIDEO_DIR="/home/ubuntu/videos"
PIPE="/tmp/stream_pipe"
LOG="/home/ubuntu/stream/zero_downtime.log"

# Load Stream Key
if [ -f "/app/.env" ]; then
    export $(grep -v '^#' /app/.env | xargs)
fi
STREAM_KEY=${YOUTUBE_STREAM_KEY:-"YOUR_YOUTUBE_STREAM_KEY"}

# Ensure pipe exists
[ -p $PIPE ] || mkfifo $PIPE

echo "🧠 [ZERO-DOWNTIME] Starting Continuous Streamer..."

# ---------------------------------------------------------
# 1. THE ETERNAL STREAMER (Runs in background)
# This process keeps the connection to YouTube alive forever.
# It reads from the pipe and pushes to RTMP.
# ---------------------------------------------------------
(
    while true; do
        ffmpeg -re -i "$PIPE" \
        -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 \
        -c:v libx264 -preset veryfast -b:v 2500k \
        -c:a aac -b:a 128k \
        -f flv "rtmp://a.rtmp.youtube.com/live2/$STREAM_KEY" >> "$LOG" 2>&1
        
        echo "⚠️ [FFMPEG] Stream process exited. Restarting in 2s..." >> "$LOG"
        sleep 2
    done
) &

# ---------------------------------------------------------
# 2. THE PLAYLIST FEEDER (Runs in foreground)
# This loop continuously feeds the latest video into the pipe.
# ---------------------------------------------------------
while true
do
    # Find the latest video
    FILE=$(ls -t $VIDEO_DIR/*.mp4 2>/dev/null | head -n 1)

    if [ -n "$FILE" ]; then
        echo "🎬 [FEEDER] Sending to pipe: $FILE"
        # We use 'cat' to stream the file into the pipe. 
        # The background FFmpeg will consume it at real-time speed (-re).
        cat "$FILE" > "$PIPE"
        
        echo "🔄 [FEEDER] Video finished. Checking for next..."
    else
        echo "⏳ [IDLE] No news video. Playing fallback loop..."
        # If no news video, play a fallback if it exists
        if [ -f "/app/assets/promo.mp4" ]; then
            cat "/app/assets/promo.mp4" > "$PIPE"
        else
            sleep 5
        fi
    fi
done
