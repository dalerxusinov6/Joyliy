#!/usr/bin/env bash
# Production build script for Joyliy deployment
set -o errexit

echo "==> Upgrading pip..."
pip install --upgrade pip

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Applying database migrations..."
python -m alembic upgrade head || true

echo "==> Build complete!"

