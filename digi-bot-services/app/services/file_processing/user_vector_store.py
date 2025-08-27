"""
User Vector Store Manager
Manages per-user vector stores for file-based chat functionality
"""

import os
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger(__name__)

class UserVectorStoreManager:
    """
    Manages user-specific vector stores for file chat functionality.
    Similar to OpenAI's approach but with user isolation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.expires_hours = 5  # Vector stores expire after 5 hours of inactivity
    
    async def get_user_vector_store(self, user_id: int) -> str:
        """
        Get or create a vector store for the user.
        Returns the vector store ID.
        """
        try:
            store_name = f"user_{user_id}_files"
            
            # Try to find existing store by name
            vector_stores = await self.client.vector_stores.list()
            
            for store in vector_stores.data:
                if store.name == store_name:
                    # Update expiry to keep it active
                    await self._update_store_expiry(store.id)
                    logger.info("Found existing vector store", user_id=user_id, store_id=store.id)
                    return store.id
            
            # Create new store
            store = await self.client.vector_stores.create(
                name=store_name,
                expires_after={
                    "anchor": "last_active_at",
                    "days": 1  # 5 hours = ~0.2 days, but minimum is 1 day for OpenAI
                },
                metadata={
                    "user_id": str(user_id),
                    "purpose": "file_chat",
                    "created_by": "digi_setu_ai"
                }
            )
            
            logger.info("Created new vector store", user_id=user_id, store_id=store.id)
            return store.id
            
        except Exception as e:
            logger.error("Failed to get user vector store", user_id=user_id, error=str(e))
            raise
    
    async def upload_file_to_user_store(
        self, 
        user_id: int, 
        file_path: str, 
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to the user's vector store.
        Returns file information.
        """
        try:
            # Get user's vector store
            vector_store_id = await self.get_user_vector_store(user_id)
            
            # Upload file
            with open(file_path, "rb") as file_data:
                file_obj = await self.client.files.create(
                    file=file_data,
                    purpose="assistants"
                )
            
            # Add to vector store
            vector_store_file = await self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_obj.id
            )
            
            logger.info(
                "File uploaded to user vector store",
                user_id=user_id,
                vector_store_id=vector_store_id,
                file_id=file_obj.id,
                filename=filename or file_path
            )
            
            return {
                "file_id": file_obj.id,
                "vector_store_id": vector_store_id,
                "vector_store_file_id": vector_store_file.id,
                "filename": filename or os.path.basename(file_path),
                "status": "uploaded"
            }
            
        except Exception as e:
            logger.error(
                "Failed to upload file to user vector store",
                user_id=user_id,
                filename=filename,
                error=str(e)
            )
            raise
    
    async def list_user_files(self, user_id: int) -> List[Dict[str, Any]]:
        """
        List all files in the user's vector store.
        """
        try:
            vector_store_id = await self.get_user_vector_store(user_id)
            
            files = await self.client.vector_stores.files.list(
                vector_store_id=vector_store_id
            )
            
            file_list = []
            for file in files.data:
                # Get file details
                file_details = await self.client.files.retrieve(file.id)
                file_list.append({
                    "file_id": file.id,
                    "filename": file_details.filename,
                    "bytes": file_details.bytes,
                    "created_at": file_details.created_at,
                    "status": file.status
                })
            
            return file_list
            
        except Exception as e:
            logger.error("Failed to list user files", user_id=user_id, error=str(e))
            return []
    
    async def delete_user_file(self, user_id: int, file_id: str) -> bool:
        """
        Delete a file from the user's vector store.
        """
        try:
            vector_store_id = await self.get_user_vector_store(user_id)
            
            # Remove from vector store
            await self.client.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            
            # Delete the file itself
            await self.client.files.delete(file_id)
            
            logger.info("File deleted from user vector store", user_id=user_id, file_id=file_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete user file", user_id=user_id, file_id=file_id, error=str(e))
            return False
    
    async def search_user_files(
        self, 
        user_id: int, 
        query: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search through the user's files using the vector store.
        Note: This would typically be done through the Assistants API or chat completions
        with file_search tool enabled.
        """
        try:
            vector_store_id = await self.get_user_vector_store(user_id)
            
            # For now, return the vector store ID for use in chat completions
            # The actual search happens when we call the chat API with file_search enabled
            return [{
                "vector_store_id": vector_store_id,
                "query": query,
                "max_results": max_results
            }]
            
        except Exception as e:
            logger.error("Failed to search user files", user_id=user_id, error=str(e))
            return []
    
    async def _update_store_expiry(self, vector_store_id: str):
        """Update the expiry of a vector store to keep it active."""
        try:
            await self.client.vector_stores.update(
                vector_store_id=vector_store_id,
                expires_after={
                    "anchor": "last_active_at",
                    "days": 1  # Minimum allowed by OpenAI (5 hours would be ideal)
                }
            )
        except Exception as e:
            logger.warning("Failed to update store expiry", store_id=vector_store_id, error=str(e))
    
    async def get_store_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about the user's vector store."""
        try:
            vector_store_id = await self.get_user_vector_store(user_id)
            
            # Get store details
            store = await self.client.vector_stores.retrieve(vector_store_id)
            
            # Get file count
            files = await self.client.vector_stores.files.list(vector_store_id=vector_store_id)
            
            return {
                "vector_store_id": vector_store_id,
                "name": store.name,
                "file_count": len(files.data),
                "created_at": store.created_at,
                "expires_at": store.expires_at,
                "status": store.status,
                "usage_bytes": store.usage_bytes
            }
            
        except Exception as e:
            logger.error("Failed to get store stats", user_id=user_id, error=str(e))
            return {}
