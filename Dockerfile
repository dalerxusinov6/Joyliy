# Production Dockerfile for Uyda Telegram Bot & Monitor
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8000 \
    RENDER=true \
    WEBSITE_URL=https://joyliy.uz \
    BOT_MODE=auto

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure upload directory and permissions
RUN mkdir -p /app/uploads && \
    useradd -u 1000 -m appuser || true && \
    chown -R appuser:appuser /app && \
    chmod -R 777 /app
USER appuser

# Expose API port
EXPOSE 8000 10000

# Default entrypoint
CMD ["python", "-m", "src.main", "--mode", "all"]

