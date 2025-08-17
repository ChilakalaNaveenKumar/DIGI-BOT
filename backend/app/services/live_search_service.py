"""
Live Search Service - Real-time Web Search Integration

Implements live search capabilities with real-time web access and result streaming.
"""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

import structlog
import httpx
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class SearchProvider(str, Enum):
    """Available search providers."""
    SERP_API = "serp_api"
    BING_API = "bing_api"
    GOOGLE_API = "google_api"
    DUCKDUCKGO = "duckduckgo"
    MOCK = "mock"


class SearchResultType(str, Enum):
    """Types of search results."""
    WEB = "web"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"
    ACADEMIC = "academic"
    SHOPPING = "shopping"


class LiveSearchResult(BaseModel):
    """Individual search result."""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[datetime] = None
    result_type: SearchResultType = SearchResultType.WEB
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = {}


class LiveSearchResponse(BaseModel):
    """Complete search response."""
    query: str
    results: List[LiveSearchResult]
    total_results: int
    search_time: float
    provider: SearchProvider
    search_type: SearchResultType
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class LiveSearchRequest(BaseModel):
    """Live search request."""
    query: str
    search_type: SearchResultType = SearchResultType.WEB
    max_results: int = 10
    provider: SearchProvider = SearchProvider.MOCK
    include_images: bool = False
    include_videos: bool = False
    time_filter: Optional[str] = None  # "day", "week", "month", "year"
    region: str = "us"
    language: str = "en"


class LiveSearchService:
    """Service for real-time web search integration."""
    
    def __init__(self):
        """Initialize live search service."""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # API keys from settings
        self.serp_api_key = getattr(settings, 'SERP_API_KEY', None)
        self.bing_api_key = getattr(settings, 'BING_SEARCH_API_KEY', None)
        self.google_api_key = getattr(settings, 'GOOGLE_SEARCH_API_KEY', None)
        
        # Rate limiting
        self.last_search_time = {}
        self.min_search_interval = 1.0  # Minimum seconds between searches
    
    async def search(self, request: LiveSearchRequest) -> LiveSearchResponse:
        """
        Perform live search with specified provider.
        
        Args:
            request: Search request configuration
            
        Returns:
            Search results from the specified provider
        """
        try:
            start_time = time.time()
            
            logger.info(
                "Starting live search",
                query=request.query,
                search_type=request.search_type,
                provider=request.provider,
                max_results=request.max_results
            )
            
            # Rate limiting check
            await self._check_rate_limit(request.provider)
            
            # Perform search based on provider
            if request.provider == SearchProvider.SERP_API:
                results = await self._search_serp_api(request)
            elif request.provider == SearchProvider.BING_API:
                results = await self._search_bing_api(request)
            elif request.provider == SearchProvider.GOOGLE_API:
                results = await self._search_google_api(request)
            elif request.provider == SearchProvider.DUCKDUCKGO:
                results = await self._search_duckduckgo(request)
            else:
                # Default to mock search
                results = await self._search_mock(request)
            
            search_time = time.time() - start_time
            
            response = LiveSearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time=search_time,
                provider=request.provider,
                search_type=request.search_type,
                timestamp=datetime.now(),
                metadata={
                    "max_results_requested": request.max_results,
                    "time_filter": request.time_filter,
                    "region": request.region,
                    "language": request.language
                }
            )
            
            logger.info(
                "Live search completed",
                query=request.query,
                results_count=len(results),
                search_time=search_time,
                provider=request.provider
            )
            
            return response
            
        except Exception as e:
            logger.error("Live search failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "LIVE_SEARCH_FAILED",
                f"Live search failed: {str(e)}",
                500,
                {"query": request.query, "provider": request.provider}
            )
    
    async def stream_search_results(
        self,
        request: LiveSearchRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream search results as they become available.
        
        Args:
            request: Search request configuration
            
        Yields:
            Search results as they're found
        """
        try:
            logger.info("Starting streaming search", query=request.query)
            
            yield {
                "type": "search_start",
                "query": request.query,
                "provider": request.provider,
                "timestamp": datetime.now().isoformat()
            }
            
            # Perform search
            response = await self.search(request)
            
            # Stream results one by one
            for i, result in enumerate(response.results):
                yield {
                    "type": "search_result",
                    "index": i,
                    "result": {
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "source": result.source,
                        "published_date": result.published_date.isoformat() if result.published_date else None,
                        "result_type": result.result_type,
                        "relevance_score": result.relevance_score
                    }
                }
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.1)
            
            yield {
                "type": "search_complete",
                "total_results": response.total_results,
                "search_time": response.search_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Streaming search failed", error=str(e))
            yield {
                "type": "search_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_rate_limit(self, provider: SearchProvider):
        """Check and enforce rate limiting."""
        
        current_time = time.time()
        last_time = self.last_search_time.get(provider, 0)
        
        if current_time - last_time < self.min_search_interval:
            wait_time = self.min_search_interval - (current_time - last_time)
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s for {provider}")
            await asyncio.sleep(wait_time)
        
        self.last_search_time[provider] = time.time()
    
    async def _search_serp_api(self, request: LiveSearchRequest) -> List[LiveSearchResult]:
        """Search using SerpAPI."""
        
        if not self.serp_api_key:
            logger.warning("SerpAPI key not configured, falling back to mock")
            return await self._search_mock(request)
        
        try:
            params = {
                "q": request.query,
                "api_key": self.serp_api_key,
                "engine": "google",
                "num": request.max_results,
                "gl": request.region,
                "hl": request.language
            }
            
            if request.time_filter:
                params["tbs"] = f"qdr:{request.time_filter[0]}"  # d, w, m, y
            
            response = await self.http_client.get(
                "https://serpapi.com/search",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic_results", [])[:request.max_results]:
                result = LiveSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=item.get("displayed_link", ""),
                    result_type=request.search_type,
                    relevance_score=item.get("position", 0) / 10.0,
                    metadata={"position": item.get("position", 0)}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error("SerpAPI search failed", error=str(e))
            return await self._search_mock(request)
    
    async def _search_bing_api(self, request: LiveSearchRequest) -> List[LiveSearchResult]:
        """Search using Bing Search API."""
        
        if not self.bing_api_key:
            logger.warning("Bing API key not configured, falling back to mock")
            return await self._search_mock(request)
        
        try:
            headers = {
                "Ocp-Apim-Subscription-Key": self.bing_api_key
            }
            
            params = {
                "q": request.query,
                "count": request.max_results,
                "mkt": f"{request.language}-{request.region}",
                "responseFilter": "Webpages"
            }
            
            if request.time_filter:
                # Bing time filters: Day, Week, Month
                time_map = {"day": "Day", "week": "Week", "month": "Month"}
                params["freshness"] = time_map.get(request.time_filter, "Week")
            
            response = await self.http_client.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("webPages", {}).get("value", []):
                result = LiveSearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    source=item.get("displayUrl", ""),
                    published_date=self._parse_date(item.get("dateLastCrawled")),
                    result_type=request.search_type,
                    relevance_score=0.8,  # Bing doesn't provide explicit scores
                    metadata={"id": item.get("id", "")}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error("Bing API search failed", error=str(e))
            return await self._search_mock(request)
    
    async def _search_google_api(self, request: LiveSearchRequest) -> List[LiveSearchResult]:
        """Search using Google Custom Search API."""
        
        if not self.google_api_key:
            logger.warning("Google API key not configured, falling back to mock")
            return await self._search_mock(request)
        
        try:
            params = {
                "key": self.google_api_key,
                "cx": "your-search-engine-id",  # TODO: Configure this
                "q": request.query,
                "num": min(request.max_results, 10),  # Google limits to 10
                "gl": request.region,
                "hl": request.language
            }
            
            response = await self.http_client.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                result = LiveSearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=item.get("displayLink", ""),
                    result_type=request.search_type,
                    relevance_score=0.8,
                    metadata={"kind": item.get("kind", "")}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error("Google API search failed", error=str(e))
            return await self._search_mock(request)
    
    async def _search_duckduckgo(self, request: LiveSearchRequest) -> List[LiveSearchResult]:
        """Search using DuckDuckGo (simplified)."""
        
        try:
            # DuckDuckGo Instant Answer API (limited)
            params = {
                "q": request.query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = await self.http_client.get(
                "https://api.duckduckgo.com/",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # DuckDuckGo API is limited, so we'll create a mock result
            if data.get("Abstract"):
                result = LiveSearchResult(
                    title=data.get("Heading", request.query),
                    url=data.get("AbstractURL", ""),
                    snippet=data.get("Abstract", ""),
                    source="DuckDuckGo",
                    result_type=request.search_type,
                    relevance_score=0.7
                )
                results.append(result)
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:request.max_results-1]:
                if isinstance(topic, dict) and topic.get("Text"):
                    result = LiveSearchResult(
                        title=topic.get("Text", "")[:100],
                        url=topic.get("FirstURL", ""),
                        snippet=topic.get("Text", ""),
                        source="DuckDuckGo",
                        result_type=request.search_type,
                        relevance_score=0.6
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e))
            return await self._search_mock(request)
    
    async def _search_mock(self, request: LiveSearchRequest) -> List[LiveSearchResult]:
        """Mock search for testing and fallback."""
        
        logger.info("Using mock search", query=request.query)
        
        # Generate mock results
        results = []
        for i in range(min(request.max_results, 5)):
            result = LiveSearchResult(
                title=f"Mock Result {i+1} for '{request.query}'",
                url=f"https://example.com/result-{i+1}",
                snippet=f"This is a mock search result for the query '{request.query}'. It demonstrates how live search results would appear in the system.",
                source=f"example{i+1}.com",
                published_date=datetime.now() - timedelta(days=i),
                result_type=request.search_type,
                relevance_score=1.0 - (i * 0.1),
                metadata={"mock": True, "index": i}
            )
            results.append(result)
        
        # Simulate search delay
        await asyncio.sleep(0.5)
        
        return results
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime."""
        
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    async def get_trending_topics(self, region: str = "us") -> List[str]:
        """Get trending search topics."""
        
        try:
            # Mock trending topics
            trending = [
                "artificial intelligence",
                "climate change",
                "space exploration",
                "renewable energy",
                "quantum computing",
                "biotechnology",
                "virtual reality",
                "blockchain technology",
                "machine learning",
                "sustainable development"
            ]
            
            return trending[:10]
            
        except Exception as e:
            logger.error("Failed to get trending topics", error=str(e))
            return []
    
    async def get_search_suggestions(self, query: str, max_suggestions: int = 10) -> List[str]:
        """Get search suggestions for a query."""
        
        try:
            # Mock suggestions based on query
            base_suggestions = [
                f"{query} tutorial",
                f"{query} examples",
                f"{query} best practices",
                f"{query} guide",
                f"{query} tips",
                f"how to {query}",
                f"{query} vs",
                f"{query} benefits",
                f"{query} problems",
                f"{query} future"
            ]
            
            return base_suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error("Failed to get search suggestions", error=str(e))
            return []
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available search providers."""
        
        return {
            "serp_api": {
                "name": "SerpAPI",
                "available": bool(self.serp_api_key),
                "features": ["web", "news", "images", "videos"],
                "rate_limit": "100 searches/month (free tier)"
            },
            "bing_api": {
                "name": "Bing Search API",
                "available": bool(self.bing_api_key),
                "features": ["web", "news", "images", "videos"],
                "rate_limit": "1000 queries/month (free tier)"
            },
            "google_api": {
                "name": "Google Custom Search",
                "available": bool(self.google_api_key),
                "features": ["web", "images"],
                "rate_limit": "100 queries/day (free tier)"
            },
            "duckduckgo": {
                "name": "DuckDuckGo",
                "available": True,
                "features": ["instant_answers"],
                "rate_limit": "No official limit"
            },
            "mock": {
                "name": "Mock Search",
                "available": True,
                "features": ["web", "news", "images", "videos"],
                "rate_limit": "Unlimited"
            }
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.http_client.aclose()

