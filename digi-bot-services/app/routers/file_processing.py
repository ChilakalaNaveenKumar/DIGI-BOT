"""
File Processing API Router
Provides comprehensive file processing capabilities including analysis, text extraction, and vector store management
"""

from __future__ import annotations
import os
import tempfile
import json
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import structlog
import aiofiles

from app.services.auth.core.auth_deps import get_current_user_required
from app.services.file_processing import FileAnalyzer, AnalyzeLimits, AnalyzeResult, VectorStoreSaver, TextVectorSaver
from app.services.file_processing.user_vector_store import UserVectorStoreManager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/files", tags=["file-processing"])


class AnalysisLimitsRequest(BaseModel):
    max_bytes: int = Field(25 * 1024 * 1024, description="Maximum file size in bytes")
    max_pdf_pages: int = Field(1000, description="Maximum PDF pages to process")
    max_slides: int = Field(1000, description="Maximum presentation slides to process")
    max_cells: int = Field(200000, description="Maximum spreadsheet cells to process")
    ocr_enabled: bool = Field(False, description="Enable OCR for image text extraction")


class VectorStoreRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name for the vector store")
    expires_after: Optional[Dict[str, int]] = Field(None, description="Expiration settings")
    chunking_strategy: Optional[Dict[str, Any]] = Field(None, description="Text chunking strategy")


class TextVectorRequest(BaseModel):
    text: str = Field(..., description="Text content to add to vector store")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    filename: Optional[str] = Field(None, description="Original filename")


class FileProcessingRouter:
    """Router for file processing with analysis and vector store management"""
    
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        self.vector_saver = VectorStoreSaver()
        self.text_vector_saver = TextVectorSaver()
        self.user_vector_manager = UserVectorStoreManager()
    
    async def initialize(self):
        """Initialize file processing clients"""
        try:
            await self.vector_saver.initialize()
            await self.text_vector_saver.initialize()
            logger.info("File processing router initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize file processing router", error=str(e))
            raise


# Global router instance
file_router = FileProcessingRouter()


@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(..., description="File to analyze"),
    max_bytes: int = Form(25 * 1024 * 1024, description="Maximum file size in bytes"),
    max_pdf_pages: int = Form(1000, description="Maximum PDF pages to process"),
    max_slides: int = Form(1000, description="Maximum presentation slides to process"),
    max_cells: int = Form(200000, description="Maximum spreadsheet cells to process"),
    ocr_enabled: bool = Form(False, description="Enable OCR for image text extraction"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Analyze and extract text from uploaded file
    
    Supports various file formats:
    - Text: .txt, .md, .csv, .tsv, .json, .log
    - Documents: .pdf, .docx, .pptx, .xlsx
    - Code: .py, .js, .ts, .html, .css, .java, .c, .cpp, .go, .rs, .sh, .sql, .yaml, .yml, .xml
    - Images: .png, .jpg, .jpeg, .webp (with optional OCR)
    """
    
    try:
        # Validate file size
        if file.size and file.size > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_bytes} bytes."
            )
        
        # Create analysis limits
        limits = AnalyzeLimits(
            max_bytes=max_bytes,
            max_pdf_pages=max_pdf_pages,
            max_slides=max_slides,
            max_cells=max_cells,
            ocr_enabled=ocr_enabled
        )
        
        # Log the request
        logger.info(
            "File analysis request",
            user_id=current_user["id"],
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            ocr_enabled=ocr_enabled
        )
        
        # Save uploaded file temporarily
        temp_file = None
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename or "file.txt")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Analyze the file
            result = await file_router.file_analyzer.analyze_file(temp_path, limits)
            
            logger.info(
                "File analysis completed",
                user_id=current_user["id"],
                filename=file.filename,
                success=result.success,
                text_length=len(result.text) if result.text else 0,
                pages_processed=result.pages_processed,
                error=result.error
            )
            
            # Convert result to dict for JSON response
            result_dict = {
                "success": result.success,
                "filename": file.filename,
                "file_type": result.file_type,
                "text": result.text,
                "metadata": result.metadata,
                "pages_processed": result.pages_processed,
                "cells_processed": result.cells_processed,
                "error": result.error,
                "processing_time": result.processing_time,
                "file_size": file.size,
                "limits_used": {
                    "max_bytes": limits.max_bytes,
                    "max_pdf_pages": limits.max_pdf_pages,
                    "max_slides": limits.max_slides,
                    "max_cells": limits.max_cells,
                    "ocr_enabled": limits.ocr_enabled
                }
            }
            
            return result_dict
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "File analysis error",
            user_id=current_user["id"],
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"File analysis failed: {str(e)}"
        )


@router.post("/analyze-batch")
async def analyze_files_batch(
    files: List[UploadFile] = File(..., description="Files to analyze"),
    limits: AnalysisLimitsRequest = Depends(),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Analyze multiple files in batch
    
    Processes multiple files and returns analysis results for each.
    Useful for bulk document processing.
    """
    
    try:
        if len(files) > 10:  # Reasonable batch limit
            raise HTTPException(
                status_code=400,
                detail="Too many files. Maximum 10 files per batch."
            )
        
        # Create analysis limits
        analyze_limits = AnalyzeLimits(
            max_bytes=limits.max_bytes,
            max_pdf_pages=limits.max_pdf_pages,
            max_slides=limits.max_slides,
            max_cells=limits.max_cells,
            ocr_enabled=limits.ocr_enabled
        )
        
        logger.info(
            "Batch file analysis request",
            user_id=current_user["id"],
            file_count=len(files),
            filenames=[f.filename for f in files]
        )
        
        results = []
        temp_files = []
        
        try:
            # Process each file
            for file in files:
                # Validate file size
                if file.size and file.size > limits.max_bytes:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": f"File too large. Maximum size is {limits.max_bytes} bytes.",
                        "file_size": file.size
                    })
                    continue
                
                # Create temporary file
                suffix = os.path.splitext(file.filename or "file.txt")[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_path = temp_file.name
                    temp_files.append(temp_path)
                
                # Analyze the file
                try:
                    result = await file_router.file_analyzer.analyze_file(temp_path, analyze_limits)
                    
                    result_dict = {
                        "filename": file.filename,
                        "success": result.success,
                        "file_type": result.file_type,
                        "text": result.text,
                        "metadata": result.metadata,
                        "pages_processed": result.pages_processed,
                        "cells_processed": result.cells_processed,
                        "error": result.error,
                        "processing_time": result.processing_time,
                        "file_size": file.size
                    }
                    
                    results.append(result_dict)
                    
                except Exception as e:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": str(e),
                        "file_size": file.size
                    })
            
            logger.info(
                "Batch file analysis completed",
                user_id=current_user["id"],
                total_files=len(files),
                successful=sum(1 for r in results if r.get("success")),
                failed=sum(1 for r in results if not r.get("success"))
            )
            
            return {
                "success": True,
                "total_files": len(files),
                "results": results,
                "limits_used": {
                    "max_bytes": limits.max_bytes,
                    "max_pdf_pages": limits.max_pdf_pages,
                    "max_slides": limits.max_slides,
                    "max_cells": limits.max_cells,
                    "ocr_enabled": limits.ocr_enabled
                }
            }
            
        finally:
            # Clean up temporary files
            for temp_path in temp_files:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "Batch file analysis error",
            user_id=current_user["id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Batch file analysis failed: {str(e)}"
        )


@router.post("/vector-store/create")
async def create_vector_store(
    request: VectorStoreRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Create a new vector store for file storage
    
    Creates a vector store that can be used to store and search files.
    """
    
    try:
        # Initialize if needed
        if not file_router.vector_saver._initialized:
            await file_router.initialize()
        
        logger.info(
            "Vector store creation request",
            user_id=current_user["id"],
            name=request.name
        )
        
        # Create vector store
        vector_store = await file_router.vector_saver.create_vector_store(
            name=request.name,
            expires_after=request.expires_after,
            chunking_strategy=request.chunking_strategy
        )
        
        logger.info(
            "Vector store created",
            user_id=current_user["id"],
            vector_store_id=vector_store.id,
            name=vector_store.name
        )
        
        return {
            "success": True,
            "vector_store": {
                "id": vector_store.id,
                "name": vector_store.name,
                "status": vector_store.status,
                "created_at": vector_store.created_at,
                "file_counts": vector_store.file_counts,
                "expires_after": vector_store.expires_after
            }
        }
        
    except Exception as e:
        logger.error(
            "Vector store creation error",
            user_id=current_user["id"],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector store creation failed: {str(e)}"
        )


@router.post("/vector-store/{vector_store_id}/upload")
async def upload_to_vector_store(
    vector_store_id: str,
    file: UploadFile = File(..., description="File to upload to vector store"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Upload file to existing vector store
    
    Uploads and processes a file into the specified vector store for semantic search.
    """
    
    try:
        # Initialize if needed
        if not file_router.vector_saver._initialized:
            await file_router.initialize()
        
        logger.info(
            "Vector store file upload request",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            filename=file.filename,
            file_size=file.size
        )
        
        # Save uploaded file temporarily
        temp_file = None
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename or "file.txt")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Upload to vector store
            vector_store_file = await file_router.vector_saver.upload_file(
                vector_store_id,
                temp_path,
                filename=file.filename
            )
            
            logger.info(
                "File uploaded to vector store",
                user_id=current_user["id"],
                vector_store_id=vector_store_id,
                file_id=vector_store_file.id,
                filename=file.filename
            )
            
            return {
                "success": True,
                "vector_store_id": vector_store_id,
                "file": {
                    "id": vector_store_file.id,
                    "filename": vector_store_file.filename,
                    "status": vector_store_file.status,
                    "created_at": vector_store_file.created_at,
                    "chunking_strategy": vector_store_file.chunking_strategy
                }
            }
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "Vector store file upload error",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector store file upload failed: {str(e)}"
        )


@router.post("/upload-for-chat")
async def upload_file_for_chat(
    file: UploadFile = File(..., description="File to upload for chat"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Upload a file to the user's personal vector store for chat functionality.
    This creates a user-specific vector store and uploads the file for file-aware chat.
    """
    try:
        user_id = current_user["id"]
        
        # Validate file size (25MB limit)
        max_size = 25 * 1024 * 1024
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_size} bytes."
            )
        
        # Save uploaded file temporarily
        temp_file = None
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename or "file.txt")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Upload to user's vector store
            result = await file_router.user_vector_manager.upload_file_to_user_store(
                user_id=user_id,
                file_path=temp_path,
                filename=file.filename
            )
            
            logger.info(
                "File uploaded for chat",
                user_id=user_id,
                filename=file.filename,
                file_id=result["file_id"],
                vector_store_id=result["vector_store_id"]
            )
            
            return {
                "success": True,
                "file": {
                    "id": result["file_id"],
                    "filename": result["filename"],
                    "vector_store_id": result["vector_store_id"],
                    "vector_store_file_id": result["vector_store_file_id"],
                    "status": result["status"]
                },
                "message": "File uploaded successfully and ready for chat"
            }
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "Chat file upload error",
            user_id=current_user["id"],
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/my-files")
async def get_user_files(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Get all files uploaded by the current user for chat functionality.
    """
    try:
        user_id = current_user["id"]
        files = await file_router.user_vector_manager.list_user_files(user_id)
        
        return {
            "success": True,
            "files": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error("Failed to get user files", user_id=current_user["id"], error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve files: {str(e)}"
        )


@router.delete("/my-files/{file_id}")
async def delete_user_file(
    file_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Delete a file from the user's vector store.
    """
    try:
        user_id = current_user["id"]
        success = await file_router.user_vector_manager.delete_user_file(user_id, file_id)
        
        if success:
            return {
                "success": True,
                "message": "File deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="File not found or could not be deleted"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete user file", user_id=current_user["id"], file_id=file_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/my-vector-store/stats")
async def get_user_vector_store_stats(
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Get statistics about the user's vector store.
    """
    try:
        user_id = current_user["id"]
        stats = await file_router.user_vector_manager.get_store_stats(user_id)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error("Failed to get vector store stats", user_id=current_user["id"], error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.post("/vector-store/{vector_store_id}/add-text")
async def add_text_to_vector_store(
    vector_store_id: str,
    request: TextVectorRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Add text content directly to vector store
    
    Adds text content to the vector store without requiring a file upload.
    """
    
    try:
        # Initialize if needed
        if not file_router.text_vector_saver._initialized:
            await file_router.initialize()
        
        logger.info(
            "Vector store text addition request",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            text_length=len(request.text),
            filename=request.filename
        )
        
        # Add text to vector store
        result = await file_router.text_vector_saver.add_text_to_vector_store(
            vector_store_id,
            request.text,
            metadata=request.metadata,
            filename=request.filename
        )
        
        logger.info(
            "Text added to vector store",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            result=result
        )
        
        return {
            "success": True,
            "vector_store_id": vector_store_id,
            "text_length": len(request.text),
            "filename": request.filename,
            "metadata": request.metadata,
            "result": result
        }
        
    except Exception as e:
        logger.error(
            "Vector store text addition error",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector store text addition failed: {str(e)}"
        )


@router.get("/vector-store/{vector_store_id}")
async def get_vector_store(
    vector_store_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Get vector store information
    
    Retrieves details about a specific vector store including file counts and status.
    """
    
    try:
        # Initialize if needed
        if not file_router.vector_saver._initialized:
            await file_router.initialize()
        
        # Get vector store info
        vector_store = await file_router.vector_saver.get_vector_store(vector_store_id)
        
        logger.info(
            "Vector store info retrieved",
            user_id=current_user["id"],
            vector_store_id=vector_store_id
        )
        
        return {
            "success": True,
            "vector_store": {
                "id": vector_store.id,
                "name": vector_store.name,
                "status": vector_store.status,
                "created_at": vector_store.created_at,
                "file_counts": vector_store.file_counts,
                "expires_after": vector_store.expires_after,
                "usage_bytes": vector_store.usage_bytes
            }
        }
        
    except Exception as e:
        logger.error(
            "Vector store info retrieval error",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector store info retrieval failed: {str(e)}"
        )


@router.get("/vector-store/{vector_store_id}/files")
async def list_vector_store_files(
    vector_store_id: str,
    limit: int = Query(20, description="Number of files to return"),
    order: str = Query("desc", description="Order: asc or desc"),
    after: Optional[str] = Query(None, description="Pagination cursor"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    List files in vector store
    
    Returns a paginated list of files in the specified vector store.
    """
    
    try:
        # Initialize if needed
        if not file_router.vector_saver._initialized:
            await file_router.initialize()
        
        # List files
        files_response = await file_router.vector_saver.list_files(
            vector_store_id,
            limit=limit,
            order=order,
            after=after
        )
        
        logger.info(
            "Vector store files listed",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            file_count=len(files_response.data)
        )
        
        return {
            "success": True,
            "vector_store_id": vector_store_id,
            "files": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "status": f.status,
                    "created_at": f.created_at,
                    "chunking_strategy": f.chunking_strategy
                }
                for f in files_response.data
            ],
            "has_more": files_response.has_more,
            "first_id": files_response.first_id,
            "last_id": files_response.last_id
        }
        
    except Exception as e:
        logger.error(
            "Vector store files listing error",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector store files listing failed: {str(e)}"
        )


@router.delete("/vector-store/{vector_store_id}")
async def delete_vector_store(
    vector_store_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Delete vector store
    
    Permanently deletes a vector store and all its files.
    """
    
    try:
        # Initialize if needed
        if not file_router.vector_saver._initialized:
            await file_router.initialize()
        
        logger.info(
            "Vector store deletion request",
            user_id=current_user["id"],
            vector_store_id=vector_store_id
        )
        
        # Delete vector store
        result = await file_router.vector_saver.delete_vector_store(vector_store_id)
        
        logger.info(
            "Vector store deleted",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            result=result
        )
        
        return {
            "success": True,
            "vector_store_id": vector_store_id,
            "deleted": result
        }
        
    except Exception as e:
        logger.error(
            "Vector store deletion error",
            user_id=current_user["id"],
            vector_store_id=vector_store_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Vector store deletion failed: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get list of supported file formats
    
    Returns information about supported file types and their capabilities.
    """
    
    return {
        "success": True,
        "supported_formats": {
            "text_files": [".txt", ".md", ".csv", ".tsv", ".json", ".log"],
            "documents": [".pdf", ".docx", ".pptx", ".xlsx"],
            "code_files": [".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".go", ".rs", ".sh", ".sql", ".yaml", ".yml", ".xml"],
            "images": [".png", ".jpg", ".jpeg", ".webp"],
            "capabilities": {
                "ocr": "Available for image files",
                "max_file_size": "25MB (configurable)",
                "batch_processing": "Up to 10 files",
                "vector_storage": "OpenAI vector stores"
            }
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for file processing service"""
    try:
        return {
            "status": "healthy",
            "service": "file-processing",
            "vector_saver_initialized": file_router.vector_saver._initialized if hasattr(file_router.vector_saver, '_initialized') else False,
            "text_vector_saver_initialized": file_router.text_vector_saver._initialized if hasattr(file_router.text_vector_saver, '_initialized') else False
        }
    except Exception as e:
        logger.error("File processing health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Export the router
__all__ = ["router"]
