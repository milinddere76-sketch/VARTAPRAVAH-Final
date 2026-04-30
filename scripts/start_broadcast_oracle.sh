#!/bin/bash

# Varta Pravah - Oracle Master Broadcast Starter
# This script launches both the Playlist Updater and the Eternal Streamer.

echo "🎙️ [MASTER] Starting Varta Pravah Broadcast System..."

# 1. Generate fallback video if it doesn't exist
if [ ! -f "/home/ubuntu/stream/fallback.mp4" ]; then
    echo "🎥 [MASTER] Generating initial fallback video..."
    bash scripts/create_fallback.sh
fi

# 2. Initial Playlist Build
echo "📝 [MASTER] Performing initial playlist build..."
bash scripts/update_playlist.sh

# 3. Start Playlist Updater (Every 30 seconds)
echo "🔁 [MASTER] Starting Playlist Auto-Updater in background..."
nohup watch -n 30 bash scripts/update_playlist.sh > /home/ubuntu/stream/updater.log 2>&1 &

# 4. Start Eternal Streamer (The YouTube Connection)
echo "📡 [MASTER] Starting Eternal Streamer in background..."
nohup bash scripts/oracle_playlist_streamer.sh > /home/ubuntu/stream/stream.log 2>&1 &

echo "✅ [MASTER] Broadcast System is LIVE."
echo "👉 Check /home/ubuntu/stream/stream.log for stream status."
