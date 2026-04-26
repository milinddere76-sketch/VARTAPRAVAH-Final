FROM tiangolo/nginx-rtmp:latest

# Install FFmpeg and Curl for the relay logic
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files from the streaming/ directory (context is root)
COPY streaming/stream.sh /app/stream.sh
COPY assets /app/assets
RUN chmod +x /app/stream.sh

# Copy Nginx config
COPY streaming/nginx/nginx.conf /etc/nginx/nginx.conf.template

# Create a startup script
RUN echo '#!/bin/sh\n\
envsubst "\$YOUTUBE_STREAM_KEY" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf\n\
nginx -g "daemon on;"\n\
/app/stream.sh' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV YOUTUBE_RTMP_URL="rtmp://localhost/live/stream"

ENTRYPOINT ["/app/entrypoint.sh"]
