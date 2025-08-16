#!/bin/bash

# Digi Setu AI - Development Startup Script

echo "🚀 Starting Digi Setu AI Development Environment"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Backend .env file not found. Creating from example..."
    cp backend/env.example backend/.env
    echo "✅ Created backend/.env - Please update with your API keys!"
fi

# Check if frontend .env file exists
if [ ! -f "frontend/.env" ]; then
    echo "⚠️  Frontend .env file not found. Creating..."
    cat > frontend/.env << EOF
# Digi Setu AI Frontend Configuration
NUXT_PUBLIC_API_BASE=http://localhost:8000
NUXT_PUBLIC_APP_NAME=Digi Setu AI
NUXT_PUBLIC_APP_VERSION=2.0.0
EOF
    echo "✅ Created frontend/.env"
fi

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose up -d postgres redis

echo "⏳ Waiting for database to be ready..."
sleep 5

echo "🔧 Installing backend dependencies..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "🗄️  Setting up database..."
cd backend
source venv/bin/activate
# Run database migrations here when Alembic is set up
# alembic upgrade head
cd ..

echo "🎉 Development environment is ready!"
echo ""
echo "To start the applications:"
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Access points:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔧 Backend API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo "  🗄️  Database: localhost:5432 (postgres/password)"
echo "  🔴 Redis: localhost:6379"
echo ""
echo "Don't forget to:"
echo "  1. Update backend/.env with your AI API keys"
echo "  2. Set up your database credentials"
echo "  3. Configure any additional settings"
echo ""
echo "Happy coding! 🎯"
