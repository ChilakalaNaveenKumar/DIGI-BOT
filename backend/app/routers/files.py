"""
Files Router

Handles file serving, management, and user file operations.
"""

import os
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.dev_auth import get_current_user
from app.core.database import get_db_session
from app.models.user import User
from app.services.file_service import FileService
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/files", tags=["Files"])


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify files router is working."""
    return {
        "message": "Files router is working",
        "service": "files"
    }


@router.get("/{file_id}")
async def serve_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Serve a file by its ID."""
    try:
        file_service = FileService()
        
        # Get file from database
        from sqlalchemy import select
        from app.models.file import File
        
        result = await db.execute(
            select(File).where(File.file_id == file_id)
        )
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if user owns the file
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists on disk
        file_path = Path(file_record.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Serve the file
        return FileResponse(
            path=str(file_path),
            filename=file_record.original_filename,
            media_type=file_record.content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to serve file", file_id=file_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to serve file")


@router.get("/")
async def get_user_files(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    file_type: Optional[str] = Query(None, description="Filter by file type (audio, image, document)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's files."""
    try:
        file_service = FileService()
        files = await file_service.get_user_files(
            user_id=current_user.id,
            db=db,
            file_type=file_type,
            limit=limit,
            offset=offset
        )
        
        return {
            "files": [file.to_dict() for file in files],
            "total": len(files),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error("Failed to get user files", error=str(e))
        raise DigiSetuException(
            status_code=500,
            error_code="FILE_FETCH_ERROR",
            message="Failed to fetch user files"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a file."""
    try:
        from sqlalchemy import select, delete
        from app.models.file import File
        
        # Get file from database
        result = await db.execute(
            select(File).where(File.file_id == file_id)
        )
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if user owns the file
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete file from disk
        file_path = Path(file_record.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        await db.execute(
            delete(File).where(File.file_id == file_id)
        )
        await db.commit()
        
        logger.info("File deleted", file_id=file_id, user_id=current_user.id)
        
        return {"message": "File deleted successfully", "file_id": file_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete file", file_id=file_id, error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete file")


@router.get("/stats/summary")
async def get_file_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get file statistics for the user."""
    try:
        from sqlalchemy import select, func
        from app.models.file import File
        
        # Get file counts by type
        result = await db.execute(
            select(
                func.substr(File.content_type, 1, func.instr(File.content_type, '/') - 1).label('type'),
                func.count().label('count'),
                func.sum(File.file_size).label('total_size')
            )
            .where(File.user_id == current_user.id)
            .group_by(func.substr(File.content_type, 1, func.instr(File.content_type, '/') - 1))
        )
        
        stats_by_type = {}
        total_files = 0
        total_size = 0
        
        for row in result:
            file_type = row.type or 'other'
            count = row.count
            size = row.total_size or 0
            
            stats_by_type[file_type] = {
                "count": count,
                "size": size
            }
            total_files += count
            total_size += size
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_type": stats_by_type
        }
        
    except Exception as e:
        logger.error("Failed to get file stats", error=str(e))
        raise DigiSetuException(
            status_code=500,
            error_code="FILE_STATS_ERROR",
            message="Failed to get file statistics"
        )

