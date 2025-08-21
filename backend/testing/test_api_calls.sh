#!/bin/bash

# Test API Calls - Isolated Testing
# This script tests the actual API endpoints to see token consumption

echo "🧪 Testing API Calls - Token Analysis"
echo "======================================"

# Check if backend is running
echo "Checking if backend is running on port 8000..."
if ! curl -s http://localhost:8000/api/chat/test > /dev/null; then
    echo "❌ Backend not running. Start it first:"
    echo "cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000"
    exit 1
fi

echo "✅ Backend is running"

# Test 1: Simple question via main chat endpoint
echo ""
echo "--- Test 1: Simple Question via Main Chat ---"
echo "Testing: 'What is 2+2?'"

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "What is 2+2?"
      }
    ]
  }' \
  --no-buffer \
  -v 2>&1 | head -50

echo ""
echo "--- Test 2: Orchestrator Stream Endpoint ---"
echo "Testing: 'Explain Python in 20 words'"

curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-token" \
  -d '{
    "message": "Explain Python in 20 words",
    "conversation_id": null,
    "user_preferences": null
  }' \
  --no-buffer \
  -v 2>&1 | head -30

echo ""
echo "--- Test 3: Check Logs After Tests ---"
echo "Recent API calls from logs:"

if [ -f "logs/api_counts.log" ]; then
    echo "Last 5 API calls:"
    tail -5 logs/api_counts.log
else
    echo "No API logs found"
fi

echo ""
echo "Test completed. Check the responses above for:"
echo "1. How many API calls were made"
echo "2. Token usage in responses"
echo "3. Response structure and metadata"
