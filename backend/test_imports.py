#!/usr/bin/env python3
"""
Test script to validate all imports work correctly
"""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a module and report results."""
    try:
        __import__(module_name)
        print(f"✓ {description}")
        return True
    except Exception as e:
        print(f"✗ {description}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("Testing Backend Imports")
    print("=" * 30)
    
    tests = [
        ("app.core.config", "Core Configuration"),
        ("app.core.database", "Database Configuration"),
        ("app.core.exceptions", "Custom Exceptions"),
        ("app.core.logging", "Logging Setup"),
        ("app.core.middleware", "Middleware"),
        ("app.models.user", "User Model"),
        ("app.models.project", "Project Model"),
        ("app.models.conversation", "Conversation Model"),
        ("app.models.file", "File Model"),
        ("app.services.conversation_service", "Conversation Service"),
        ("app.services.auth_service", "Auth Service"),
        ("app.services.file_service", "File Service"),
        ("app.services.ai_providers.openai_provider", "OpenAI Provider"),
        ("app.routers.ai_chat", "AI Chat Router"),
        ("app.schemas.chat", "Chat Schemas"),
    ]
    
    passed = 0
    total = len(tests)
    
    for module, description in tests:
        if test_import(module, description):
            passed += 1
    
    print("\n" + "=" * 30)
    print(f"Results: {passed}/{total} imports successful")
    
    if passed == total:
        print("✓ All imports working! Server should start successfully.")
        return 0
    else:
        print("✗ Some imports failed. Fix these before starting the server.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
