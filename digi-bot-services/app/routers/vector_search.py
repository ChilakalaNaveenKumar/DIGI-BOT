"""
Vector Search API Router

Provides vector search capabilities for semantic message search.
Integrates with existing conversation system.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.auth.core.auth_deps import get_current_user_required
from app.services.vector import get_vector_service

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/vector", tags=["vector-search"])


class VectorSearchRequest(BaseModel):
    """Request model for vector search."""
    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    conversation_id: Optional[int] = Field(None, description="Search within specific conversation")
    limit: int = Field(5, description="Maximum number of results", ge=1, le=20)
    days_back: int = Field(30, description="Search within last N days", ge=1, le=365)
    similarity_threshold: float = Field(0.7, description="Minimum similarity score", ge=0.0, le=1.0)


class VectorSearchResult(BaseModel):
    """Response model for vector search results."""
    vector_id: str
    conversation_id: int
    message_id: str
    turn_index: int
    snippet: str
    similarity_score: float
    timestamp: str
    has_attachments: bool


class VectorSearchResponse(BaseModel):
    """Response model for vector search."""
    query: str
    results: List[VectorSearchResult]
    total_found: int
    search_time_ms: int


class VectorStatsResponse(BaseModel):
    """Response model for vector statistics."""
    total_vectors: int
    active_vectors: int
    expired_vectors: int
    conversations_with_vectors: int
    oldest_vector: Optional[str]
    newest_vector: Optional[str]


@router.post("/search", response_model=VectorSearchResponse)
async def search_messages(
    request: VectorSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Search for similar messages using vector similarity.
    
    Finds semantically similar conversations based on the query.
    Can search within a specific conversation or across all user's conversations.
    """
    
    try:
        import time
        start_time = time.time()
        
        # Get vector service
        vector_service = await get_vector_service(db)
        
        # Perform search
        results = await vector_service.search_similar_messages(
            query=request.query,
            user_id=current_user["id"],
            limit=request.limit,
            conversation_id=request.conversation_id,
            days_back=request.days_back,
            similarity_threshold=request.similarity_threshold
        )
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        # Format results
        search_results = [
            VectorSearchResult(
                vector_id=result["vector_id"],
                conversation_id=result["conversation_id"],
                message_id=result["message_id"],
                turn_index=result["turn_index"],
                snippet=result["snippet"],
                similarity_score=result["similarity_score"],
                timestamp=result["timestamp"],
                has_attachments=result["has_attachments"]
            )
            for result in results
        ]
        
        logger.info(
            "Vector search completed",
            user_id=current_user["id"],
            query_length=len(request.query),
            results_found=len(search_results),
            search_time_ms=search_time_ms
        )
        
        return VectorSearchResponse(
            query=request.query,
            results=search_results,
            total_found=len(search_results),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        logger.error(
            "Vector search failed",
            user_id=current_user["id"],
            query=request.query,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector search failed: {str(e)}"
        )


@router.get("/stats", response_model=VectorStatsResponse)
async def get_vector_stats(
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get vector statistics for the current user.
    
    Shows information about stored vectors, active/expired counts, etc.
    """
    
    try:
        # Get vector service
        vector_service = await get_vector_service(db)
        
        # Get stats
        stats = await vector_service.get_vector_stats(current_user["id"])
        
        logger.info(
            "Vector stats retrieved",
            user_id=current_user["id"],
            stats=stats
        )
        
        return VectorStatsResponse(**stats)
        
    except Exception as e:
        logger.error(
            "Failed to get vector stats",
            user_id=current_user["id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get vector statistics: {str(e)}"
        )


@router.get("/conversation/{conversation_id}/context")
async def get_conversation_context(
    conversation_id: int,
    around_turn: int = Query(..., description="Turn index to get context around"),
    context_window: int = Query(2, description="Number of turns before/after", ge=1, le=10),
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get conversation context around a specific turn.
    
    Useful for understanding the context of a specific message exchange.
    """
    
    try:
        # Get vector service
        vector_service = await get_vector_service(db)
        
        # Get context
        context = await vector_service.get_conversation_context(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            around_turn=around_turn,
            context_window=context_window
        )
        
        logger.info(
            "Conversation context retrieved",
            user_id=current_user["id"],
            conversation_id=conversation_id,
            around_turn=around_turn,
            context_messages=len(context)
        )
        
        return {
            "conversation_id": conversation_id,
            "around_turn": around_turn,
            "context_window": context_window,
            "context": context,
            "total_messages": len(context)
        }
        
    except Exception as e:
        logger.error(
            "Failed to get conversation context",
            user_id=current_user["id"],
            conversation_id=conversation_id,
            around_turn=around_turn,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversation context: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_expired_vectors(
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Manually trigger cleanup of expired vectors.
    
    Normally this runs automatically, but can be triggered manually for testing.
    """
    
    try:
        # Get vector service
        vector_service = await get_vector_service(db)
        
        # Cleanup expired vectors
        cleaned_count = await vector_service.cleanup_expired_vectors()
        
        logger.info(
            "Manual vector cleanup completed",
            user_id=current_user["id"],
            cleaned_count=cleaned_count
        )
        
        return {
            "success": True,
            "cleaned_count": cleaned_count,
            "message": f"Cleaned up {cleaned_count} expired vectors"
        }
        
    except Exception as e:
        logger.error(
            "Manual vector cleanup failed",
            user_id=current_user["id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector cleanup failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for vector search service."""
    return {
        "status": "ok",
        "service": "vector-search",
        "message": "Vector search service is operational"
    }
