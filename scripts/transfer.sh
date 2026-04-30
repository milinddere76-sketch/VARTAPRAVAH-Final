#!/bin/bash

# Varta Pravah - Automated Video Transfer & Cleanup Utility
# Usage: bash scripts/transfer.sh [optional_file_path]

# Load ORACLE_NODE_IP from environment if available
ORACLE_IP=${ORACLE_NODE_IP:-"ORACLE_IP_NOT_SET"}
FILE=${1:-"/app/output/news.mp4"}
DEST="ubuntu@$ORACLE_IP:/home/ubuntu/videos/"

if [ "$ORACLE_IP" == "ORACLE_IP_NOT_SET" ]; then
    echo "🚨 Error: ORACLE_NODE_IP environment variable is not set."
    exit 1
fi

if [ -f "$FILE" ]; then
    echo "📤 Transferring video: $FILE to $ORACLE_IP..."
    
    # Perform rsync transfer
    rsync -avz --progress "$FILE" "$DEST"
    
    if [ $? -eq 0 ]; then
        echo "✅ Transfer successful. Deleting local file: $FILE"
        rm -f "$FILE"
    else
        echo "❌ Transfer failed. Keeping local file for retry."
        exit 1
    fi
else
    echo "ℹ️  No file found at $FILE to transfer."
fi
