#!/usr/bin/env python3
"""
Test script to verify Digi Setu AI setup
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python_version():
    """Check if Python 3.8+ is available"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_node_version():
    """Check if Node.js 18+ is available"""
    print("📦 Checking Node.js version...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_str = result.stdout.strip()
            version_num = int(version_str[1:].split('.')[0])  # Remove 'v' and get major version
            if version_num >= 18:
                print(f"✅ Node.js {version_str} - OK")
                return True
            else:
                print(f"❌ Node.js {version_str} - Need Node.js 18+")
                return False
        else:
            print("❌ Node.js not found")
            return False
    except Exception as e:
        print(f"❌ Error checking Node.js: {e}")
        return False

def check_project_structure():
    """Check if all required files exist"""
    print("📁 Checking project structure...")
    
    required_files = [
        "backend/main.py",
        "backend/requirements.txt",
        "backend/routers/chat.py",
        "backend/services/openai_service.py",
        "backend/services/grok_service.py",
        "backend/services/anthropic_service.py",
        "frontend/nuxt.config.ts",
        "frontend/package.json",
        "frontend/pages/index.vue",
        "frontend/components/ChatInterface.vue",
        "README.md",
        "start-dev.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_environment_setup():
    """Check if environment variables are configured"""
    print("🔧 Checking environment setup...")
    
    # Check for .env files or environment variables
    env_vars = ['OPENAI_API_KEY', 'GROK_API_KEY', 'ANTHROPIC_API_KEY']
    missing_vars = []
    
    for var in env_vars:
        if not os.getenv(var):
            # Check if it exists in backend/.env
            env_file = Path("backend/.env")
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                    if f"{var}=" not in content:
                        missing_vars.append(var)
            else:
                missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables (this is OK for testing):")
        for var in missing_vars:
            print(f"   - {var}")
        print("   You can add them to backend/.env when ready to test with real APIs")
    else:
        print("✅ Environment variables configured")
    
    return True

def test_backend_startup():
    """Test if backend can start (without API calls)"""
    print("🚀 Testing backend startup...")
    
    try:
        # Load environment variables from backend/.env
        from dotenv import load_dotenv
        load_dotenv('backend/.env')
        
        # Just try to import the main modules
        sys.path.insert(0, 'backend')
        
        # Test imports without initializing services
        import main
        from models.chat_models import ChatRequest, Message
        
        print("✅ Backend modules import successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Backend import error: {e}")
        print("   Try: cd backend && pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Digi Setu AI Setup Test")
    print("=" * 40)
    
    tests = [
        ("Python Version", check_python_version),
        ("Node.js Version", check_node_version),
        ("Project Structure", check_project_structure),
        ("Environment Setup", check_environment_setup),
        ("Backend Modules", test_backend_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Setup looks good! Ready to start development.")
        print("   Run: ./start-dev.sh")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("   See README.md for setup instructions.")

if __name__ == "__main__":
    main()
