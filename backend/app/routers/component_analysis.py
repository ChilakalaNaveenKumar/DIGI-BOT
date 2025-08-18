"""
Component Analysis Router

Handles AI-powered content analysis for dynamic component generation.
"""

import json
import time
from typing import Dict, Any, Optional, List

import structlog
from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import DigiSetuException
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.component_analysis_service import ComponentAnalysisService

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["component-analysis"])


class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis."""
    content: str
    context: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None


class ComponentDecision(BaseModel):
    """Response model for component generation decision."""
    decision: str  # "GENERATE_NOW" or "NO_COMPONENT"
    component_type: Optional[str] = None  # "pie-chart", "bar-chart", "line-chart", "data-table"
    confidence: float
    reasoning: str
    markdown: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


@router.post("/test")
async def test_endpoint():
    """Test endpoint for component analysis connectivity."""
    return {
        "message": "Component Analysis router is working",
        "timestamp": time.time(),
        "service": "component-analysis"
    }


@router.post("/analyze", response_model=ComponentDecision)
async def analyze_content(
    request: ContentAnalysisRequest,
    current_user = Depends(get_current_user),
    http_request: Request = None,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Analyze content and determine if enhanced components should be generated.
    
    This endpoint uses Claude Sonnet to analyze content and decide whether
    to generate interactive components like charts or tables.
    """
    try:
        # Get component analysis service
        if not hasattr(http_request.app.state, 'component_analysis_service'):
            # Initialize service if not already done
            service = ComponentAnalysisService()
            await service.initialize()
            http_request.app.state.component_analysis_service = service
        else:
            service = http_request.app.state.component_analysis_service
        
        logger.info(
            "Analyzing content for component generation",
            user_id=getattr(current_user, 'id', 'anonymous'),
            content_length=len(request.content)
        )
        
        # Analyze content using AI
        decision = await service.analyze_content(
            content=request.content,
            context=request.context,
            user_preferences=request.user_preferences or {}
        )
        
        logger.info(
            "Content analysis completed",
            decision=decision.decision,
            component_type=decision.component_type,
            confidence=decision.confidence
        )
        
        return decision
        
    except Exception as e:
        logger.error(
            "Content analysis failed",
            error=str(e),
            content_preview=request.content[:100] + "..." if len(request.content) > 100 else request.content
        )
        
        # Return a safe fallback response
        return ComponentDecision(
            decision="NO_COMPONENT",
            confidence=0.0,
            reasoning=f"Analysis failed due to error: {str(e)}"
        )


@router.post("/batch-analyze")
async def batch_analyze_content(
    requests: List[ContentAnalysisRequest],
    current_user = Depends(get_current_user),
    http_request: Request = None,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Analyze multiple content chunks in batch for component generation.
    
    Useful for analyzing entire documents or multiple content sections.
    """
    try:
        if len(requests) > 10:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 10 items"
            )
        
        # Get component analysis service
        if not hasattr(http_request.app.state, 'component_analysis_service'):
            service = ComponentAnalysisService()
            await service.initialize()
            http_request.app.state.component_analysis_service = service
        else:
            service = http_request.app.state.component_analysis_service
        
        logger.info(
            "Starting batch content analysis",
            user_id=getattr(current_user, 'id', 'anonymous'),
            batch_size=len(requests)
        )
        
        # Process all requests
        results = []
        for i, request in enumerate(requests):
            try:
                decision = await service.analyze_content(
                    content=request.content,
                    context=request.context,
                    user_preferences=request.user_preferences or {}
                )
                results.append({
                    "index": i,
                    "success": True,
                    "decision": decision
                })
            except Exception as e:
                logger.error(f"Failed to analyze content at index {i}", error=str(e))
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e),
                    "decision": ComponentDecision(
                        decision="NO_COMPONENT",
                        confidence=0.0,
                        reasoning=f"Analysis failed: {str(e)}"
                    )
                })
        
        logger.info(
            "Batch analysis completed",
            total_requests=len(requests),
            successful=sum(1 for r in results if r["success"]),
            failed=sum(1 for r in results if not r["success"])
        )
        
        return {
            "total": len(requests),
            "results": results,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error("Batch analysis failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )


@router.get("/supported-components")
async def get_supported_components():
    """Get list of supported component types and their capabilities."""
    return {
        "components": [
            {
                "type": "pie-chart",
                "name": "Pie Chart",
                "description": "Display percentage-based data as circular segments",
                "best_for": ["market share", "demographics", "survey results", "categorical percentages"],
                "markdown_syntax": ":::pie-chart"
            },
            {
                "type": "bar-chart",
                "name": "Bar Chart",
                "description": "Compare quantities across different categories",
                "best_for": ["performance metrics", "comparisons", "rankings", "time-based comparisons"],
                "markdown_syntax": ":::bar-chart"
            },
            {
                "type": "line-chart",
                "name": "Line Chart",
                "description": "Show trends and changes over time",
                "best_for": ["time series data", "growth trends", "performance tracking", "progression analysis"],
                "markdown_syntax": ":::line-chart"
            },
            {
                "type": "data-table",
                "name": "Data Table",
                "description": "Present structured data with sorting, filtering, and pagination",
                "best_for": ["detailed datasets", "comparison tables", "lists with multiple attributes"],
                "markdown_syntax": ":::data-table"
            }
        ],
        "total_components": 4,
        "version": "1.0.0"
    }
