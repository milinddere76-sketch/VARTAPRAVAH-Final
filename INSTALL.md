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
sudo apt-get install -y docker.io docker-compose git curl
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

## 🚀 Step 3: Deployment

### 1. Deploying the Primary Node (Hetzner)
On the server intended for AI processing:
```bash
docker-compose --profile primary up -d --build
```
*This starts the AI engine, database, and Temporal orchestrator.*

### 2. Deploying the Relay Node (Oracle)
On the server intended for streaming:
```bash
docker-compose --profile relay up -d --build
```
*This starts only the Nginx-RTMP gateway and the relay engine. Ensure HETZNER_NODE_URL is set correctly in .env.*

---

## 📊 Step 4: Monitoring & Control

- **Dashboard**: Access `http://your-primary-ip:8000` to view the control panel.
- **Logs**:
  - `docker-compose logs -f` for general logs.
  - Check `logs/streamer.log` for streaming diagnostics.
- **Health**: Run `bash scripts/healthcheck.sh` to verify system integrity.

## 🔄 Step 5: Auto-Start & Recovery
All services are configured with `restart: always`. They will automatically start on boot and recover from crashes.

---

## 🛑 Troubleshooting
- **Memory Errors**: Ensure the 8GB swap is active (`swapon --show`).
- **Stream Drops**: Check `HETZNER_NODE_URL` in the relay server's `.env`.
- **Model Download**: SadTalker will download ~2GB of models on the first run. Ensure you have a stable internet connection.

---
© 2026 Varta Pravah Enterprise. Autonomous Marathi AI News.
