FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=1000

# Install required system libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone SadTalker with compression
RUN git clone https://github.com/OpenTalker/SadTalker.git && \
    cd SadTalker && \
    git config core.compression 9

WORKDIR /app/SadTalker

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install numpy==1.26.4
RUN pip install pillow==10.2.0

# Install heavy AI packages manually (CPU versions for build stability)
# Using CPU wheels to avoid huge image size and build timeouts
RUN pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt -vvv

# Make output directory
RUN mkdir -p /app/output /app/checkpoints

# Default command - Download models ONCE at runtime, then stay ready
# This makes the Docker build fast (minutes) instead of hours.
CMD ["/bin/bash", "-c", "if [ ! -d '/app/SadTalker/checkpoints' ]; then bash scripts/download_models.sh; fi; python3 inference.py"]
