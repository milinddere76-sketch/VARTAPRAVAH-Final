# --- STAGE 1: BUILDER ---
FROM python:3.10-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --user --no-cache-dir -r requirements.txt

# --- STAGE 2: RUNTIME ---
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install ONLY runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libpq5 \
    curl \
    ca-certificates \
    fonts-noto-ui-core \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI manually (Static Binary for maximum reliability)
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz | tar -xzC /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    chmod +x /usr/local/bin/docker && \
    rm -rf /tmp/docker

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy the project files
COPY . .

# Internal fallback assets to ensure it works even if volume is empty
RUN mkdir -p /app/assets_internal && cp -r /app/assets/* /app/assets_internal/ || true

# Default to running the backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
