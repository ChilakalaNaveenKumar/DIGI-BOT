"""
Database Initialization Script for Digi Bot Services

Creates all tables and sets up the database.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.database import init_db
from app.models import User, Conversation, Message, MessagePart, File

async def main():
    """Initialize the database with all tables."""
    print("🔧 Initializing Digi Bot Services Database...")
    
    try:
        await init_db()
        print("✅ Database initialized successfully!")
        print("📊 Created tables:")
        print("   - users")
        print("   - conversations") 
        print("   - messages")
        print("   - message_parts")
        print("   - files")
        print("\n🚀 Ready to start Digi Bot Services!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

