from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import ColoniaProcesada
from core.storage import StaticMediaStorage
import os
import tempfile

class Command(BaseCommand):
    help = 'Debug the save process to understand why images are not being saved'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Debugging save process...")
        
        # Check storage configuration
        self.stdout.write("\n📁 Storage Configuration:")
        storage = StaticMediaStorage()
        self.stdout.write(f"  Storage location: {storage.location}")
        self.stdout.write(f"  Storage base_url: {storage.base_url}")
        self.stdout.write(f"  Location exists: {os.path.exists(storage.location)}")
        
        # Check if location is writable
        try:
            test_file = os.path.join(storage.location, 'test_write.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            self.stdout.write("  ✅ Location is writable")
        except Exception as e:
            self.stdout.write(f"  ❌ Location is not writable: {str(e)}")
        
        # Check existing colonias
        self.stdout.write("\n🏘️ Existing Colonias:")
        colonias = ColoniaProcesada.objects.all()
        self.stdout.write(f"  Total colonias: {colonias.count()}")
        
        for colonia in colonias:
            self.stdout.write(f"\n  🏘️ {colonia.nombre}:")
            self.stdout.write(f"    Has image: {bool(colonia.imagen)}")
            if colonia.imagen:
                self.stdout.write(f"    Image name: {colonia.imagen.name}")
                self.stdout.write(f"    Image path: {colonia.imagen.path}")
                self.stdout.write(f"    Image URL: {colonia.imagen.url}")
                
                # Check if file exists
                if os.path.exists(colonia.imagen.path):
                    file_size = os.path.getsize(colonia.imagen.path)
                    self.stdout.write(f"    ✅ File exists ({file_size} bytes)")
                else:
                    self.stdout.write(f"    ❌ File missing!")
                
                # Check if file exists in static
                static_path = settings.STATIC_ROOT / 'media' / colonia.imagen.name
                if static_path.exists():
                    static_size = os.path.getsize(static_path)
                    self.stdout.write(f"    ✅ In static ({static_size} bytes)")
                else:
                    self.stdout.write(f"    ❌ Not in static!")
        
        # Test file upload simulation
        self.stdout.write("\n🧪 Testing file upload simulation:")
        try:
            # Create a test file
            test_content = b'fake image content'
            test_name = 'test_image.png'
            
            # Test saving with storage
            saved_name = storage.save(test_name, tempfile.NamedTemporaryFile())
            self.stdout.write(f"  ✅ Test save successful: {saved_name}")
            
            # Check if file was created
            full_path = os.path.join(storage.location, saved_name)
            if os.path.exists(full_path):
                self.stdout.write(f"  ✅ Test file created: {full_path}")
                os.remove(full_path)  # Clean up
            else:
                self.stdout.write(f"  ❌ Test file not created!")
                
        except Exception as e:
            self.stdout.write(f"  ❌ Test save failed: {str(e)}")
        
        # Check directory permissions
        self.stdout.write("\n🔐 Directory Permissions:")
        static_media_dir = settings.BASE_DIR / 'static' / 'media'
        staticfiles_media_dir = settings.STATIC_ROOT / 'media'
        
        for dir_path, dir_name in [(static_media_dir, 'static/media'), (staticfiles_media_dir, 'staticfiles/media')]:
            self.stdout.write(f"\n  📁 {dir_name}:")
            self.stdout.write(f"    Exists: {dir_path.exists()}")
            if dir_path.exists():
                self.stdout.write(f"    Writable: {os.access(dir_path, os.W_OK)}")
                self.stdout.write(f"    Readable: {os.access(dir_path, os.R_OK)}")
                self.stdout.write(f"    Executable: {os.access(dir_path, os.X_OK)}")
        
        self.stdout.write("\n✅ Debug completed!")
