"""
Search API Router - Live Search Endpoints

Handles web search and information retrieval capabilities.
"""

import logging
from typing import List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.search_service import SearchService
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    """Request model for search operations."""
    query: str
    max_results: int = 10
    search_type: str = "web"  # web, news, images, videos
    language: str = "en"
    region: str = "us"


class SearchResult(BaseModel):
    """Individual search result model."""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str] = None
    relevance_score: Optional[float] = None


class SearchResponse(BaseModel):
    """Response model for search operations."""
    success: bool
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    metadata: dict


@router.post("/web", response_model=SearchResponse)
async def web_search(request: SearchRequest):
    """
    Perform live web search.
    
    Args:
        request: Search request with query and parameters
    
    Returns:
        JSON response with search results
    """
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )
        
        if request.max_results > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 results allowed per search"
            )
        
        logger.info(
            "Processing web search request",
            query=request.query[:100] + "..." if len(request.query) > 100 else request.query,
            max_results=request.max_results,
            search_type=request.search_type
        )
        
        search_service = SearchService()
        results = await search_service.search_web(
            request.query,
            request.max_results,
            request.search_type,
            request.language,
            request.region
        )
        
        logger.info(
            "Web search completed successfully",
            results_count=len(results["results"]),
            search_time=results["search_time"]
        )
        
        return SearchResponse(
            success=True,
            query=request.query,
            results=[SearchResult(**result) for result in results["results"]],
            total_results=results["total_results"],
            search_time=results["search_time"],
            metadata={
                "type": "search_result",
                "search_type": request.search_type,
                "language": request.language,
                "region": request.region
            }
        )
        
    except DigiSetuException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Web search failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}"
        )


@router.get("/web")
async def web_search_get(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    search_type: str = Query("web", description="Type of search (web, news, images, videos)"),
    language: str = Query("en", description="Language code"),
    region: str = Query("us", description="Region code")
):
    """
    Perform live web search using GET parameters.
    
    Args:
        query: Search query
        max_results: Maximum number of results (1-50)
        search_type: Type of search
        language: Language code
        region: Region code
    
    Returns:
        JSON response with search results
    """
    request = SearchRequest(
        query=query,
        max_results=max_results,
        search_type=search_type,
        language=language,
        region=region
    )
    return await web_search(request)


@router.post("/news")
async def news_search(
    query: str,
    max_results: int = 10,
    language: str = "en",
    region: str = "us",
    time_range: str = "week"  # hour, day, week, month, year
):
    """
    Search for news articles.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        language: Language code
        region: Region code
        time_range: Time range for news search
    
    Returns:
        JSON response with news search results
    """
    try:
        logger.info(
            "Processing news search request",
            query=query[:100] + "..." if len(query) > 100 else query,
            time_range=time_range
        )
        
        search_service = SearchService()
        results = await search_service.search_news(
            query, max_results, language, region, time_range
        )
        
        logger.info("News search completed successfully")
        
        return {
            "success": True,
            "query": query,
            "results": results["results"],
            "total_results": results["total_results"],
            "search_time": results["search_time"],
            "metadata": {
                "type": "news_search_result",
                "time_range": time_range,
                "language": language,
                "region": region
            }
        }
        
    except Exception as e:
        logger.error("News search failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"News search failed: {str(e)}"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Partial search query"),
    max_suggestions: int = Query(5, ge=1, le=10, description="Maximum number of suggestions")
):
    """
    Get search query suggestions.
    
    Args:
        query: Partial search query
        max_suggestions: Maximum number of suggestions
    
    Returns:
        JSON response with search suggestions
    """
    try:
        search_service = SearchService()
        suggestions = await search_service.get_suggestions(query, max_suggestions)
        
        return {
            "success": True,
            "query": query,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error("Failed to get search suggestions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.get("/trending")
async def get_trending_topics(
    region: str = Query("us", description="Region code"),
    category: str = Query("general", description="Category (general, technology, business, etc.)")
):
    """
    Get trending search topics.
    
    Args:
        region: Region code
        category: Topic category
    
    Returns:
        JSON response with trending topics
    """
    try:
        search_service = SearchService()
        trends = await search_service.get_trending_topics(region, category)
        
        return {
            "success": True,
            "region": region,
            "category": category,
            "trends": trends
        }
        
    except Exception as e:
        logger.error("Failed to get trending topics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending topics: {str(e)}"
        )

