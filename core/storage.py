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
        # Always save to static/media for consistency
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
            
            logger.info(f"File saved successfully: {saved_name}")
            return saved_name
            
        except Exception as e:
            logger.error(f"Error saving file {name}: {str(e)}")
            raise
