# Varta Pravah - Final Multi-Node Architecture

The system is optimized for a high-performance, automated pipeline across two cloud providers.

## 🏗️ The Core Workflow

### 1. 🏭 Hetzner (Processing Server)
*   **Role**: AI Factory (Heavy CPU/GPU).
*   **Folder Structure**:
    ```text
    /app/
    ├── output/   (Temporary video storage)
    ├── scripts/  (Deployment & Utility scripts)
    └── logs/     (System & AI diagnostics)
    ```
*   **Tasks**:
    *   **Generate**: News video synthesis (AI Anchor + Neural TTS + FFmpeg).
    *   **Auto-Transfer**: Immediately push the final video to Oracle via `rsync`.
    *   **Auto-Cleanup**: Delete local video files immediately after successful transfer to save disk space.

### 2. 📡 Oracle Cloud (Streaming Server)
*   **Role**: Broadcast Station (Network Stability).
*   **Tasks**:
*   **Receive**: Automated reception of videos from Hetzner.
*   **Auto-Stream**: Nginx-RTMP relay pushes the video to YouTube Live 24/7.
*   **Store**: Maintains only minimal necessary files for the active broadcast.
*   **Auto-Cleanup**: Regularly delete received files older than 60 minutes to prevent disk exhaustion.
    *   *Command*: `find /home/ubuntu/videos -type f -mmin +60 -delete` (Recommended as a 30-min cron job).

---

## 🚀 Automated Synchronization (Production Flow)

To ensure maximum reliability and speed, the system uses a strict **Generate ➔ Transfer ➔ Delete** policy.

### METHOD: RSYNC (FAST + RELIABLE)

#### 1. Preparation
*   **Hetzner**: Install rsync:
    ```bash
    apt update && apt install -y rsync
    ```
*   **Oracle**: Create the destination folder:
    ```bash
    mkdir -p /home/ubuntu/videos
    ```

#### 2. Synchronization Command (Automated in Worker)
The worker automatically executes this command after rendering:
```bash
rsync -avz /app/output/final_bulletin_TIMESTAMP.mp4 ubuntu@ORACLE_IP:/home/ubuntu/videos/
```

#### 3. 🧹 Auto Cleanup (Hetzner)
The AI node automatically clears the `/app/output` folder after every successful transfer to prevent RAM/Storage exhaustion.

#### 📶 4. Network & Security Check
*   **Port 22**: Must be open for SSH/rsync.
*   **Firewall**: Oracle Cloud ingress rules must allow the Hetzner IP on Port 22.
*   **SSH Keys**: SSH key-based authentication is required for the automated transfer script.

---

## 🛑 Troubleshooting Common Issues

### ❌ Permission denied (rsync)
If you see authentication errors during transfer, ensure your SSH permissions are strict:
*   **On Oracle (Relay)**:
    ```bash
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/authorized_keys
    ```

### ❌ NewsProductionWorkflow TypeError
If the worker crashes with missing arguments, ensure you have pulled the latest code and rebuilt the worker container:
```bash
docker-compose up -d --build worker
```
