#!/bin/bash
# Varta Pravah - Hetzner Primary Node Deployment

echo "🚀 Starting Primary AI Node Deployment..."

# 1. Update and Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git rsync

# 2. Setup Swap (Crucial for SadTalker/AI)
if [ ! -f /swapfile ]; then
    echo "💾 Creating 8GB Swap..."
    sudo fallocate -l 8G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# 3. Clone/Update Repo (Assuming already in repo dir or using git)
# git pull origin main

# 4. Start Infrastructure
docker-compose up --build -d

echo "✅ Primary Node is ONLINE at http://$(hostname -I | awk '{print $1}'):8000"
