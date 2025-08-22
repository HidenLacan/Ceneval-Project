from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from core.models import ColoniaProcesada
import os
import shutil

class Command(BaseCommand):
    help = 'Force collect media files and copy existing images to static directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force copy even if files exist',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Force collecting media files...")

        # Get directories
        static_media_dir = settings.STATIC_ROOT / 'media'
        local_media_dir = settings.BASE_DIR / 'static' / 'media'
        old_media_dir = settings.MEDIA_ROOT

        # Create directories if they don't exist
        os.makedirs(static_media_dir, exist_ok=True)
        os.makedirs(local_media_dir, exist_ok=True)

        self.stdout.write(f"📁 Static media dir: {static_media_dir}")
        self.stdout.write(f"📁 Local media dir: {local_media_dir}")
        self.stdout.write(f"📁 Old media dir: {old_media_dir}")

        # Copy existing images from old media directory to static/media
        if old_media_dir.exists():
            self.stdout.write("📋 Copying existing images from old media directory...")
            
            for root, dirs, files in os.walk(old_media_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # Get relative path
                        rel_path = os.path.relpath(root, old_media_dir)
                        src_file = os.path.join(root, file)
                        dst_file = static_media_dir / rel_path / file
                        
                        # Create destination directory
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        
                        # Copy file
                        try:
                            shutil.copy2(src_file, dst_file)
                            self.stdout.write(f"  ✅ Copied: {rel_path}/{file}")
                        except Exception as e:
                            self.stdout.write(f"  ❌ Error copying {rel_path}/{file}: {str(e)}")

        # Copy from local static/media to staticfiles/media
        if local_media_dir.exists():
            self.stdout.write("📋 Copying from local static/media to staticfiles/media...")
            
            for root, dirs, files in os.walk(local_media_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        # Get relative path
                        rel_path = os.path.relpath(root, local_media_dir)
                        src_file = os.path.join(root, file)
                        dst_file = static_media_dir / rel_path / file
                        
                        # Create destination directory
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        
                        # Copy file
                        try:
                            shutil.copy2(src_file, dst_file)
                            self.stdout.write(f"  ✅ Copied: {rel_path}/{file}")
                        except Exception as e:
                            self.stdout.write(f"  ❌ Error copying {rel_path}/{file}: {str(e)}")

        # Run collectstatic
        self.stdout.write("🔄 Running collectstatic...")
        try:
            call_command('collectstatic',
                        interactive=False,
                        verbosity=1,
                        clear=options['force'])
            self.stdout.write(self.style.SUCCESS("✅ Collectstatic completed successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error in collectstatic: {str(e)}"))

        # Verify results
        self.stdout.write("🔍 Verifying results...")
        if static_media_dir.exists():
            static_files = list(static_media_dir.rglob('*'))
            image_files = [f for f in static_files if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']]
            self.stdout.write(f"📁 Total image files in static: {len(image_files)}")
            
            for img_file in image_files[:5]:
                rel_path = img_file.relative_to(static_media_dir)
                self.stdout.write(f"  📄 {rel_path}")
            
            if len(image_files) > 5:
                self.stdout.write(f"  ... and {len(image_files) - 5} more files")

        self.stdout.write("✅ Force collect media completed!")
