#!/bin/bash

# Configuration
REMOTE_VIDEO="/app/videos/output.mp4"
LOCAL_FALLBACK="/app/assets/promo.mp4"

while true
do
  # Choose the source
  if [ -f "$REMOTE_VIDEO" ]; then
    SOURCE="$REMOTE_VIDEO"
    echo "🌐 [PRIMARY] Streaming news from Hetzner node..."
  else
    SOURCE="$LOCAL_FALLBACK"
    echo "🛡️ [FALLBACK] Hetzner video missing. Streaming local promo..."
  fi

  # Note: $YOUTUBE_RTMP_URL should be set in the .env
  ffmpeg -re -i "$SOURCE" \
    -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k \
    -pix_fmt yuv420p -g 50 \
    -c:a aac -b:a 128k \
    -f flv "$YOUTUBE_RTMP_URL"

  echo "⚠️ Stream ended or crashed. Checking connection and restarting in 5 sec..."
  sleep 5
done
