#!/bin/bash

# Configuration
HETZNER_URL=${HETZNER_NODE_URL:-"http://hetzner-ip:8000"}
LOCAL_FALLBACK="/app/assets/promo.mp4"
AD_SLOT="/app/assets/promo.mp4"
DOWNLOAD_PATH="/app/videos/latest_news.mp4"
LOG_FILE="/app/logs/streamer.log"
LAST_FILENAME=""
NEWS_COUNTER=0

mkdir -p /app/videos /app/logs

exec > >(tee -a "$LOG_FILE") 2>&1

echo "📡 [$(date)] [STREAMER] VartaPravah Ingest Started."

if [ -z "$YOUTUBE_STREAM_KEY" ]; then
    echo "❌ [FATAL] YOUTUBE_STREAM_KEY missing"
    exit 1
fi

while true
do
  # 1. Commercial Logic
  if [ "$NEWS_COUNTER" -ge 2 ]; then
    echo "📺 [$(date)] [PROMO] Starting break..."
    SOURCE="$AD_SLOT"
    NEWS_COUNTER=0
  else
      # 2. Poll logic
      RESPONSE=$(curl -s --max-time 10 "$HETZNER_URL/api/latest-video")
      
      if [ $? -ne 0 ]; then
        echo "🛡️ [$(date)] [CONNECTION] Primary Node ($HETZNER_URL) Offline"
        SOURCE="$LOCAL_FALLBACK"
      elif echo "$RESPONSE" | grep -q '"status":"success"'; then
        NEW_FILENAME=$(echo $RESPONSE | grep -oP '"filename":"\K[^"]+')
        VIDEO_URL=$(echo $RESPONSE | grep -oP '"video_url":"\K[^"]+')
        
        if [ "$NEW_FILENAME" != "$LAST_FILENAME" ]; then
          echo "📥 [$(date)] [NEW-VIDEO] Downloading $NEW_FILENAME..."
          curl -s "$HETZNER_URL$VIDEO_URL" -o "${DOWNLOAD_PATH}.tmp"
          if [ $? -eq 0 ]; then
            mv "${DOWNLOAD_PATH}.tmp" "$DOWNLOAD_PATH"
            SOURCE="$DOWNLOAD_PATH"
            LAST_FILENAME="$NEW_FILENAME"
            NEWS_COUNTER=$((NEWS_COUNTER + 1))
            echo "✅ [$(date)] [READY] Bulletin Switched to $NEW_FILENAME"
          else
            echo "⚠️ [$(date)] [DOWNLOAD] Failed for $NEW_FILENAME"
            SOURCE="$LOCAL_FALLBACK"
          fi
        else
          SOURCE="$DOWNLOAD_PATH"
          [ ! -f "$SOURCE" ] && SOURCE="$LOCAL_FALLBACK"
        fi
      else
        ERROR_MSG=$(echo $RESPONSE | grep -oP '"message":"\K[^"]+')
        echo "⏳ [$(date)] [IDLE] Backend Online. Status: $ERROR_MSG (Waiting for first bulletin...)"
        SOURCE="$LOCAL_FALLBACK"
      fi
    fi

  # 3. Persistent Broadcast (Strict CBR 2500k)
  echo "🚀 [$(date)] [BROADCAST] Source: $(basename $SOURCE)"
  
  # Check if source exists, if not, use a synthetic placeholder to keep YouTube alive
  if [ ! -f "$SOURCE" ]; then
      echo "⚠️ [$(date)] [FAILOVER] Source missing! Generating high-bitrate placeholder..."
      # This generates a 720p black screen with scrolling text to maintain bitrate
      ffmpeg -re -f lavfi -i "color=c=black:s=1280x720:r=25" \
        -f lavfi -i "sine=f=440:b=4" \
        -c:v libx264 -preset superfast -tune zerolatency \
        -b:v 2500k -minrate 2500k -maxrate 2500k -bufsize 5000k \
        -nal-hrd cbr -pix_fmt yuv420p -g 50 -r 25 \
        -c:a aac -b:a 128k -ar 44100 \
        -t 10 -f flv "rtmp://localhost/live/stream"
      sleep 1
      continue
  fi

  # Regular Streaming
  ffmpeg -re -i "$SOURCE" \
    -c:v libx264 -preset superfast -tune zerolatency \
    -b:v 2500k -minrate 2500k -maxrate 2500k -bufsize 5000k \
    -nal-hrd cbr -pix_fmt yuv420p -g 50 -r 25 \
    -c:a aac -b:a 128k -ar 44100 \
    -fflags +genpts \
    -f flv "rtmp://localhost/live/stream" 2>> "$LOG_FILE"

  if [ $? -ne 0 ]; then
    echo "🚨 [$(date)] [FFMPEG] Process crashed or disconnected. Self-healing in 2s..."
  fi
  
  sleep 2
done
