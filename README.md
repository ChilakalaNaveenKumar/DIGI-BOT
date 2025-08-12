# 🧠 Digi Bot - AI-Powered Educational Content Platform

A modern, multi-AI provider chat application built with **Nuxt 3** (frontend) and **Python FastAPI** (backend). Transform static content into interactive learning experiences with the power of GPT-4, Grok, and Claude.

## ✨ Features

### 🤖 **Multi-AI Provider Support**
- **GPT-4** (OpenAI) - Advanced reasoning and content generation
- **Grok** (X.AI) - Real-time information and analysis
- **Claude** (Anthropic) - Thoughtful and nuanced responses

### 🎨 **Beautiful User Interface**
- **Modern gradient design** with smooth animations
- **Responsive layout** that works on all devices
- **Enhanced message bubbles** with markdown support
- **Thinking indicators** showing AI processing
- **File upload** with drag-and-drop support
- **Quick action buttons** for common tasks

### 🚀 **Advanced Features**
- **Markdown rendering** with syntax highlighting
- **Code block highlighting** for technical content
- **File processing** (images, PDFs, documents)
- **Message actions** (copy, regenerate, export, like)
- **Smooth scrolling** and animations
- **Real-time provider switching**

## 🏗️ Project Structure

```
digi-bot/
├── frontend/                 # Nuxt 3 Vue.js application
│   ├── components/
│   │   ├── Chat/            # Chat-related components
│   │   │   ├── ChatContainer.vue
│   │   │   ├── MessageBubble.vue
│   │   │   ├── ChatInput.vue
│   │   │   ├── ThinkingIndicator.vue
│   │   │   └── MarkdownRenderer.vue
│   │   └── UI/              # Reusable UI components
│   ├── pages/               # Nuxt pages
│   ├── assets/              # CSS and static assets
│   └── nuxt.config.ts       # Nuxt configuration
│
├── backend/                 # Python FastAPI application
│   ├── main.py              # FastAPI app entry point
│   ├── routers/             # API route handlers
│   │   └── chat.py          # Chat endpoints
│   ├── services/            # AI provider services
│   │   ├── openai_service.py
│   │   ├── grok_service.py
│   │   └── anthropic_service.py
│   ├── models/              # Pydantic models
│   └── requirements.txt     # Python dependencies
│
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.8+
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/[your-username]/digi-bot.git
cd digi-bot
```

### 2. Backend Setup (Python FastAPI)
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file from example
cp .env.example .env

# Edit .env file and add your API keys:
# OPENAI_API_KEY=your_actual_openai_api_key_here
# GROK_API_KEY=your_actual_grok_api_key_here
# ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here

# Start the backend server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup (Nuxt 3)
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NUXT_PUBLIC_API_BASE=http://localhost:8000/api" > .env

# Start the development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env or export)
```bash
OPENAI_API_KEY=your_openai_api_key_here
GROK_API_KEY=your_grok_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ENVIRONMENT=development
DEBUG=true
```

#### Frontend (.env)
```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000/api
```

## 🎯 API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send message to AI provider
- `GET /api/providers` - Get available AI providers
- `GET /api/test/{provider}` - Test AI provider connection

### Example API Usage
```javascript
// Send a chat message
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Explain photosynthesis' }
    ],
    provider: 'openai'
  })
})
```

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Development
```bash
cd backend
uvicorn main:app --reload --port 8000    # Development server
python -m pytest                         # Run tests (when added)
```

## 🎨 UI Components

### Chat Components
- **ChatContainer** - Main chat layout with header and footer
- **MessageBubble** - Individual message display with actions
- **ChatInput** - Enhanced input with file upload and quick actions
- **ThinkingIndicator** - AI processing visualization
- **MarkdownRenderer** - Render markdown with syntax highlighting

### UI Components
- **ProviderSelector** - AI provider switching dropdown
- **FilePreview** - File upload preview component

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use `.env` files for local development
- **CORS**: Backend configured for localhost development
- **File Uploads**: Limited file types and sizes for security

## 📦 Dependencies

### Frontend (Nuxt 3)
- **Nuxt 3** - Vue.js framework
- **Tailwind CSS** - Utility-first CSS framework
- **@nuxtjs/tailwindcss** - Nuxt Tailwind integration
- **@tailwindcss/typography** - Typography plugin
- **marked** - Markdown parser
- **highlight.js** - Syntax highlighting
- **lucide-vue-next** - Modern icons
- **@vueuse/core** - Vue composition utilities

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **OpenAI** - OpenAI API client
- **Anthropic** - Anthropic API client
- **Pydantic** - Data validation
- **python-dotenv** - Environment variable management

## 🚀 Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy the .output directory
```

### Backend (Railway/Render/Heroku)
```bash
cd backend
# Set environment variables in your deployment platform
# Deploy with: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Anthropic** for Claude API
- **X.AI** for Grok API
- **Nuxt.js** team for the amazing framework
- **FastAPI** team for the excellent Python framework
- **Tailwind CSS** for beautiful styling

---

**Built with ❤️ using modern web technologies**

For support or questions, please open an issue in this repository.