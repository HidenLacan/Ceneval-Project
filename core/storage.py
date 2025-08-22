from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

class StaticMediaStorage(FileSystemStorage):
    """
    Custom storage that saves uploaded files to static/media directory.
    This ensures files are included in static files collection and work in production.
    """
    
    def __init__(self, location=None, base_url=None):
        # Set location to static/media
        if location is None:
            location = os.path.join(settings.BASE_DIR, 'static', 'media')
        
        # Set base_url to /static/media/
        if base_url is None:
            base_url = '/static/media/'
        
        # Ensure the base directory exists
        os.makedirs(location, exist_ok=True)
        
        super().__init__(location=location, base_url=base_url)
    
    def get_available_name(self, name, max_length=None):
        """Ensure the directory exists before saving"""
        # Create the directory structure if it doesn't exist
        dir_path = os.path.dirname(os.path.join(self.location, name))
        os.makedirs(dir_path, exist_ok=True)
        
        return super().get_available_name(name, max_length)
    
    def save(self, name, content, max_length=None):
        """Override save to ensure directory exists and log any errors"""
        try:
            # Ensure the directory exists
            dir_path = os.path.dirname(os.path.join(self.location, name))
            os.makedirs(dir_path, exist_ok=True)
            
            # Save the file
            saved_name = super().save(name, content, max_length)
            
            # Also save to staticfiles/media for production
            staticfiles_path = os.path.join(settings.STATIC_ROOT, 'media', saved_name)
            staticfiles_dir = os.path.dirname(staticfiles_path)
            os.makedirs(staticfiles_dir, exist_ok=True)
            
            # Copy the file to staticfiles
            import shutil
            original_path = os.path.join(self.location, saved_name)
            if os.path.exists(original_path):
                shutil.copy2(original_path, staticfiles_path)
                logger.info(f"✅ File also copied to staticfiles: {staticfiles_path}")
            
            logger.info(f"✅ File saved successfully: {saved_name}")
            return saved_name
            
        except Exception as e:
            logger.error(f"❌ Error saving file {name}: {str(e)}")
            raise
