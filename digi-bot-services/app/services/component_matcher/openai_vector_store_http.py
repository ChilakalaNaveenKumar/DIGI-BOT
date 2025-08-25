"""
OpenAI Vector Store Manager using Direct HTTP API
Creates and manages OpenAI Vector Stores using HTTP requests
"""
import os
import json
import httpx
from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger(__name__)

class OpenAIVectorStoreManager:
    """Manages documents using OpenAI's Vector Store API via HTTP"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        
        # HTTP headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }
        
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
                "vector_store": self.vector_store
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Saved vector store metadata", vector_store_id=self.vector_store_id)
        except Exception as e:
            logger.error("Failed to save metadata", error=str(e))
    
    async def _get_or_create_vector_store(self):
        """Get existing vector store or create new one"""
        
        async with httpx.AsyncClient() as client:
            # Try to get existing vector store
            if self.vector_store_id:
                try:
                    response = await client.get(
                        f"{self.base_url}/vector_stores/{self.vector_store_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        self.vector_store = response.json()
                        logger.info("Retrieved existing vector store", 
                                   vector_store_id=self.vector_store_id,
                                   status=self.vector_store.get('status'))
                        return self.vector_store
                    else:
                        logger.warning("Failed to retrieve existing vector store", 
                                     vector_store_id=self.vector_store_id, 
                                     status_code=response.status_code)
                        self.vector_store_id = None
                        
                except Exception as e:
                    logger.warning("Failed to retrieve existing vector store", 
                                 vector_store_id=self.vector_store_id, 
                                 error=str(e))
                    self.vector_store_id = None
            
            # Create new vector store
            try:
                create_data = {
                    "name": self.vector_store_name,
                    "metadata": self.vector_store_metadata
                }
                
                response = await client.post(
                    f"{self.base_url}/vector_stores",
                    headers=self.headers,
                    json=create_data
                )
                
                if response.status_code == 200:
                    self.vector_store = response.json()
                    self.vector_store_id = self.vector_store['id']
                    
                    logger.info("Created new vector store", 
                               vector_store_id=self.vector_store_id,
                               name=self.vector_store_name)
                    
                    # Save metadata
                    self._save_metadata()
                    
                    return self.vector_store
                else:
                    raise Exception(f"Failed to create vector store: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error("Failed to create vector store", error=str(e))
                raise
    
    async def _upload_file(self, local_path: str, consistent_name: str) -> Optional[str]:
        """Upload a file to OpenAI"""
        try:
            async with httpx.AsyncClient() as client:
                # Prepare file upload
                with open(local_path, 'rb') as f:
                    files = {
                        'file': (consistent_name, f, 'text/markdown'),
                        'purpose': (None, 'assistants')
                    }
                    
                    upload_headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        # Don't set Content-Type for multipart uploads
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/files",
                        headers=upload_headers,
                        files=files
                    )
                
                if response.status_code == 200:
                    file_data = response.json()
                    logger.info("Uploaded file", 
                               filename=consistent_name,
                               file_id=file_data['id'],
                               size=file_data['bytes'])
                    return file_data['id']
                else:
                    logger.error("Failed to upload file", 
                                filename=consistent_name,
                                status_code=response.status_code,
                                error=response.text)
                    return None
                    
        except Exception as e:
            logger.error("Failed to upload file", 
                        filename=consistent_name, 
                        error=str(e))
            return None
    
    async def _add_file_to_vector_store(self, file_id: str) -> bool:
        """Add a file to the vector store"""
        try:
            async with httpx.AsyncClient() as client:
                add_data = {"file_id": file_id}
                
                response = await client.post(
                    f"{self.base_url}/vector_stores/{self.vector_store_id}/files",
                    headers=self.headers,
                    json=add_data
                )
                
                if response.status_code == 200:
                    vs_file_data = response.json()
                    logger.info("Added file to vector store", 
                               file_id=file_id,
                               vector_store_file_id=vs_file_data['id'])
                    return True
                else:
                    logger.error("Failed to add file to vector store", 
                                file_id=file_id,
                                status_code=response.status_code,
                                error=response.text)
                    return False
                    
        except Exception as e:
            logger.error("Failed to add file to vector store", 
                        file_id=file_id, 
                        error=str(e))
            return False
    
    async def _list_vector_store_files(self) -> List[Dict[str, Any]]:
        """List files in the vector store"""
        try:
            if not self.vector_store_id:
                return []
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/vector_stores/{self.vector_store_id}/files",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    files = data.get('data', [])
                    
                    # Get file details for each
                    file_details = []
                    for file in files:
                        try:
                            file_response = await client.get(
                                f"{self.base_url}/files/{file['id']}",
                                headers=self.headers
                            )
                            
                            if file_response.status_code == 200:
                                file_info = file_response.json()
                                file_details.append({
                                    "id": file['id'],
                                    "filename": file_info.get('filename', 'unknown'),
                                    "bytes": file_info.get('bytes', 0),
                                    "status": file.get('status', 'unknown'),
                                    "created_at": file.get('created_at')
                                })
                        except Exception as e:
                            logger.warning("Failed to get file details", file_id=file['id'], error=str(e))
                    
                    return file_details
                else:
                    logger.error("Failed to list vector store files", 
                                status_code=response.status_code,
                                error=response.text)
                    return []
                    
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
                file_id = await self._upload_file(local_path, consistent_name)
                
                if file_id:
                    # Add to vector store
                    if await self._add_file_to_vector_store(file_id):
                        uploaded_count += 1
                        logger.info("Successfully added to vector store", 
                                   filename=consistent_name,
                                   file_id=file_id)
                    else:
                        logger.error("Failed to add to vector store", filename=consistent_name)
                else:
                    logger.error("Failed to upload", filename=consistent_name)
            
            # Update metadata
            if uploaded_count > 0:
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
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"{self.base_url}/vector_stores/{self.vector_store_id}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        logger.info("Deleted vector store", vector_store_id=self.vector_store_id)
                    else:
                        logger.error("Failed to delete vector store", 
                                    status_code=response.status_code,
                                    error=response.text)
                
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
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/vector_stores/{self.vector_store_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    self.vector_store = response.json()
                else:
                    logger.error("Failed to refresh vector store info", 
                                status_code=response.status_code)
            
            files = await self._list_vector_store_files()
            total_bytes = sum(f["bytes"] for f in files)
            
            return {
                "storage_type": "openai_vector_store",
                "vector_store_id": self.vector_store_id,
                "vector_store_name": self.vector_store.get('name'),
                "status": self.vector_store.get('status'),
                "file_counts": self.vector_store.get('file_counts', {}),
                "files": [f["filename"] for f in files],
                "file_details": files,
                "total_bytes": total_bytes,
                "created_at": self.vector_store.get('created_at'),
                "metadata": self.vector_store.get('metadata', {})
            }
            
        except Exception as e:
            logger.error("Failed to get stats", error=str(e))
            return {"status": "error", "error": str(e)}

# Backward compatibility
VectorStoreManager = OpenAIVectorStoreManager
