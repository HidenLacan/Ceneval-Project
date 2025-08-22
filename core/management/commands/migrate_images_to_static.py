from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import ColoniaProcesada
import os
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Migrate existing images from media to static/media directory'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Migrating images to static/media...")
        
        # Source: old media directory
        old_media_root = settings.BASE_DIR / 'media'
        # Destination: static/media directory
        static_media_dir = settings.BASE_DIR / 'static' / 'media'
        
        if not old_media_root.exists():
            self.stdout.write("❌ Old media directory does not exist")
            return
        
        # Create static/media directory
        static_media_dir.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write(f"📁 Migrating from: {old_media_root}")
        self.stdout.write(f"📁 Migrating to: {static_media_dir}")
        
        # Copy all files and directories
        for root, dirs, files in os.walk(old_media_root):
            # Create corresponding directories in static/media
            rel_path = os.path.relpath(root, old_media_root)
            static_dir = static_media_dir / rel_path
            static_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = static_dir / file
                shutil.copy2(src_file, dst_file)
                self.stdout.write(f"  📄 Migrated: {rel_path}/{file}")
        
        self.stdout.write("✅ Images migrated successfully!")
        self.stdout.write("💡 Now run: python manage.py collectstatic --noinput")
