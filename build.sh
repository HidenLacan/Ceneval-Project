#!/bin/bash
# Build script for Render.com deployment

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p static/media
mkdir -p staticfiles/media

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files (initial)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run our custom collectstatic command to ensure media files are included
echo "🔄 Running custom collectstatic for media files..."
python manage.py collect_media_static

# Force collect and copy existing media files
echo "🔄 Force collecting and copying media files..."
python manage.py force_collect_media --force

# Verify the setup
echo "🔍 Verifying media setup..."
python manage.py check_production_status

echo "✅ Build completed successfully!"
