#!/bin/bash

# Varta Pravah - Fallback Video Generator
# This creates a 1-hour static fallback loop to ensure the stream never stops.

IMAGE="/app/assets/studio.jpg"
OUTPUT="/home/ubuntu/stream/fallback.mp4"

echo "🎥 [FALLBACK] Generating 1-hour fallback video..."

# Ensure directory exists
mkdir -p /home/ubuntu/stream

if [ ! -f "$IMAGE" ]; then
    echo "⚠️ Image $IMAGE not found. Creating black fallback."
    IMAGE_INPUT="-f lavfi -i color=c=black:s=1280x720:d=3600"
else
    IMAGE_INPUT="-loop 1 -i $IMAGE -t 3600"
fi

# Generate 1-hour static video
ffmpeg -y $IMAGE_INPUT \
-vf "scale=1280:720,format=yuv420p" \
-c:v libx264 -preset ultrafast -tune stillimage \
-c:a aac -b:a 128k \
-ar 44100 -ac 2 \
$OUTPUT

echo "✅ [FALLBACK] Created: $OUTPUT"
