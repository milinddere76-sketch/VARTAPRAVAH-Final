#!/bin/bash
# Varta Pravah - Oracle Relay Node Deployment

echo "🚀 Starting Streaming Relay Node Deployment..."

# 1. Update and Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl

# 2. Start Relay Service
# We only need the streamer service on the Oracle node
docker-compose up --build -d streamer

echo "✅ Relay Node is ONLINE. Checking connection to Primary Node..."
