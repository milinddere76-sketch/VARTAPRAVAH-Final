#!/bin/bash

# VARTAPRAVAH - Oracle Server Swap Setup Script
# This script adds a 4GB swap file to prevent silent crashes on Oracle Free Tier.

echo "🚀 Starting Swap Setup..."

# 1. Create a 4GB swap file
echo "📦 Allocating 4GB swap file..."
sudo fallocate -l 4G /swapfile

# 2. Secure the swap file
echo "🔒 Setting permissions..."
sudo chmod 600 /swapfile

# 3. Format as swap
echo "🛠️ Formatting swap..."
sudo mkswap /swapfile

# 4. Enable swap
echo "🔄 Enabling swap..."
sudo swapon /swapfile

# 5. Make it permanent
if ! grep -q "/swapfile" /etc/fstab; then
    echo "💾 Making swap permanent in /etc/fstab..."
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo "✅ Swap setup complete!"
free -h
