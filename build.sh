#!/bin/bash
# Build script for Render.com deployment

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create static/media directory
echo "📁 Creating static/media directory..."
mkdir -p static/media

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files (initial)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run our custom collectstatic command to ensure media files are included
echo "🔄 Running custom collectstatic for media files..."
python manage.py collect_media_static

echo "✅ Build completed successfully!"
