# Pixelle-Video Docker Image
# Based on Python 3.11 slim for smaller image size

FROM python:3.11-slim

# Build arguments for mirror configuration
# USE_CN_MIRROR: whether to use China mirrors (true/false)
# UV_INDEX_URL: Python package index URL (defaults to Aliyun when USE_CN_MIRROR=true)
ARG USE_CN_MIRROR=false
ARG UV_INDEX_URL=https://pypi.org/simple

# Set working directory
WORKDIR /app

# Replace apt sources with China mirrors if needed
# Debian 12 uses DEB822 format in /etc/apt/sources.list.d/debian.sources
RUN if [ "$USE_CN_MIRROR" = "true" ]; then \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; \
    fi

# Install system dependencies
# - curl: for health checks and downloads
# - ffmpeg: for video/audio processing
# - chromium: for html2image rendering
# - fonts-noto-cjk: for CJK character support
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    chromium \
    chromium-driver \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv --version
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files and source code for building
# Note: pixelle_video is needed for hatchling to build the package
COPY pyproject.toml uv.lock README.md ./
COPY pixelle_video ./pixelle_video

# Install Python dependencies using uv with configurable index URL
# Auto-select Aliyun mirror when USE_CN_MIRROR=true and UV_INDEX_URL is default
RUN if [ "$USE_CN_MIRROR" = "true" ] && [ "$UV_INDEX_URL" = "https://pypi.org/simple" ]; then \
        /root/.local/bin/uv sync --frozen --no-dev --index-url https://mirrors.aliyun.com/pypi/simple/; \
    else \
        /root/.local/bin/uv sync --frozen --no-dev --index-url $UV_INDEX_URL; \
    fi

# Copy rest of application code
COPY api ./api
COPY web ./web
COPY bgm ./bgm
COPY templates ./templates
COPY workflows ./workflows
COPY resources ./resources

# Create output and data directories
RUN mkdir -p /app/output /app/data

# Set environment variables for html2image to use chromium
ENV BROWSER_EXECUTABLE_PATH=/usr/bin/chromium
ENV CHROME_BIN=/usr/bin/chromium

# Expose ports
# 8000: API service
# 8501: Web UI service
EXPOSE 8000 8501

# Default command (can be overridden in docker-compose)
CMD ["/root/.local/bin/uv", "run", "python", "api/app.py"]

