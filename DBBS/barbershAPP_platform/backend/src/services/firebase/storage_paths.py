from firebase_admin import storage # type: ignore
from datetime import datetime
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FirebaseStorageService:
    _instance = None
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    def __init__(self):
        self.bucket = storage.bucket()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _get_file_path(self, folder: str, user_id: str, file_name: str) -> str:
        """Generate storage path for file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{folder}/{user_id}/{timestamp}_{file_name}"
    
    def upload_image(self, 
                    folder: str,
                    user_id: str, 
                    file_data: bytes, 
                    content_type: str,
                    original_filename: str) -> Optional[str]:
        """Upload image to Firebase Storage"""
        try:
            file_path = self._get_file_path(folder, user_id, original_filename)
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(
                file_data,
                content_type=content_type
            )
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload image: {str(e)}")
            return None