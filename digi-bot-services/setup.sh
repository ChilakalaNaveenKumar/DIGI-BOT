#!/bin/bash
echo "🚀 Setting up Digi Bot Authentication Service..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo "⚙️  Setting up environment..."
cp env.example .env

# Extract Google OAuth credentials
echo "🔑 Extracting Google OAuth credentials..."
if [ -f "client_secret_505944872695-1s09bpf3ljaal6omfm5cuu4o1jc32b7v.apps.googleusercontent.com.json" ]; then
    GOOGLE_CLIENT_ID=$(python3 -c "
import json
with open('client_secret_505944872695-1s09bpf3ljaal6omfm5cuu4o1jc32b7v.apps.googleusercontent.com.json', 'r') as f:
    data = json.load(f)
    print(data['web']['client_id'])
")
    
    GOOGLE_CLIENT_SECRET=$(python3 -c "
import json
with open('client_secret_505944872695-1s09bpf3ljaal6omfm5cuu4o1jc32b7v.apps.googleusercontent.com.json', 'r') as f:
    data = json.load(f)
    print(data['web']['client_secret'])
")
    
    # Update .env file
    sed -i.bak "s/GOOGLE_CLIENT_ID=.*/GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID/" .env
    sed -i.bak "s/GOOGLE_CLIENT_SECRET=.*/GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET/" .env
    rm .env.bak
    
    echo "✅ Google OAuth credentials configured"
else
    echo "⚠️  Google OAuth credentials file not found"
fi

echo "✅ Setup complete!"
echo ""
echo "To start the authentication service:"
echo "  cd digi-bot-services"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "The service will run on: http://localhost:8000"
