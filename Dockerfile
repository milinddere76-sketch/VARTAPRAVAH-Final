# This Dockerfile is at the root to improve compatibility with CI/CD tools like Coolify
# It builds the Varta Pravah backend/dashboard service.

FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

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
    fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from the backend folder
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install numpy==1.26.4
RUN pip install pillow==10.2.0

RUN pip install --no-cache-dir -r requirements.txt -vvv

# Copy the entire project context
COPY . .

ENV PYTHONPATH=/app

# Default to running the backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
