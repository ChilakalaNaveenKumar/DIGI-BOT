#!/usr/bin/env python3
"""
Vector Database Setup Script

Sets up the vector database tables and indexes for Digi Setu AI.
Run this script after setting up the main database.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import get_settings

logger = structlog.get_logger(__name__)


async def setup_vector_database():
    """Set up vector database tables and indexes."""
    
    try:
        settings = get_settings()
        
        # Create database engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True
        )
        
        logger.info("Starting vector database setup...")
        
        # Read the SQL setup file
        sql_file = project_root / "vector_database_setup.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL setup file not found: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        # Execute the SQL setup - each statement in its own transaction
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement and not statement.startswith('--') and not statement.startswith('/*'):
                try:
                    logger.info(f"Executing statement {i+1}/{len(statements)}")
                    async with engine.begin() as conn:
                        await conn.execute(text(statement))
                except Exception as e:
                    logger.warning(f"Statement {i+1} failed (may be expected): {str(e)}")
                    continue
        
        logger.info("✅ Vector database setup completed successfully!")
        
        # Test the setup
        await test_vector_setup(engine)
        
    except Exception as e:
        logger.error("❌ Vector database setup failed", error=str(e))
        raise
    finally:
        await engine.dispose()


async def test_vector_setup(engine):
    """Test that vector tables were created successfully."""
    
    try:
        logger.info("Testing vector database setup...")
        
        async with engine.begin() as conn:
            # Test that tables exist
            tables_to_check = [
                'message_vectors',
                'conversation_summaries', 
                'attachments',
                'attachment_vectors',
                'message_attachments'
            ]
            
            for table in tables_to_check:
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """))
                exists = result.scalar()
                
                if exists:
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.error(f"❌ Table '{table}' missing")
                    raise Exception(f"Table {table} was not created")
            
            # Test vector extension
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM pg_extension 
                    WHERE extname = 'vector'
                );
            """))
            vector_exists = result.scalar()
            
            if vector_exists:
                logger.info("✅ pgvector extension is installed")
            else:
                logger.error("❌ pgvector extension is missing")
                raise Exception("pgvector extension not found")
        
        logger.info("✅ All vector database tests passed!")
        
    except Exception as e:
        logger.error("❌ Vector database test failed", error=str(e))
        raise


async def main():
    """Main setup function."""
    
    try:
        logger.info("🚀 Starting Digi Setu AI Vector Database Setup")
        
        # Check environment
        settings = get_settings()
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL not configured")
        
        if not settings.OPENAI_API_KEY:
            logger.warning("⚠️  OPENAI_API_KEY not configured - vector embeddings will fail")
        
        logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
        
        # Setup vector database
        await setup_vector_database()
        
        logger.info("🎉 Vector database setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start the application: python main.py")
        logger.info("2. Test vector search: POST /api/vector/search")
        logger.info("3. Check vector stats: GET /api/vector/stats")
        
    except Exception as e:
        logger.error("💥 Setup failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
