"""
File Service

Handles file upload, processing, and management.
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path

import structlog
from fastapi import UploadFile
from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import FileProcessingError

logger = structlog.get_logger(__name__)
settings = get_settings()


class FileService:
    """Service for handling file operations."""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "images").mkdir(exist_ok=True)
        (self.upload_dir / "documents").mkdir(exist_ok=True)
        (self.upload_dir / "temp").mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize the file service."""
        logger.info("FileService initialized successfully")
    
    async def upload_file(
        self, 
        file: UploadFile, 
        user_id: int,
        max_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Upload and process a file."""
        
        try:
            # Validate file size
            max_size = max_size or settings.MAX_FILE_SIZE
            if file.size and file.size > max_size:
                raise FileProcessingError(
                    f"File too large. Maximum size: {max_size} bytes",
                    filename=file.filename
                )
            
            # Validate file type
            if not self._is_allowed_file_type(file.content_type):
                raise FileProcessingError(
                    f"File type not allowed: {file.content_type}",
                    filename=file.filename
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower()
            filename = f"{file_id}{file_extension}"
            
            # Determine subdirectory based on file type
            if file.content_type.startswith('image/'):
                subdir = "images"
            else:
                subdir = "documents"
            
            file_path = self.upload_dir / subdir / filename
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Process file based on type
            file_info = {
                "id": file_id,
                "filename": file.filename,
                "original_filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": file.content_type,
                "user_id": user_id,
                "url": f"/api/v1/files/{file_id}"
            }
            
            # Additional processing for images
            if file.content_type.startswith('image/'):
                image_info = await self._process_image(file_path)
                file_info.update(image_info)
            
            logger.info(
                "File uploaded successfully",
                file_id=file_id,
                filename=file.filename,
                size=len(content),
                user_id=user_id
            )
            
            return file_info
            
        except Exception as e:
            logger.error(
                "File upload failed",
                filename=file.filename,
                error=str(e)
            )
            raise FileProcessingError(
                f"Failed to upload file: {str(e)}",
                filename=file.filename
            )
    
    async def get_file(self, file_id: str) -> Optional[Path]:
        """Get file path by ID."""
        
        # Search in subdirectories
        for subdir in ["images", "documents", "temp"]:
            subdir_path = self.upload_dir / subdir
            for file_path in subdir_path.glob(f"{file_id}.*"):
                if file_path.is_file():
                    return file_path
        
        return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file by ID."""
        
        try:
            file_path = await self.get_file(file_id)
            if file_path and file_path.exists():
                file_path.unlink()
                logger.info("File deleted", file_id=file_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error("File deletion failed", file_id=file_id, error=str(e))
            return False
    
    async def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """Process uploaded image and extract metadata."""
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode
                
                # Generate thumbnail
                thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, format=format_name)
                
                return {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "mode": mode,
                    "thumbnail_url": f"/api/v1/files/thumb_{file_path.stem}"
                }
                
        except Exception as e:
            logger.warning("Image processing failed", file_path=str(file_path), error=str(e))
            return {}
    
    def _is_allowed_file_type(self, content_type: str) -> bool:
        """Check if file type is allowed."""
        
        allowed_types = settings.ALLOWED_FILE_TYPES
        return content_type in allowed_types
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than specified age."""
        
        import time
        
        temp_dir = self.upload_dir / "temp"
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        try:
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error("Temp file cleanup failed", error=str(e))
            return 0
    
    async def get_file_stats(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        
        try:
            stats = {
                "total_files": 0,
                "total_size": 0,
                "by_type": {}
            }
            
            for subdir in ["images", "documents", "temp"]:
                subdir_path = self.upload_dir / subdir
                subdir_stats = {
                    "count": 0,
                    "size": 0
                }
                
                for file_path in subdir_path.glob("*"):
                    if file_path.is_file():
                        file_size = file_path.stat().st_size
                        subdir_stats["count"] += 1
                        subdir_stats["size"] += file_size
                
                stats["by_type"][subdir] = subdir_stats
                stats["total_files"] += subdir_stats["count"]
                stats["total_size"] += subdir_stats["size"]
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get file stats", error=str(e))
            return {"error": str(e)}
