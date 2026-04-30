#!/bin/bash

# Varta Pravah - High-Frequency Loop Runner (Full Automation)
# This script continuously triggers generation and transfer every 10 seconds.
# WARNING: This is a standalone runner. Ensure it doesn't conflict with your Temporal worker.

echo "🚀 [RUNNER] Starting Automated Loop (Interval: 10s)..."

while true
do
    echo "--- 🕒 New Cycle Started: $(date) ---"
    
    # 1. Generate Test Video
    bash /app/scripts/generate_video.sh
    
    # 2. Transfer to Oracle & Cleanup Hetzner
    bash /app/scripts/transfer.sh
    
    echo "--- 😴 Cycle Complete. Sleeping... ---"
    sleep 10
done
