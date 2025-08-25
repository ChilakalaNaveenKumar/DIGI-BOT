"""
OpenAI File Storage Manager
Uploads files to OpenAI's cloud storage with consistent naming
"""
import os
import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger(__name__)

class OpenAIFileStorageManager:
    """Manages documents by uploading to OpenAI's file storage"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Document paths
        self.documents_folder = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/component_matcher/documents"
        
        # File mapping with consistent names
        self.file_mapping = {
            "chartjs_markdown_format_v1.md": "digi_setu_charts_v3.md",
            "data_table_markdown_format_v1.md": "digi_setu_tables_v3.md", 
            "Examples.md": "digi_setu_examples.md",
            "PositionAnchors.md": "digi_setu_positions.md"
        }
        
        # Store uploaded file metadata
        self.metadata_file = os.path.join(self.documents_folder, "openai_files_metadata.json")
        self.uploaded_files = {}
        self._initialized = False
    
    def _load_metadata(self):
        """Load existing file metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.uploaded_files = json.load(f)
                logger.info("Loaded file metadata", count=len(self.uploaded_files))
            except Exception as e:
                logger.error("Failed to load metadata", error=str(e))
                self.uploaded_files = {}
        else:
            self.uploaded_files = {}
    
    def _save_metadata(self):
        """Save file metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.uploaded_files, f, indent=2)
            logger.info("Saved file metadata", count=len(self.uploaded_files))
        except Exception as e:
            logger.error("Failed to save metadata", error=str(e))
    
    async def _upload_file(self, local_path: str, consistent_name: str) -> Optional[str]:
        """Upload a file to OpenAI storage"""
        try:
            # Create a temporary file with the consistent name
            import tempfile
            import shutil
            
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.md', delete=False) as temp_file:
                # Copy content to temp file
                with open(local_path, 'rb') as source:
                    shutil.copyfileobj(source, temp_file)
                temp_file.flush()
                
                # Upload with consistent filename
                with open(temp_file.name, 'rb') as f:
                    file_obj = await self.client.files.create(
                        file=(consistent_name, f, 'text/markdown'),  # Specify filename
                        purpose="assistants"
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            logger.info("Uploaded file to OpenAI", 
                       filename=consistent_name,
                       file_id=file_obj.id,
                       size=file_obj.bytes)
            
            return file_obj.id
            
        except Exception as e:
            logger.error("Failed to upload file", 
                        filename=consistent_name, 
                        error=str(e))
            return None
    
    async def _list_openai_files(self) -> List[Dict[str, Any]]:
        """List files in OpenAI storage"""
        try:
            files = await self.client.files.list(purpose="assistants")
            
            # Filter for our files based on naming convention
            our_files = []
            for file in files.data:
                if file.filename and file.filename.startswith("digi_setu_"):
                    our_files.append({
                        "id": file.id,
                        "filename": file.filename,
                        "bytes": file.bytes,
                        "created_at": file.created_at,
                        "status": file.status
                    })
            
            return our_files
            
        except Exception as e:
            logger.error("Failed to list OpenAI files", error=str(e))
            return []
    
    async def initialize(self):
        """Initialize file storage and upload documents"""
        if self._initialized:
            return len(self.uploaded_files)
        
        try:
            # Load existing metadata
            self._load_metadata()
            
            # Get files already in OpenAI storage
            openai_files = await self._list_openai_files()
            openai_filenames = {f["filename"] for f in openai_files}
            
            logger.info("Found existing OpenAI files", count=len(openai_files))
            for f in openai_files:
                logger.info("Existing file", filename=f["filename"], file_id=f["id"])
            
            # Process each local document
            uploaded_count = 0
            for local_filename in os.listdir(self.documents_folder):
                if not local_filename.endswith('.md'):
                    continue
                
                consistent_name = self.file_mapping.get(local_filename, local_filename)
                local_path = os.path.join(self.documents_folder, local_filename)
                
                # Check if already uploaded
                if consistent_name in openai_filenames:
                    logger.info("File already exists in OpenAI storage", filename=consistent_name)
                    # Update metadata with existing file info
                    existing_file = next(f for f in openai_files if f["filename"] == consistent_name)
                    self.uploaded_files[consistent_name] = {
                        "file_id": existing_file["id"],
                        "original_filename": local_filename,
                        "bytes": existing_file["bytes"],
                        "status": "uploaded"
                    }
                    continue
                
                # Upload new file
                logger.info("Uploading new file", filename=consistent_name)
                file_id = await self._upload_file(local_path, consistent_name)
                
                if file_id:
                    # Get file size
                    file_size = os.path.getsize(local_path)
                    
                    # Store metadata
                    self.uploaded_files[consistent_name] = {
                        "file_id": file_id,
                        "original_filename": local_filename,
                        "bytes": file_size,
                        "status": "uploaded"
                    }
                    uploaded_count += 1
                    
                    logger.info("Successfully uploaded", 
                               filename=consistent_name,
                               file_id=file_id,
                               size=file_size)
                else:
                    logger.error("Failed to upload", filename=consistent_name)
            
            # Save updated metadata
            if uploaded_count > 0:
                self._save_metadata()
            
            self._initialized = True
            logger.info("File storage initialization complete", 
                       total_files=len(self.uploaded_files),
                       new_uploads=uploaded_count)
            
            return len(self.uploaded_files)
            
        except Exception as e:
            logger.error("Failed to initialize file storage", error=str(e))
            raise
    
    async def query(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query files (placeholder - would need vector search implementation)"""
        if not self._initialized:
            await self.initialize()
        
        # For now, return file metadata as placeholder
        # In a real implementation, you'd use embeddings or assistant API
        results = []
        for filename, metadata in self.uploaded_files.items():
            results.append({
                "text": f"File: {filename}",
                "score": 0.8,  # Placeholder score
                "meta": {
                    "filename": filename,
                    "file_id": metadata["file_id"],
                    "original_filename": metadata["original_filename"],
                    "bytes": metadata["bytes"]
                }
            })
        
        return results[:top_k]
    
    async def clear_all_docs(self):
        """Delete all uploaded files from OpenAI storage"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Delete each file from OpenAI
            for filename, metadata in self.uploaded_files.items():
                try:
                    await self.client.files.delete(file_id=metadata["file_id"])
                    logger.info("Deleted file from OpenAI", filename=filename, file_id=metadata["file_id"])
                except Exception as e:
                    logger.error("Failed to delete file", filename=filename, error=str(e))
            
            # Clear local metadata
            self.uploaded_files = {}
            self._save_metadata()
            
            logger.info("Cleared all files from OpenAI storage")
            
        except Exception as e:
            logger.error("Failed to clear files", error=str(e))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get file storage statistics"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Get current OpenAI files
            openai_files = await self._list_openai_files()
            
            total_bytes = sum(f["bytes"] for f in openai_files)
            
            return {
                "storage_type": "openai_files",
                "file_count": len(openai_files),
                "files": [f["filename"] for f in openai_files],
                "file_details": openai_files,
                "total_bytes": total_bytes,
                "status": "active"
            }
            
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {"status": "error", "error": str(e)}

# Alias for compatibility
OpenAIVectorStoreManager = OpenAIFileStorageManager
VectorStoreManager = OpenAIFileStorageManager
