#!/bin/bash

# Digi Setu AI Development Startup Script

echo "🚀 Starting Digi Setu AI Development Environment"
echo "================================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the digi-setu-demo root directory"
    exit 1
fi

# Create .env files if they don't exist
echo "📝 Setting up environment variables..."

# Set environment variables for backend
export OPENAI_API_KEY="REDACTED_SEE_ENV_FILE"
export GROK_API_KEY="REDACTED_SEE_ENV_FILE"
export ANTHROPIC_API_KEY="REDACTED_SEE_ENV_FILE"
export ENVIRONMENT="development"
export DEBUG="true"
echo "✅ Environment variables set"

# Frontend .env
if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << EOF
NUXT_PUBLIC_API_BASE=http://localhost:8000/api
EOF
    echo "✅ Created frontend/.env"
else
    echo "✅ frontend/.env already exists"
fi

echo ""
echo "🐍 Setting up Python backend..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting FastAPI backend server on http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000"
echo ""

# Start backend in background
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Switch to frontend
cd ../frontend

echo "🎨 Setting up Node.js frontend..."
echo "📥 Installing Node.js dependencies..."
npm install

echo ""
echo "🚀 Starting Nuxt 3 frontend server on http://localhost:3000"
echo ""

# Start frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Digi Setu AI is now running!"
echo "================================"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap 'echo ""; echo "🛑 Shutting down servers..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT
wait
