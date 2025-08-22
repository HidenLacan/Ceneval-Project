from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import ColoniaProcesada
import os
import requests

class Command(BaseCommand):
    help = 'Diagnose image loading issues in production'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Diagnosing image loading issues...")
        
        # Check environment
        self.stdout.write(f"🌍 Environment: {'Production' if not settings.DEBUG else 'Development'}")
        self.stdout.write(f"📁 BASE_DIR: {settings.BASE_DIR}")
        self.stdout.write(f"📁 STATIC_ROOT: {settings.STATIC_ROOT}")
        self.stdout.write(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")
        
        # Check static directories
        static_media_dir = settings.STATIC_ROOT / 'media'
        local_media_dir = settings.BASE_DIR / 'static' / 'media'
        
        self.stdout.write(f"\n📁 Directory Status:")
        self.stdout.write(f"  Static media dir exists: {static_media_dir.exists()}")
        self.stdout.write(f"  Local media dir exists: {local_media_dir.exists()}")
        
        # Check colonias with images
        colonias_con_imagen = ColoniaProcesada.objects.filter(imagen__isnull=False)
        self.stdout.write(f"\n🏘️ Colonias con imágenes: {colonias_con_imagen.count()}")
        
        for colonia in colonias_con_imagen:
            self.stdout.write(f"\n  🏘️ {colonia.nombre}:")
            self.stdout.write(f"    📄 Image name: {colonia.imagen.name}")
            self.stdout.write(f"    📄 Image path: {colonia.imagen.path}")
            self.stdout.write(f"    📄 Image URL: {colonia.imagen.url}")
            
            # Check if file exists at path
            if os.path.exists(colonia.imagen.path):
                file_size = os.path.getsize(colonia.imagen.path)
                self.stdout.write(f"    ✅ File exists at path ({file_size} bytes)")
            else:
                self.stdout.write(f"    ❌ File missing at path!")
            
            # Check if file exists in static
            static_path = static_media_dir / colonia.imagen.name
            if static_path.exists():
                static_size = os.path.getsize(static_path)
                self.stdout.write(f"    ✅ File exists in static ({static_size} bytes)")
            else:
                self.stdout.write(f"    ❌ File missing in static!")
            
            # Try to access via URL (if in production)
            if not settings.DEBUG:
                try:
                    # Get the full URL
                    from django.contrib.sites.models import Site
                    domain = Site.objects.get_current().domain if Site.objects.count() > 0 else 'ceneval-project.onrender.com'
                    full_url = f"https://{domain}{colonia.imagen.url}"
                    
                    response = requests.head(full_url, timeout=5)
                    if response.status_code == 200:
                        self.stdout.write(f"    ✅ URL accessible: {full_url}")
                    else:
                        self.stdout.write(f"    ❌ URL not accessible: {full_url} (Status: {response.status_code})")
                except Exception as e:
                    self.stdout.write(f"    ⚠️ Could not test URL: {str(e)}")
        
        # Check static files collection
        self.stdout.write(f"\n📁 Static files in {static_media_dir}:")
        if static_media_dir.exists():
            static_files = list(static_media_dir.rglob('*'))
            self.stdout.write(f"  Total files: {len(static_files)}")
            
            # Group by directory
            dir_counts = {}
            for file in static_files:
                if file.is_file():
                    rel_path = file.relative_to(static_media_dir)
                    parent_dir = rel_path.parent
                    dir_counts[parent_dir] = dir_counts.get(parent_dir, 0) + 1
            
            for directory, count in dir_counts.items():
                self.stdout.write(f"  📂 {directory}: {count} files")
        else:
            self.stdout.write(f"  ❌ Static media directory does not exist!")
        
        self.stdout.write("\n✅ Diagnosis completed!")
