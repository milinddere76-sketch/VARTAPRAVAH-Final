# Varta Pravah - Enterprise Installation Guide

Welcome to the **Varta Pravah** AI News Ecosystem. This guide provides step-by-step instructions for deploying the 24/7 autonomous Marathi news pipeline.

## 🏗️ System Overview
- **Primary Node (Hetzner)**: Handles AI synthesis (SadTalker, TTS, News Generation).
- **Relay Node (Oracle)**: Handles 24/7 RTMP streaming and commercial breaks.

---

## 🛠️ Step 1: Environment Setup

### 1. Hardware Requirements
- **Primary Node**: Ubuntu 22.04+, 16GB RAM (32GB recommended), 4-8 vCPUs. GPU (NVIDIA) is optional but highly recommended for faster synthesis.
- **Relay Node**: Oracle Cloud Free Tier (ARM or x86), 4GB+ RAM.

### 2. Software Prerequisites
On both servers, run:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git curl rsync ffmpeg openssh-client
```

---

## ⚙️ Step 2: Configuration

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/vartapravah-ai-news-encoder.git
    cd vartapravah-ai-news-encoder
    ```

2.  **Configure Environment Variables**:
    Copy `.env.example` to `.env` and fill in your keys:
    ```bash
    cp .env.example .env
    nano .env
    ```
    - `NEWS_API_KEY`: Get from [newsapi.org](https://newsapi.org/)
    - `GROQ_API_KEY`: Get from [groq.com](https://groq.com/)
    - `YOUTUBE_STREAM_KEY`: Get from your YouTube Live Dashboard.

---

## 🔐 Step 3: Node Inter-Connectivity (SSH Setup)

To enable automated video transfers from Hetzner to Oracle, you must set up passwordless SSH.

1.  **Generate SSH Key (On Hetzner)**:
    ```bash
    ssh-keygen -t rsa -b 4096
    ```
    *Press Enter for all prompts (no passphrase).*

2.  **Copy Key to Oracle**:
    ```bash
    ssh-copy-id ubuntu@<ORACLE_IP>
    ```

3.  **Test the Connection**:
    ```bash
    ssh ubuntu@<ORACLE_IP>
    ```
    *If you log in without a password, the automated pipeline is ready.*

---

## 🚀 Step 4: Deployment

### 1. Deploying the Primary Node (Hetzner)
On the server intended for AI processing:
```bash
docker-compose up -d --build
```
*This starts the AI production engine, database, and Temporal workers.*

### 2. Deploying the Relay Node (Oracle)
On the server intended for streaming:
```bash
docker-compose -f docker-compose.relay.yml up -d --build
```
*This starts only the lightweight streaming engine and Nginx-RTMP gateway.*

---

## 📊 Step 5: Monitoring & Control

- **Dashboard**: Access `http://your-primary-ip:8000` to view the control panel.
- **Logs**:
  - `docker-compose logs -f` for general logs.
  - Check `logs/streamer.log` for streaming diagnostics.
- **Health**: Run `bash scripts/healthcheck.sh` to verify system integrity.

## 🔄 Step 6: Auto-Start & Recovery
All services are configured with `restart: always`. They will automatically start on boot and recover from crashes.

---

## 🛑 Troubleshooting
- **Memory Errors**: Ensure the 8GB swap is active (`swapon --show`).
- **Stream Drops**: Check `HETZNER_NODE_URL` in the relay server's `.env`.
- **Model Download**: SadTalker will download ~2GB of models on the first run. Ensure you have a stable internet connection.

---
© 2026 Varta Pravah Enterprise. Autonomous Marathi AI News.
