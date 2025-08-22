from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
import subprocess
import sys

class Command(BaseCommand):
    help = 'Collect static files including newly uploaded media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force collectstatic even if files are up to date',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Collecting static files including media...")

        try:
            call_command('collectstatic',
                        interactive=False,
                        verbosity=1,
                        clear=options['force'])

            self.stdout.write(
                self.style.SUCCESS("✅ Static files collected successfully!")
            )

            static_media_dir = settings.STATIC_ROOT / 'media'
            if static_media_dir.exists():
                media_files = list(static_media_dir.rglob('*'))
                self.stdout.write(f"📁 Found {len(media_files)} files in {static_media_dir}")

                for file in media_files[:5]:
                    if file.is_file():
                        self.stdout.write(f"  📄 {file.relative_to(static_media_dir)}")

                if len(media_files) > 5:
                    self.stdout.write(f"  ... and {len(media_files) - 5} more files")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error collecting static files: {str(e)}")
            )
            sys.exit(1)
