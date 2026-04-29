FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install ONLY runtime system dependencies (FFmpeg is needed for branding)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    curl \
    ca-certificates \
    libgl1 \
    libglib2.0-0 \
    libpq-dev \
    fonts-noto-ui-core \
    && rm -rf /var/lib/apt/lists/*

# Install ONLY the core requirements (No Torch, No TTS)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Internal fallback assets
RUN mkdir -p /app/assets_internal && cp -r /app/assets/* /app/assets_internal/ || true

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
