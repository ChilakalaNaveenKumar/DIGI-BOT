"""
Search Service - Web Search and Information Retrieval

Handles web search, news search, and trending topics using various search APIs.
"""

import time
from typing import Dict, List, Optional

import structlog
import httpx

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class SearchService:
    """Service for handling web search and information retrieval."""
    
    def __init__(self):
        """Initialize search service."""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Search API configurations (add your API keys to settings)
        self.search_apis = {
            "serpapi": {
                "base_url": "https://serpapi.com/search",
                "api_key": getattr(settings, "SERPAPI_KEY", None)
            },
            "bing": {
                "base_url": "https://api.bing.microsoft.com/v7.0/search",
                "api_key": getattr(settings, "BING_SEARCH_KEY", None)
            }
        }
    
    async def search_web(
        self, 
        query: str, 
        max_results: int = 10,
        search_type: str = "web",
        language: str = "en",
        region: str = "us"
    ) -> Dict[str, any]:
        """
        Perform live web search.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_type: Type of search (web, news, images, videos)
            language: Language code
            region: Region code
        
        Returns:
            Dictionary with search results and metadata
        """
        try:
            start_time = time.time()
            
            logger.info(
                "Performing web search",
                query=query[:100] + "..." if len(query) > 100 else query,
                search_type=search_type,
                max_results=max_results
            )
            
            # Try different search APIs in order of preference
            results = None
            
            # Try SerpAPI first
            if self.search_apis["serpapi"]["api_key"]:
                try:
                    results = await self._search_with_serpapi(
                        query, max_results, search_type, language, region
                    )
                except Exception as e:
                    logger.warning("SerpAPI search failed", error=str(e))
            
            # Fallback to Bing Search API
            if not results and self.search_apis["bing"]["api_key"]:
                try:
                    results = await self._search_with_bing(
                        query, max_results, search_type, language, region
                    )
                except Exception as e:
                    logger.warning("Bing search failed", error=str(e))
            
            # Fallback to mock results if no API is available
            if not results:
                logger.info("Using mock search results (no API keys configured)")
                results = await self._mock_search_results(query, max_results)
            
            search_time = time.time() - start_time
            results["search_time"] = search_time
            
            logger.info(
                "Web search completed",
                results_count=len(results["results"]),
                search_time=search_time
            )
            
            return results
            
        except Exception as e:
            logger.error("Web search failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "WEB_SEARCH_FAILED",
                f"Web search failed: {str(e)}",
                500,
                {"query": query, "search_type": search_type}
            )
    
    async def _search_with_serpapi(
        self, 
        query: str, 
        max_results: int,
        search_type: str,
        language: str,
        region: str
    ) -> Dict[str, any]:
        """Search using SerpAPI."""
        params = {
            "q": query,
            "api_key": self.search_apis["serpapi"]["api_key"],
            "num": max_results,
            "hl": language,
            "gl": region,
            "engine": "google"
        }
        
        if search_type == "news":
            params["tbm"] = "nws"
        elif search_type == "images":
            params["tbm"] = "isch"
        elif search_type == "videos":
            params["tbm"] = "vid"
        
        response = await self.http_client.get(
            self.search_apis["serpapi"]["base_url"],
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Parse SerpAPI results
        results = []
        organic_results = data.get("organic_results", [])
        
        for result in organic_results[:max_results]:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": result.get("source", ""),
                "published_date": result.get("date"),
                "relevance_score": None
            })
        
        return {
            "results": results,
            "total_results": len(results),
            "provider": "serpapi"
        }
    
    async def _search_with_bing(
        self, 
        query: str, 
        max_results: int,
        search_type: str,
        language: str,
        region: str
    ) -> Dict[str, any]:
        """Search using Bing Search API."""
        headers = {
            "Ocp-Apim-Subscription-Key": self.search_apis["bing"]["api_key"]
        }
        
        params = {
            "q": query,
            "count": max_results,
            "mkt": f"{language}-{region}",
            "responseFilter": "Webpages"
        }
        
        if search_type == "news":
            # Use Bing News Search endpoint
            url = "https://api.bing.microsoft.com/v7.0/news/search"
            params["responseFilter"] = "News"
        else:
            url = self.search_apis["bing"]["base_url"]
        
        response = await self.http_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse Bing results
        results = []
        web_pages = data.get("webPages", {}).get("value", [])
        news_articles = data.get("value", [])  # For news search
        
        items = web_pages if web_pages else news_articles
        
        for result in items[:max_results]:
            results.append({
                "title": result.get("name", ""),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", ""),
                "source": result.get("provider", [{}])[0].get("name", "") if result.get("provider") else "",
                "published_date": result.get("datePublished"),
                "relevance_score": None
            })
        
        return {
            "results": results,
            "total_results": len(results),
            "provider": "bing"
        }
    
    async def _mock_search_results(self, query: str, max_results: int) -> Dict[str, any]:
        """Generate mock search results for testing."""
        results = []
        
        for i in range(min(max_results, 5)):  # Limit mock results
            results.append({
                "title": f"Mock Result {i+1} for '{query}'",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"This is a mock search result for the query '{query}'. It demonstrates how search results would appear in the system.",
                "source": f"example{i+1}.com",
                "published_date": "2024-01-15",
                "relevance_score": 0.9 - (i * 0.1)
            })
        
        return {
            "results": results,
            "total_results": len(results),
            "provider": "mock"
        }
    
    async def search_news(
        self, 
        query: str, 
        max_results: int = 10,
        language: str = "en",
        region: str = "us",
        time_range: str = "week"
    ) -> Dict[str, any]:
        """
        Search for news articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            language: Language code
            region: Region code
            time_range: Time range for news search
        
        Returns:
            Dictionary with news search results
        """
        try:
            start_time = time.time()
            
            logger.info("Performing news search", query=query, time_range=time_range)
            
            # Use web search with news type
            results = await self.search_web(
                query, max_results, "news", language, region
            )
            
            # Add news-specific metadata
            results["time_range"] = time_range
            results["search_type"] = "news"
            
            return results
            
        except Exception as e:
            logger.error("News search failed", error=str(e))
            raise DigiSetuException(
                "NEWS_SEARCH_FAILED",
                f"News search failed: {str(e)}",
                500,
                {"query": query, "time_range": time_range}
            )
    
    async def get_suggestions(self, query: str, max_suggestions: int = 5) -> List[str]:
        """
        Get search query suggestions.
        
        Args:
            query: Partial search query
            max_suggestions: Maximum number of suggestions
        
        Returns:
            List of search suggestions
        """
        try:
            # Mock suggestions (replace with real API)
            base_suggestions = [
                f"{query} tutorial",
                f"{query} examples",
                f"{query} best practices",
                f"{query} guide",
                f"{query} tips",
                f"how to {query}",
                f"{query} vs alternatives",
                f"{query} documentation"
            ]
            
            # Return limited suggestions
            suggestions = base_suggestions[:max_suggestions]
            
            logger.info("Generated search suggestions", query=query, count=len(suggestions))
            
            return suggestions
            
        except Exception as e:
            logger.error("Failed to get search suggestions", error=str(e))
            return [f"{query} help"]  # Fallback suggestion
    
    async def get_trending_topics(self, region: str = "us", category: str = "general") -> List[Dict[str, any]]:
        """
        Get trending search topics.
        
        Args:
            region: Region code
            category: Topic category
        
        Returns:
            List of trending topics
        """
        try:
            # Mock trending topics (replace with real API)
            mock_trends = [
                {
                    "topic": "Artificial Intelligence",
                    "search_volume": 1000000,
                    "trend": "rising",
                    "category": "technology"
                },
                {
                    "topic": "Climate Change",
                    "search_volume": 800000,
                    "trend": "stable",
                    "category": "environment"
                },
                {
                    "topic": "Space Exploration",
                    "search_volume": 600000,
                    "trend": "rising",
                    "category": "science"
                },
                {
                    "topic": "Renewable Energy",
                    "search_volume": 500000,
                    "trend": "rising",
                    "category": "technology"
                },
                {
                    "topic": "Digital Health",
                    "search_volume": 400000,
                    "trend": "stable",
                    "category": "health"
                }
            ]
            
            # Filter by category if specified
            if category != "general":
                mock_trends = [t for t in mock_trends if t["category"] == category]
            
            logger.info("Retrieved trending topics", region=region, category=category, count=len(mock_trends))
            
            return mock_trends
            
        except Exception as e:
            logger.error("Failed to get trending topics", error=str(e))
            return []
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.http_client.aclose()
            logger.info("Search service cleanup completed")
        except Exception as e:
            logger.error("Search service cleanup failed", error=str(e))

