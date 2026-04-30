#!/bin/bash
# Varta Pravah - Oracle Relay Node Deployment

echo "🚀 Starting Streaming Relay Node Deployment..."

# 1. Update and Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl rsync ffmpeg

# 2. Create folders for video reception
mkdir -p /home/ubuntu/videos
mkdir -p /home/ubuntu/stream

# 3. Start Relay Service
docker-compose up --build -d streamer

echo "✅ Relay Node is ONLINE. Checking connection to Primary Node..."
