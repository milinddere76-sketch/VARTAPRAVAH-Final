# Varta Pravah AI News Encoder

Autonomous 24/7 Marathi AI News Broadcasting Platform.

## 🚀 Overview
Varta Pravah is an enterprise-grade AI news pipeline that automatically fetches news, generates Marathi scripts, synthesizes high-fidelity AI anchors, and streams to platforms like YouTube via RTMP.

## 📁 Project Structure
- `backend/`: FastAPI application, services, and workflows.
- `ai/`: AI models and synthesis engines (SadTalker, Wav2Lip).
- `assets/`: Media assets, logos, and fonts.
- `streaming/`: Nginx-RTMP configuration and streamer logic.
- `scripts/`: Deployment and maintenance scripts.
- `logs/`: System and application logs.

## 🛠️ Setup & Installation
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in the API keys.
3. Build and start the containers:
   ```bash
   docker-compose up --build -d
   ```

## 📡 Tech Stack
- **Backend**: FastAPI, Redis, PostgreSQL.
- **AI**: SadTalker, TTS (XTTS v2), Groq (LLM).
- **Streaming**: FFmpeg, Nginx-RTMP.
- **Infrastructure**: Docker, Coolify.

## 📜 License
Proprietary - Enterprise Edition.
