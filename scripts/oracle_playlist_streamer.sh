#!/bin/bash

# Varta Pravah - Oracle Playlist-Based Streamer
# This script manages a dynamic playlist and ensures a continuous stream to YouTube.

VIDEO_DIR="/home/ubuntu/videos"
PLAYLIST="/home/ubuntu/stream/playlist.txt"
LOG="/home/ubuntu/stream/playlist_streamer.log"

# Load Stream Key
if [ -f "/app/.env" ]; then
    export $(grep -v '^#' /app/.env | xargs)
fi
STREAM_KEY=${YOUTUBE_STREAM_KEY:-"YOUR_YOUTUBE_STREAM_KEY"}

echo "🎶 [PLAYLIST] Starting Playlist-Based Continuous Streamer..."

# Function to refresh playlist
refresh_playlist() {
    echo "📝 Refreshing playlist..."
    # Get latest 5 videos and format for FFmpeg concat demuxer
    ls -t $VIDEO_DIR/*.mp4 2>/dev/null | head -n 5 | sed "s|^|file '|;s|$|'|" > $PLAYLIST
    
    if [ ! -s $PLAYLIST ]; then
        echo "⚠️ No videos found. Adding fallback loop."
        echo "file '/app/assets/promo.mp4'" > $PLAYLIST
    fi
}

while true
do
    refresh_playlist
    
    echo "🎬 [STREAM] Starting FFmpeg with playlist: $PLAYLIST"
    
    # Main stream command (Infinite Loop + Seamless Switching)
    ffmpeg -re -stream_loop -1 \
    -f concat -safe 0 -i "$PLAYLIST" \
    -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 \
    -c:v libx264 -preset veryfast -b:v 2500k \
    -c:a aac -b:a 128k \
    -f flv "rtmp://a.rtmp.youtube.com/live2/$STREAM_KEY" >> "$LOG" 2>&1
    
    echo "🔄 [STREAM] Playlist finished or FFmpeg exited. Refreshing and restarting..."
    sleep 2
done
