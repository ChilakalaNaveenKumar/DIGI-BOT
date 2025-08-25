"""
OpenAI Vector Store Manager
Creates and manages an actual OpenAI Vector Store with consistent ID
"""
import os
import json
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger(__name__)

class OpenAIVectorStoreManager:
    """Manages documents using OpenAI's actual Vector Store API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Consistent vector store name and metadata
        self.vector_store_name = "digi_setu_component_matcher"
        self.vector_store_metadata = {
            "project": "digi_setu",
            "purpose": "component_matching", 
            "version": "v3"
        }
        
        # Document paths
        self.documents_folder = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/component_matcher/documents"
        
        # File mapping with consistent names
        self.file_mapping = {
            "chartjs_markdown_format_v1.md": "digi_setu_charts_v3.md",
            "data_table_markdown_format_v1.md": "digi_setu_tables_v3.md", 
            "Examples.md": "digi_setu_examples.md",
            "PositionAnchors.md": "digi_setu_positions.md"
        }
        
        # Store vector store info
        self.metadata_file = os.path.join(self.documents_folder, "vector_store_metadata.json")
        self.vector_store = None
        self.vector_store_id = None
        self._initialized = False
    
    def _load_metadata(self):
        """Load existing vector store metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.vector_store_id = data.get('vector_store_id')
                logger.info("Loaded vector store metadata", vector_store_id=self.vector_store_id)
            except Exception as e:
                logger.error("Failed to load metadata", error=str(e))
                self.vector_store_id = None
        else:
            self.vector_store_id = None
    
    def _save_metadata(self):
        """Save vector store metadata"""
        try:
            data = {
                "vector_store_id": self.vector_store_id,
                "vector_store_name": self.vector_store_name,
                "created_at": self.vector_store.created_at if self.vector_store else None,
                "file_counts": self.vector_store.file_counts.dict() if self.vector_store else None
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Saved vector store metadata", vector_store_id=self.vector_store_id)
        except Exception as e:
            logger.error("Failed to save metadata", error=str(e))
    
    async def _get_or_create_vector_store(self):
        """Get existing vector store or create new one"""
        
        # Try to get existing vector store
        if self.vector_store_id:
            try:
                self.vector_store = await self.client.beta.vector_stores.retrieve(
                    vector_store_id=self.vector_store_id
                )
                logger.info("Retrieved existing vector store", 
                           vector_store_id=self.vector_store_id,
                           status=self.vector_store.status)
                return self.vector_store
            except Exception as e:
                logger.warning("Failed to retrieve existing vector store", 
                             vector_store_id=self.vector_store_id, 
                             error=str(e))
                self.vector_store_id = None
        
        # Create new vector store
        try:
            self.vector_store = await self.client.beta.vector_stores.create(
                name=self.vector_store_name,
                metadata=self.vector_store_metadata
            )
            self.vector_store_id = self.vector_store.id
            
            logger.info("Created new vector store", 
                       vector_store_id=self.vector_store_id,
                       name=self.vector_store_name)
            
            # Save metadata
            self._save_metadata()
            
            return self.vector_store
            
        except Exception as e:
            logger.error("Failed to create vector store", error=str(e))
            raise
    
    async def _upload_file_to_vector_store(self, local_path: str, consistent_name: str) -> Optional[str]:
        """Upload a file and add it to the vector store"""
        try:
            # Upload file first
            with open(local_path, 'rb') as f:
                file_obj = await self.client.files.create(
                    file=f,
                    purpose="assistants"
                )
            
            logger.info("Uploaded file", 
                       filename=consistent_name,
                       file_id=file_obj.id,
                       size=file_obj.bytes)
            
            # Add file to vector store
            vector_store_file = await self.client.beta.vector_stores.files.create(
                vector_store_id=self.vector_store_id,
                file_id=file_obj.id
            )
            
            logger.info("Added file to vector store", 
                       filename=consistent_name,
                       file_id=file_obj.id,
                       vector_store_file_id=vector_store_file.id)
            
            return file_obj.id
            
        except Exception as e:
            logger.error("Failed to upload file to vector store", 
                        filename=consistent_name, 
                        error=str(e))
            return None
    
    async def _list_vector_store_files(self) -> List[Dict[str, Any]]:
        """List files in the vector store"""
        try:
            if not self.vector_store_id:
                return []
            
            files = await self.client.beta.vector_stores.files.list(
                vector_store_id=self.vector_store_id
            )
            
            file_list = []
            for file in files.data:
                # Get file details
                try:
                    file_details = await self.client.files.retrieve(file.id)
                    file_list.append({
                        "id": file.id,
                        "filename": file_details.filename,
                        "bytes": file_details.bytes,
                        "status": file.status,
                        "created_at": file.created_at
                    })
                except Exception as e:
                    logger.warning("Failed to get file details", file_id=file.id, error=str(e))
            
            return file_list
            
        except Exception as e:
            logger.error("Failed to list vector store files", error=str(e))
            return []
    
    async def initialize(self):
        """Initialize vector store and upload documents"""
        if self._initialized:
            files = await self._list_vector_store_files()
            return len(files)
        
        try:
            # Load existing metadata
            self._load_metadata()
            
            # Get or create vector store
            await self._get_or_create_vector_store()
            
            # Get existing files in vector store
            existing_files = await self._list_vector_store_files()
            existing_filenames = {f["filename"] for f in existing_files}
            
            logger.info("Found existing files in vector store", count=len(existing_files))
            for f in existing_files:
                logger.info("Existing file", filename=f["filename"], file_id=f["id"])
            
            # Process each local document
            uploaded_count = 0
            for local_filename in os.listdir(self.documents_folder):
                if not local_filename.endswith('.md'):
                    continue
                
                consistent_name = self.file_mapping.get(local_filename, local_filename)
                local_path = os.path.join(self.documents_folder, local_filename)
                
                # Check if already uploaded
                if consistent_name in existing_filenames:
                    logger.info("File already exists in vector store", filename=consistent_name)
                    continue
                
                # Upload new file
                logger.info("Uploading new file to vector store", filename=consistent_name)
                file_id = await self._upload_file_to_vector_store(local_path, consistent_name)
                
                if file_id:
                    uploaded_count += 1
                    logger.info("Successfully added to vector store", 
                               filename=consistent_name,
                               file_id=file_id)
                else:
                    logger.error("Failed to add to vector store", filename=consistent_name)
            
            # Update metadata
            if uploaded_count > 0:
                # Refresh vector store info
                self.vector_store = await self.client.beta.vector_stores.retrieve(
                    vector_store_id=self.vector_store_id
                )
                self._save_metadata()
            
            self._initialized = True
            
            # Get final file count
            final_files = await self._list_vector_store_files()
            
            logger.info("Vector store initialization complete", 
                       total_files=len(final_files),
                       new_uploads=uploaded_count,
                       vector_store_id=self.vector_store_id)
            
            return len(final_files)
            
        except Exception as e:
            logger.error("Failed to initialize vector store", error=str(e))
            raise
    
    async def query(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query the vector store (placeholder - would use assistant API)"""
        if not self._initialized:
            await self.initialize()
        
        # Note: To actually query a vector store, you'd typically use the Assistants API
        # or create a thread and run with the vector store attached
        
        logger.info("Vector store query requested", 
                   query_length=len(query_text), 
                   top_k=top_k,
                   vector_store_id=self.vector_store_id)
        
        # For now, return file list as placeholder
        files = await self._list_vector_store_files()
        results = []
        for file in files:
            results.append({
                "text": f"Content from {file['filename']}",
                "score": 0.8,  # Placeholder score
                "meta": {
                    "filename": file["filename"],
                    "file_id": file["id"],
                    "bytes": file["bytes"]
                }
            })
        
        return results[:top_k]
    
    async def clear_all_docs(self):
        """Delete the entire vector store"""
        try:
            if self.vector_store_id:
                await self.client.beta.vector_stores.delete(
                    vector_store_id=self.vector_store_id
                )
                logger.info("Deleted vector store", vector_store_id=self.vector_store_id)
                
                # Clear local metadata
                self.vector_store_id = None
                self.vector_store = None
                if os.path.exists(self.metadata_file):
                    os.remove(self.metadata_file)
                
                logger.info("Cleared vector store metadata")
            
        except Exception as e:
            logger.error("Failed to clear vector store", error=str(e))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            if not self._initialized:
                await self.initialize()
            
            if not self.vector_store:
                return {"status": "error", "error": "No vector store"}
            
            # Refresh vector store info
            self.vector_store = await self.client.beta.vector_stores.retrieve(
                vector_store_id=self.vector_store_id
            )
            
            files = await self._list_vector_store_files()
            total_bytes = sum(f["bytes"] for f in files)
            
            return {
                "storage_type": "openai_vector_store",
                "vector_store_id": self.vector_store_id,
                "vector_store_name": self.vector_store.name,
                "status": self.vector_store.status,
                "file_counts": self.vector_store.file_counts.dict() if self.vector_store.file_counts else {},
                "files": [f["filename"] for f in files],
                "file_details": files,
                "total_bytes": total_bytes,
                "created_at": self.vector_store.created_at,
                "metadata": self.vector_store.metadata
            }
            
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {"status": "error", "error": str(e)}

# Backward compatibility
VectorStoreManager = OpenAIVectorStoreManager
