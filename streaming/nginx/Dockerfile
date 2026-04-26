FROM tiangolo/nginx-rtmp:latest

# Install FFmpeg and Curl for the relay logic
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the stream script and assets
COPY stream.sh /app/stream.sh
COPY assets /app/assets
RUN chmod +x /app/stream.sh

# Copy Nginx config
COPY nginx.conf /etc/nginx/nginx.conf.template

# Create a startup script to handle Env Var substitution in nginx.conf
RUN echo '#!/bin/sh\n\
envsubst "\$YOUTUBE_STREAM_KEY" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf\n\
nginx -g "daemon on;"\n\
/app/stream.sh' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# We push to the local Nginx ingest
ENV YOUTUBE_RTMP_URL="rtmp://localhost/live/stream"

ENTRYPOINT ["/app/entrypoint.sh"]
