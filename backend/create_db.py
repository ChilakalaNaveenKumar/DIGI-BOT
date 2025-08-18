#!/usr/bin/env python3
"""
Database initialization script
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db
from app.models import *  # Import all models

async def main():
    """Initialize the database with all tables."""
    print("Initializing database...")
    try:
        await init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
