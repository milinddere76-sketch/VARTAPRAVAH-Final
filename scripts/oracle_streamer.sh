#!/bin/bash

# Varta Pravah - Oracle Automated YouTube Streamer
# This script picks the latest video from the reception folder and pushes it to YouTube Live.

VIDEO_DIR="/home/ubuntu/videos"

# Load Stream Key from environment or .env
if [ -f "/app/.env" ]; then
    export $(grep -v '^#' /app/.env | xargs)
fi

STREAM_KEY=${YOUTUBE_STREAM_KEY:-"YOUR_YOUTUBE_STREAM_KEY"}

echo "📡 [STREAMER] Starting Oracle Relay Streamer..."

while true
do
    # Find the latest .mp4 file by modification time
    FILE=$(ls -t $VIDEO_DIR/*.mp4 2>/dev/null | head -n 1)

    if [ -n "$FILE" ]; then
        echo "🎬 [STREAM] Playing latest video: $FILE"
        
        # FFmpeg stream to YouTube
        ffmpeg -re -i "$FILE" \
        -c:v libx264 -preset veryfast -b:v 2500k \
        -c:a aac -b:a 128k \
        -f flv "rtmp://a.rtmp.youtube.com/live2/$STREAM_KEY"
        
        echo "🔄 [STREAM] Video finished. Searching for updates..."
        sleep 2
    else
        echo "⏳ [IDLE] No video found in $VIDEO_DIR. Waiting for transfer..."
        sleep 10
    fi
done
