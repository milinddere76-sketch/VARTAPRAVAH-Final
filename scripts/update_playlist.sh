#!/bin/bash

# Varta Pravah - Dynamic Playlist Builder
# This script updates the playlist.txt file without stopping the FFmpeg stream.
# It ensures the latest news bulletins are always in the loop.

VIDEO_DIR="/home/ubuntu/videos"
PLAYLIST="/home/ubuntu/stream/playlist.txt"

echo "📝 [UPDATER] Refreshing playlist from $VIDEO_DIR..."

# 1. Clear current playlist
# Using a temporary file to ensure atomic update
TEMP_PLAYLIST="/tmp/playlist.tmp"
echo "" > $TEMP_PLAYLIST

# 2. Add latest 20 videos (most recent first)
for file in $(ls -t $VIDEO_DIR/*.mp4 2>/dev/null | head -n 20)
do
    echo "file '$file'" >> $TEMP_PLAYLIST
done

# 3. ALWAYS add the Fallback Loop at the end
# This ensures FFmpeg never hits the end of the file list.
if [ -f "/home/ubuntu/stream/fallback.mp4" ]; then
    echo "file '/home/ubuntu/stream/fallback.mp4'" >> $TEMP_PLAYLIST
elif [ -f "/app/assets/promo.mp4" ]; then
    echo "file '/app/assets/promo.mp4'" >> $TEMP_PLAYLIST
fi

# 4. Atomically move to the active playlist path
mv $TEMP_PLAYLIST $PLAYLIST

echo "✅ [UPDATER] Playlist updated with $(grep -c 'file' $PLAYLIST) items."
