FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=1000

WORKDIR /app

# Combine ALL installation steps into a single layer to save disk space
RUN apt-get update && apt-get install -y \
    build-essential gcc ffmpeg git curl libgl1 libglib2.0-0 \
    && git clone https://github.com/Rudrabha/Wav2Lip.git /app/Wav2Lip \
    && cd /app/Wav2Lip \
    && mkdir -p temp checkpoints face_detection/detection/sfd \
    && pip install --upgrade pip wheel "setuptools<70.0.0" \
    && pip uninstall -y librosa numba numpy \
    && if [ "$(uname -m)" = "x86_64" ]; then \
        pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu; \
    else \
        pip install torch==2.1.0 torchvision==0.16.0; \
    fi \
    && pip install \
        numpy==1.23.5 \
        scipy==1.10.1 \
        librosa==0.9.2 \
        opencv-python==4.8.0.76 \
        tqdm \
        numba==0.56.4 \
    && curl -L "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" -o face_detection/detection/sfd/s3fd.pth \
    && curl -L "https://huggingface.co/camenduru/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth" -o checkpoints/wav2lip_gan.pth \
    && apt-get purge -y --auto-remove build-essential gcc git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/Wav2Lip

# Copy only necessary assets
COPY assets/ /app/assets/

CMD ["tail", "-f", "/dev/null"]
