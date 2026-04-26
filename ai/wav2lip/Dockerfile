FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DEFAULT_TIMEOUT=1000

RUN apt-get update && apt-get install -y \
    build-essential gcc ffmpeg git wget libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone Wav2Lip
RUN git clone https://github.com/Rudrabha/Wav2Lip.git /app/Wav2Lip

WORKDIR /app/Wav2Lip

# Install requirements
RUN pip install --upgrade pip setuptools wheel
# Install PyTorch components separately to prevent OOM on constrained deployment servers
RUN pip install torch==2.0.1+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install torchvision==0.15.2+cpu --index-url https://download.pytorch.org/whl/cpu

# Install the rest of the requirements
RUN pip install --no-cache-dir \
    "numpy<1.24" \
    scipy \
    librosa \
    opencv-python \
    tqdm \
    numba

# Download Face Detection model
RUN wget -q "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" -O face_detection/detection/sfd/s3fd.pth

# Download Wav2Lip GAN model
RUN mkdir -p checkpoints && \
    wget -q "https://huggingface.co/camenduru/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth" -O checkpoints/wav2lip_gan.pth

# Script to keep container alive
CMD ["tail", "-f", "/dev/null"]
