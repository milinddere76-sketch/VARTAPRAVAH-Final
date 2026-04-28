FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# ---------------------------
# SYSTEM DEPENDENCIES
# ---------------------------
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
    espeak-ng \
    curl \
    git \
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------
# WORKDIR
# ---------------------------
WORKDIR /app

# ---------------------------
# COPY REQUIREMENTS
# ---------------------------
COPY backend/requirements.txt .

# ---------------------------
# INSTALL PYTHON DEPS
# ---------------------------
RUN pip install --upgrade pip setuptools wheel

# Fix numpy/pillow compatibility (good you already had this)
RUN pip install numpy==1.26.4
RUN pip install pillow==10.2.0

RUN pip install --no-cache-dir -r requirements.txt -vvv

# ---------------------------
# PREPARE TTS CACHE (🔥 VERY IMPORTANT)
# ---------------------------
RUN mkdir -p /root/.local/share/tts

# ---------------------------
# COPY PROJECT FILES
# ---------------------------
COPY . .

# ---------------------------
# FIX PERMISSIONS (🔥 IMPORTANT)
# ---------------------------
RUN chmod -R 777 /tmp

# ---------------------------
# ENV
# ---------------------------
ENV PYTHONPATH=/app

# ---------------------------
# DEFAULT CMD
# ---------------------------
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]