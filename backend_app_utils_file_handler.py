import os
import shutil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"

async def save_upload_file(upload_file, user_id: int) -> str:
    """
    Save an uploaded file to the upload directory.
    
    Args:
        upload_file: The uploaded file
        user_id: ID of the user uploading the file
        
    Returns:
        Path to the saved file
    """
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Create user-specific directory
        user_dir = os.path.join(UPLOAD_DIR, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{upload_file.filename}"
        file_path = os.path.join(user_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"File saved to {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise

def delete_file(file_path: str) -> bool:
    """
    Delete a file from the filesystem.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if the file was deleted successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return False