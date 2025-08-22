#!/bin/bash
# Build script for Render.com deployment

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p static/media
mkdir -p staticfiles/media

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files (this will include media files from static/media)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build completed successfully!"
