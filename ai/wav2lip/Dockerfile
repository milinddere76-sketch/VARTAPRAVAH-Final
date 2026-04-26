FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_NO_CACHE_DIR=1

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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
RUN pip install numpy==1.26.4
RUN pip install pillow==10.2.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -vvv
COPY render.py .

CMD ["python", "render.py"]
