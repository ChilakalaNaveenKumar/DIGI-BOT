"""
Vector Service for Message Embeddings

Handles vector operations for message pairs using OpenAI text-embedding-3-large.
Integrates with existing conversation flow without breaking current functionality.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import structlog
import openai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, and_
from sqlalchemy.dialects.postgresql import insert

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class VectorService:
    """Service for managing message vectors and semantic search."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize OpenAI client for embeddings."""
        if self._initialized:
            return
            
        try:
            self.client = openai.AsyncOpenAI(
                api_key=self.settings.OPENAI_API_KEY
            )
            self._initialized = True
            logger.info("Vector service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize vector service", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="VECTOR_INIT_ERROR",
                message="Failed to initialize vector service"
            )
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding using OpenAI text-embedding-3-medium."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Clean and truncate text if needed
            cleaned_text = text.strip()
            if len(cleaned_text) > 8000:  # Conservative limit for embeddings
                cleaned_text = cleaned_text[:8000] + "..."
            
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=cleaned_text,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            logger.debug("Created embedding", text_length=len(cleaned_text), embedding_dim=len(embedding))
            
            return embedding
            
        except Exception as e:
            logger.error("Failed to create embedding", error=str(e), text_length=len(text))
            raise DigiSetuException(
                status_code=500,
                error_code="EMBEDDING_ERROR",
                message="Failed to create text embedding"
            )
    
    async def save_message_vector(
        self,
        user_id: int,
        conversation_id: int,
        user_message: str,
        assistant_response: str,
        turn_index: int,
        user_message_id: Optional[int] = None,
        assistant_message_id: Optional[int] = None,
        attachment_ids: Optional[List[int]] = None,
        expires_in_days: int = 7
    ) -> str:
        """Save message pair as vector with 7-day expiry."""
        
        try:
            # Create composite message content
            content = f"User: {user_message}\n\nAssistant: {assistant_response}"
            
            # Generate vector ID
            message_id = f"{user_message_id or 'u'}:{assistant_message_id or 'a'}"
            vector_id = f"vec:{conversation_id}:{message_id}"
            
            # Create embedding
            embedding = await self.create_embedding(content)
            
            # Create snippet (first 500 chars)
            snippet = content[:500] + "..." if len(content) > 500 else content
            
            # Set expiry
            expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Prepare metadata
            metadata = {
                "user_message_id": user_message_id,
                "assistant_message_id": assistant_message_id,
                "user_message_length": len(user_message),
                "assistant_response_length": len(assistant_response),
                "total_length": len(content),
                "created_by": "vector_service"
            }
            
            # Insert vector record
            query = text("""
                INSERT INTO message_vectors (
                    id, user_id, conversation_id, message_id, turn_index, 
                    role_pair, snippet, content_summary, has_attachments,
                    attachment_ids, expires_at, metadata, embedding
                ) VALUES (
                    :id, :user_id, :conversation_id, :message_id, :turn_index,
                    'user_assistant', :snippet, :content_summary, :has_attachments,
                    :attachment_ids, :expires_at, :metadata, :embedding
                )
                ON CONFLICT (id) DO UPDATE SET
                    snippet = EXCLUDED.snippet,
                    content_summary = EXCLUDED.content_summary,
                    has_attachments = EXCLUDED.has_attachments,
                    attachment_ids = EXCLUDED.attachment_ids,
                    expires_at = EXCLUDED.expires_at,
                    metadata = EXCLUDED.metadata,
                    embedding = EXCLUDED.embedding
            """)
            
            # Convert embedding list to vector format
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"
            
            await self.db.execute(query, {
                "id": vector_id,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_id": message_id,
                "turn_index": turn_index,
                "snippet": snippet,
                "content_summary": content,
                "has_attachments": bool(attachment_ids),
                "attachment_ids": attachment_ids or [],
                "expires_at": expires_at,
                "metadata": json.dumps(metadata),
                "embedding": embedding_str
            })
            
            await self.db.commit()
            
            logger.info(
                "Message vector saved",
                vector_id=vector_id,
                conversation_id=conversation_id,
                turn_index=turn_index,
                expires_at=expires_at.isoformat()
            )
            
            return vector_id
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to save message vector", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="VECTOR_SAVE_ERROR",
                message="Failed to save message vector"
            )
    
    async def search_similar_messages(
        self,
        query: str,
        user_id: int,
        limit: int = 5,
        conversation_id: Optional[int] = None,
        days_back: int = 30,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar messages using vector similarity."""
        
        try:
            # Create query embedding
            query_embedding = await self.create_embedding(query)
            
            # Build base query
            base_conditions = [
                "user_id = :user_id",
                "is_active = TRUE",
                "ts >= :since_date"
            ]
            
            params = {
                "user_id": user_id,
                "since_date": datetime.now() - timedelta(days=days_back),
                "query_embedding": query_embedding,
                "limit": limit
            }
            
            # Add conversation filter if specified
            if conversation_id:
                base_conditions.append("conversation_id = :conversation_id")
                params["conversation_id"] = conversation_id
            
            where_clause = " AND ".join(base_conditions)
            
            # Execute similarity search
            search_query = text(f"""
                SELECT 
                    id,
                    conversation_id,
                    message_id,
                    turn_index,
                    snippet,
                    content_summary,
                    has_attachments,
                    attachment_ids,
                    ts,
                    1 - (embedding <=> :query_embedding::vector) AS similarity_score
                FROM message_vectors
                WHERE {where_clause}
                ORDER BY embedding <-> :query_embedding::vector
                LIMIT :limit
            """)
            
            result = await self.db.execute(search_query, params)
            rows = result.fetchall()
            
            # Filter by similarity threshold and format results
            similar_messages = []
            for row in rows:
                if row.similarity_score >= similarity_threshold:
                    similar_messages.append({
                        "vector_id": row.id,
                        "conversation_id": row.conversation_id,
                        "message_id": row.message_id,
                        "turn_index": row.turn_index,
                        "snippet": row.snippet,
                        "content_summary": row.content_summary,
                        "has_attachments": row.has_attachments,
                        "attachment_ids": row.attachment_ids,
                        "timestamp": row.ts.isoformat(),
                        "similarity_score": float(row.similarity_score)
                    })
            
            logger.info(
                "Vector search completed",
                query_length=len(query),
                results_found=len(similar_messages),
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            return similar_messages
            
        except Exception as e:
            logger.error("Vector search failed", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="VECTOR_SEARCH_ERROR",
                message="Failed to search similar messages"
            )
    
    async def get_conversation_context(
        self,
        conversation_id: int,
        user_id: int,
        around_turn: int,
        context_window: int = 2
    ) -> List[Dict[str, Any]]:
        """Get conversation context around a specific turn."""
        
        try:
            query = text("""
                SELECT 
                    id,
                    message_id,
                    turn_index,
                    snippet,
                    content_summary,
                    has_attachments,
                    attachment_ids,
                    ts
                FROM message_vectors
                WHERE conversation_id = :conversation_id
                  AND user_id = :user_id
                  AND turn_index BETWEEN :start_turn AND :end_turn
                  AND is_active = TRUE
                ORDER BY turn_index
            """)
            
            result = await self.db.execute(query, {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "start_turn": around_turn - context_window,
                "end_turn": around_turn + context_window
            })
            
            rows = result.fetchall()
            
            context_messages = []
            for row in rows:
                context_messages.append({
                    "vector_id": row.id,
                    "message_id": row.message_id,
                    "turn_index": row.turn_index,
                    "snippet": row.snippet,
                    "content_summary": row.content_summary,
                    "has_attachments": row.has_attachments,
                    "attachment_ids": row.attachment_ids,
                    "timestamp": row.ts.isoformat()
                })
            
            logger.info(
                "Retrieved conversation context",
                conversation_id=conversation_id,
                around_turn=around_turn,
                context_messages=len(context_messages)
            )
            
            return context_messages
            
        except Exception as e:
            logger.error("Failed to get conversation context", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="CONTEXT_RETRIEVAL_ERROR",
                message="Failed to retrieve conversation context"
            )
    
    async def cleanup_expired_vectors(self) -> int:
        """Clean up expired vectors (soft delete first, then hard delete)."""
        
        try:
            # Soft delete expired vectors
            soft_delete_query = text("""
                UPDATE message_vectors 
                SET is_active = FALSE 
                WHERE expires_at < NOW() AND is_active = TRUE
            """)
            
            result = await self.db.execute(soft_delete_query)
            soft_deleted = result.rowcount
            
            # Hard delete after grace period
            hard_delete_query = text("""
                DELETE FROM message_vectors 
                WHERE is_active = FALSE AND expires_at < NOW() - INTERVAL '1 day'
            """)
            
            result = await self.db.execute(hard_delete_query)
            hard_deleted = result.rowcount
            
            # Clean up other expired records
            await self.db.execute(text("DELETE FROM conversation_summaries WHERE expires_at < NOW()"))
            await self.db.execute(text("DELETE FROM attachment_vectors WHERE expires_at < NOW()"))
            await self.db.execute(text("DELETE FROM attachments WHERE expires_at < NOW()"))
            
            await self.db.commit()
            
            total_cleaned = soft_deleted + hard_deleted
            
            logger.info(
                "Vector cleanup completed",
                soft_deleted=soft_deleted,
                hard_deleted=hard_deleted,
                total_cleaned=total_cleaned
            )
            
            return total_cleaned
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Vector cleanup failed", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="CLEANUP_ERROR",
                message="Failed to cleanup expired vectors"
            )
    
    async def get_vector_stats(self, user_id: int) -> Dict[str, Any]:
        """Get vector statistics for a user."""
        
        try:
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_vectors,
                    COUNT(*) FILTER (WHERE is_active = TRUE) as active_vectors,
                    COUNT(*) FILTER (WHERE expires_at < NOW()) as expired_vectors,
                    COUNT(DISTINCT conversation_id) as conversations_with_vectors,
                    MIN(ts) as oldest_vector,
                    MAX(ts) as newest_vector
                FROM message_vectors
                WHERE user_id = :user_id
            """)
            
            result = await self.db.execute(stats_query, {"user_id": user_id})
            row = result.fetchone()
            
            stats = {
                "total_vectors": row.total_vectors,
                "active_vectors": row.active_vectors,
                "expired_vectors": row.expired_vectors,
                "conversations_with_vectors": row.conversations_with_vectors,
                "oldest_vector": row.oldest_vector.isoformat() if row.oldest_vector else None,
                "newest_vector": row.newest_vector.isoformat() if row.newest_vector else None
            }
            
            logger.info("Retrieved vector stats", user_id=user_id, stats=stats)
            return stats
            
        except Exception as e:
            logger.error("Failed to get vector stats", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="STATS_ERROR",
                message="Failed to retrieve vector statistics"
            )


# Async context manager for vector service
class VectorServiceManager:
    """Context manager for vector service operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.service = None
    
    async def __aenter__(self) -> VectorService:
        self.service = VectorService(self.db)
        await self.service.initialize()
        return self.service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass


# Utility function for easy access
async def get_vector_service(db: AsyncSession) -> VectorService:
    """Get initialized vector service."""
    service = VectorService(db)
    await service.initialize()
    return service
