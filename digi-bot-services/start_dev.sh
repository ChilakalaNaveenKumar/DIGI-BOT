#!/bin/bash

# Digi Bot Services - Development Startup Script
# Sets the required environment variables and starts the server

echo "🚀 Starting Digi Bot Services (Development Mode)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set required environment variables
export GOOGLE_CLIENT_ID="505944872695-1s09bpf3ljaal6omfm5cuu4o1jc32b7v.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="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"
export GOOGLE_REDIRECT_URI="http://localhost:8000/auth/callback"
export ANTHROPIC_API_KEY="sk-ant-api03-dummy-key-for-development"
export ENVIRONMENT="development"
export DEBUG="true"
export HOST="0.0.0.0"
export PORT="8000"
export DATABASE_URL="postgresql+asyncpg://digi_setu_user:secure_password_2024!@localhost/digi_setu_ai"

# Initialize database (PostgreSQL)
echo "🔧 Ensuring PostgreSQL database is ready..."
python create_db.py

# Start the server
echo "🌟 Starting Digi Bot Services on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔐 Health Check: http://localhost:8000/"
echo "🔑 Google OAuth URL: http://localhost:8000/auth/google/url"
echo ""
echo "Press Ctrl+C to stop the server"

python main.py



