FROM python:3.12-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directories
RUN mkdir -p /tmp/autouploader/clips

EXPOSE 8000

# Shell form: /bin/sh expands $PORT at runtime (Railway injects it)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
