from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

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
        
        super().__init__(location=location, base_url=base_url)
    
    def get_available_name(self, name, max_length=None):
        """Ensure the directory exists before saving"""
        # Create the directory structure if it doesn't exist
        dir_path = os.path.dirname(os.path.join(self.location, name))
        os.makedirs(dir_path, exist_ok=True)
        
        return super().get_available_name(name, max_length)
