FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# 🔧 Step 1 — Install system dependencies FIRST
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak-ng \
    libsndfile1 \
    build-essential \
    git \
    curl \
    ca-certificates \
    libgl1 \
    libglib2.0-0 \
    libpq-dev \
    fonts-noto-ui-core \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# 🔧 Step 1.5 — Install CPU-ONLY Torch (Saves 2-3GB Disk Space!)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 🔧 Step 2 — Install Python deps (NO --user)
RUN pip install --no-cache-dir cython numpy==1.23.5

# 🔧 Step 3 — Install requirements FIRST
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔧 Step 4 — Install TTS LAST (important)
RUN pip install --no-cache-dir TTS

# Install Docker CLI manually (Detect architecture for ARM/X64 support)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ]; then DOCKER_ARCH="aarch64"; else DOCKER_ARCH="x86_64"; fi && \
    curl -fsSL "https://download.docker.com/linux/static/stable/${DOCKER_ARCH}/docker-24.0.7.tgz" | tar -xzC /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    chmod +x /usr/local/bin/docker && \
    rm -rf /tmp/docker

# Copy the project files
COPY . .

# Internal fallback assets
RUN mkdir -p /app/assets_internal && cp -r /app/assets/* /app/assets_internal/ || true

# Default to running the backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
