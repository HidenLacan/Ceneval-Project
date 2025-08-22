from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import ColoniaProcesada
import os

class Command(BaseCommand):
    help = 'Check media files status in production'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking media files status...")

        # Verificar directorios
        static_media_dir = settings.STATIC_ROOT / 'media'
        local_media_dir = settings.BASE_DIR / 'static' / 'media'

        self.stdout.write(f"📁 Static media directory: {static_media_dir}")
        self.stdout.write(f"📁 Local media directory: {local_media_dir}")

        # Verificar colonias con imágenes
        colonias_con_imagen = ColoniaProcesada.objects.filter(imagen__isnull=False)
        self.stdout.write(f"\n🏘️ Colonias con imágenes: {colonias_con_imagen.count()}")

        for colonia in colonias_con_imagen:
            self.stdout.write(f"\n  🏘️ {colonia.nombre}:")
            self.stdout.write(f"    📄 Image path: {colonia.imagen.path}")
            self.stdout.write(f"    📄 Image URL: {colonia.imagen.url}")

            # Verificar si el archivo existe
            if os.path.exists(colonia.imagen.path):
                file_size = os.path.getsize(colonia.imagen.path)
                self.stdout.write(f"    ✅ File exists ({file_size} bytes)")
            else:
                self.stdout.write(f"    ❌ File missing!")

            # Verificar si está en static
            static_path = static_media_dir / colonia.imagen.name
            if static_path.exists():
                self.stdout.write(f"    ✅ In static directory")
            else:
                self.stdout.write(f"    ⚠️ Not in static directory")

        # Verificar archivos en static/media
        if static_media_dir.exists():
            static_files = list(static_media_dir.rglob('*'))
            self.stdout.write(f"\n📁 Files in static/media: {len(static_files)}")
            for file in static_files[:10]:
                if file.is_file():
                    self.stdout.write(f"  📄 {file.relative_to(static_media_dir)}")
            if len(static_files) > 10:
                self.stdout.write(f"  ... and {len(static_files) - 10} more files")
        else:
            self.stdout.write(f"\n❌ Static media directory does not exist!")

        self.stdout.write("\n✅ Media status check completed!")
