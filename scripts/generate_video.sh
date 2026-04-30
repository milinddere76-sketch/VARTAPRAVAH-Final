#!/bin/bash

# Varta Pravah - Test Video Generation Utility
# This script generates a test video using a static image and dummy audio.

OUTPUT="/app/output/news.mp4"
AUDIO="/tmp/audio.mp3"
IMAGE="/app/assets/studio.jpg"

# Ensure output directory exists
mkdir -p /app/output

# 1. Generate dummy audio (30 seconds sine wave)
echo "🎙️ Generating dummy audio..."
ffmpeg -y -f lavfi -i sine=frequency=1000:duration=30 -q:a 9 -acodec libmp3lame $AUDIO

# 2. Check if image exists, otherwise use a color placeholder
if [ ! -f "$IMAGE" ]; then
    echo "⚠️  Image $IMAGE not found. Using black background."
    IMAGE_INPUT="-f lavfi -i color=c=black:s=1280x720:d=30"
else
    IMAGE_INPUT="-loop 1 -i $IMAGE"
fi

# 3. Create video
echo "🎬 Creating video: $OUTPUT"
ffmpeg -y $IMAGE_INPUT -i $AUDIO \
-shortest -c:v libx264 -preset veryfast -tune stillimage \
-c:a aac -b:a 128k -pix_fmt yuv420p $OUTPUT

echo "✅ Video created successfully: $OUTPUT"
