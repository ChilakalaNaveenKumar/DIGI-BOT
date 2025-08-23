# 🚀 Digi Bot - AI-Powered Assistant Platform

A modern, production-ready AI assistant platform with Google OAuth authentication, multi-provider AI orchestration, and comprehensive chat functionality.

## ✨ Features

### 🔐 **Authentication & Security**
- **Google OAuth Integration**: Secure authentication with Google Sign-In
- **JWT Token Management**: Secure session handling with token refresh
- **Enhanced Security**: Rate limiting, CORS protection, and secure headers

### 🧠 **AI Orchestration**
- **Multi-Provider Support**: OpenAI (GPT-5, o3, o1), Anthropic (Claude 4), Grok (Grok-3)
- **Direct AI Streaming**: Real-time SSE responses with minimal overhead
- **Advanced Models**: Latest 2025 models with reasoning capabilities
- **Smart Provider Selection**: Automatic fallback and model optimization

### 💬 **Advanced Chat System**
- **Streaming Responses**: Real-time message streaming with Server-Sent Events
- **Conversation History**: Persistent chat history with PostgreSQL storage
- **File Upload Support**: Multi-modal content handling (images, documents, audio)
- **Message Management**: Complete CRUD operations for conversations
- **Tool Execution**: AI-powered chart generation and data table creation
- **Enhanced Content Parsing**: Automatic detection and rendering of specialized content

### 📊 **Data Visualization & Tools**
- **Chart.js Integration**: Interactive charts (pie, bar, line, scatter, bubble, radar)
- **ChartRenderer Component**: Dynamic chart creation from AI responses
- **Data Table Component**: Paginated, sortable tables with auto-header detection
- **Tool Registry**: Extensible system for AI tool execution
- **Component Renderer**: Smart parsing of AI-generated visualizations

### 📝 **Advanced Markdown Processing**
- **KaTeX Math Rendering**: Full LaTeX equation support with custom macros
- **Syntax Highlighting**: Code blocks with highlight.js (100+ languages)
- **Enhanced Markdown**: Task lists, footnotes, subscript/superscript, containers
- **AI Response Containers**: Info, warning, tip, danger styled blocks
- **Streaming Markdown**: Real-time rendering with cursor animation
- **Custom Plugins**: Abbreviations, definition lists, marked text

### 🎵 **Audio & Media Processing**
- **Whisper Integration**: OpenAI Whisper for audio transcription
- **Audio File Support**: Upload and process audio files
- **Generated Audio Storage**: Save AI-generated audio content
- **Image Processing**: PIL/Pillow for image handling
- **File Type Validation**: Secure file upload with type checking
- **Media Storage**: Organized file storage with database tracking

### 🎨 **Modern UI/UX**
- **Vue 3 + Nuxt 4**: Latest frontend framework with TypeScript
- **Tailwind CSS v4**: Modern styling with component system
- **Responsive Design**: Mobile-first approach with dark/light themes
- **Interactive Components**: Real-time chat interface with enhanced UX
- **Theme System**: Light/dark mode with smooth transitions
- **Component Auto-Import**: Organized component structure with prefixes

## 🏗️ Architecture

The project follows a **microservices architecture** with separate backend and frontend applications:

### Backend: `digi-bot-services/` (FastAPI + Python)
```
digi-bot-services/
├── app/
│   ├── core/                 # Core configuration and database
│   │   ├── config.py         # Application settings
│   │   ├── database.py       # PostgreSQL connection
│   │   ├── security.py       # Authentication & JWT
│   │   └── exceptions.py     # Custom exception handling
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py          # User model with Google OAuth
│   │   ├── conversation.py   # Chat conversation model
│   │   └── file.py          # File upload model
│   ├── routers/              # API endpoints
│   │   ├── enhanced_auth.py  # Google OAuth endpoints
│   │   ├── direct_chat.py    # AI chat streaming
│   │   ├── conversations.py  # Chat history management
│   │   └── files.py         # File upload handling
│   └── services/             # Business logic
│       ├── ai_providers/     # AI provider implementations
│       │   ├── openai_provider.py    # OpenAI GPT-5, o3, o1 with tools
│       │   ├── anthropic_provider.py # Claude 4 with reasoning & thinking
│       │   └── grok_provider.py      # Grok-3 with real-time search
│       ├── auth_service.py   # Authentication logic
│       ├── conversation_service.py  # Chat management
│       ├── file_service.py   # File & media processing
│       └── chart_tools.py    # Chart & table generation tools
├── uploads/                  # File storage directory
├── main.py                   # FastAPI application entry
├── requirements.txt          # Python dependencies
└── start_dev.sh             # Development startup script
```

### Frontend: `digi-setu-ai/` (Vue 3 + Nuxt 4)
```
digi-setu-ai/
├── components/
│   ├── auth/                # Authentication components
│   │   ├── GoogleSignInButton.vue
│   │   └── LogoutButton.vue
│   ├── chat/                # Chat interface components
│   │   ├── ChatContainer.vue
│   │   ├── ChatMessage.vue
│   │   └── Message.vue
│   ├── enhanced/            # Advanced UI components
│   │   ├── ChartRenderer.vue      # Chart.js integration
│   │   ├── ComponentRenderer.vue  # AI component parser
│   │   └── DataTable.vue         # Paginated data tables
│   ├── layout/              # Layout components
│   │   ├── Header.vue
│   │   ├── Sidebar.vue
│   │   ├── Footer.vue
│   │   └── ThemeToggle.vue
│   ├── ui/                  # Reusable UI components
│   │   ├── StreamingMarkdown.vue  # Enhanced markdown renderer
│   │   ├── DigiSetuInput.vue     # Custom input component
│   │   └── LoadingDots.vue       # Loading animations
│   └── demo/                # Demo components
│       └── examples/        # Educational demos
├── composables/             # Vue 3 composables
│   ├── useChat.ts          # Chat functionality
│   ├── useStreamingChat.ts # Real-time streaming
│   ├── useConversations.ts # Chat history
│   ├── useMarkdown.ts      # Markdown processing
│   └── useTheme.ts         # Theme management
├── stores/                  # Pinia state management
│   └── auth.ts             # Global authentication store
├── pages/                   # Application routes
│   ├── index.vue           # Landing page
│   ├── chat.vue            # Main chat interface
│   ├── signin.vue          # Authentication page
│   └── auth/
│       └── callback.vue    # OAuth callback
├── assets/css/             # Styling
├── nuxt.config.ts          # Nuxt configuration
└── package.json            # Node.js dependencies
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+** with pip
- **Node.js 18+** with npm
- **PostgreSQL** database
- **Google OAuth** credentials

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Digi Bot"
```

### 2. Backend Setup (digi-bot-services)

**Install Dependencies:**
```bash
cd digi-bot-services
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Configure Environment:**
Copy `env.example` to `.env` and update:
```env
# Google OAuth (Required)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# Database (Required)
DATABASE_URL=postgresql+asyncpg://username:password@localhost/digi_bot_ai

# AI Providers (At least one required)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GROK_API_KEY=xai-your-grok-key

# Application Settings
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this
```

**Initialize Database:**
```bash
python create_db.py
```

**Start Backend:**
```bash
./start_dev.sh
# Or manually: python main.py
```

### 3. Frontend Setup (digi-setu-ai)

**Install Dependencies:**
```bash
cd ../digi-setu-ai
npm install
```

**Configure Environment:**
Create `.env`:
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

**Start Frontend:**
```bash
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Technology Stack

### **Backend Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.104.1 | Modern Python web framework |
| **SQLAlchemy** | 2.0.23 | ORM with async support |
| **PostgreSQL** | Latest | Primary database |
| **Redis** | 5.0.1 | Caching and session storage |
| **Pydantic** | 2.5.0 | Data validation and settings |
| **Structlog** | 23.2.0 | Structured logging |
| **OpenAI Whisper** | 20231117 | Audio transcription |
| **Pillow** | 10.1.0 | Image processing |
| **Google OAuth** | 2.25.2 | Authentication |

### **Frontend Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Vue 3** | 3.5.18 | Progressive JavaScript framework |
| **Nuxt 4** | 4.0.3 | Vue.js meta-framework |
| **TypeScript** | 5.9.2 | Type-safe JavaScript |
| **Tailwind CSS** | 4.1.12 | Utility-first CSS framework |
| **Chart.js** | 4.5.0 | Interactive data visualization |
| **ApexCharts** | 5.3.3 | Advanced charting library |
| **Markdown-it** | 14.1.0 | Markdown parser |
| **KaTeX** | 0.16.22 | Math equation rendering |
| **Highlight.js** | 11.11.1 | Syntax highlighting |
| **Mermaid** | 11.4.0 | Diagram generation |

### **AI & ML Integration**
| Provider | Models | Capabilities |
|----------|--------|-------------|
| **OpenAI** | GPT-5, o3, o3-mini, o1 | Tools, Vision, Reasoning, Audio |
| **Anthropic** | Claude 4.1, Sonnet 4, Claude 3.7 | Thinking, Code execution, Analysis |
| **Grok/xAI** | Grok-3, Grok-4 | Real-time search, X integration |

### **Development Tools**
- **Black**: Code formatting
- **isort**: Import sorting  
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **ESLint**: JavaScript linting
- **Prettier**: Code formatting

## 🔧 Configuration

### AI Providers

| Provider | Models Available | Features |
|----------|-----------------|----------|
| **OpenAI** | GPT-5, o3, o3-mini, o1-preview | Tools, Vision, Reasoning, 400K context |
| **Anthropic** | Claude Opus 4.1, Claude Sonnet 4, Claude 3.7 | Thinking, Code execution, 200K context |
| **Grok** | Grok-3, Grok-4 | Real-time search, X integration, 128K context |

### Environment Variables

#### Backend (`digi-bot-services/.env`)
| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | ⚠️ |
| `ANTHROPIC_API_KEY` | Anthropic API key | ⚠️ |
| `GROK_API_KEY` | Grok/xAI API key | ⚠️ |
| `SECRET_KEY` | JWT signing key | ✅ |
| `ENVIRONMENT` | Application environment | ✅ |

*⚠️ At least one AI provider key is required*

#### Frontend (`digi-setu-ai/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `NUXT_PUBLIC_API_BASE` | Backend API URL | `http://localhost:8000` |

## 🛠️ Development

### Backend Development

**Code Quality:**
```bash
cd digi-bot-services
black .              # Code formatting
isort .              # Import sorting
flake8              # Linting
mypy .              # Type checking
```

**Testing:**
```bash
pytest              # Run tests
pytest --cov       # With coverage
```

**Database Management:**
```bash
python create_db.py  # Initialize database
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head  # Apply migrations
```

### Frontend Development

**Development Server:**
```bash
cd digi-setu-ai
npm run dev         # Start dev server
npm run dev:tunnel  # Start with tunnel (0.0.0.0:3000)
```

**Code Quality:**
```bash
npm run lint        # ESLint
npm run lint:fix    # Fix linting issues
```

**Build:**
```bash
npm run build       # Production build
npm run preview     # Preview build
```

## 📊 API Endpoints

### Authentication
- `POST /auth/google` - Google OAuth authentication
- `GET /auth/google/url` - Get Google OAuth URL  
- `GET /auth/callback` - OAuth callback handler
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/me` - Get current user profile

### AI Chat & Streaming
- `POST /chat/stream` - **Main streaming chat with tool execution**
- `POST /chat` - Non-streaming chat (fallback)
- `GET /chat/providers` - List available AI providers
- `GET /chat/models/{provider}` - Get models for provider
- `POST /chat/regenerate/{message_id}` - Regenerate specific message

### Tool Execution
- `POST /tools/chart` - Generate charts via AI tools
- `POST /tools/table` - Generate data tables
- `GET /tools/available` - List available tools
- `POST /tools/execute` - Execute custom tools

### Conversations & History
- `GET /conversations` - List user conversations
- `POST /conversations` - Create new conversation
- `GET /conversations/{id}` - Get conversation details
- `GET /conversations/{id}/messages` - Get conversation messages
- `PUT /conversations/{id}` - Update conversation
- `DELETE /conversations/{id}` - Delete conversation

### File & Media Management
- `POST /files/upload` - Upload files (images, audio, documents)
- `GET /files/{id}` - Get file details
- `GET /files/{id}/download` - Download file
- `DELETE /files/{id}` - Delete file
- `POST /files/audio/transcribe` - Transcribe audio with Whisper
- `POST /files/image/analyze` - Analyze images with vision models
- `GET /files/stats` - Get file storage statistics

### Health & Monitoring
- `GET /` - Basic health check
- `GET /health` - Detailed health status
- `GET /health/db` - Database connection status
- `GET /metrics` - Prometheus metrics (if enabled)

## 🔒 Security Features

- **Google OAuth 2.0** integration
- **JWT token** authentication with refresh
- **Rate limiting** on API endpoints
- **CORS protection** with configurable origins
- **Input validation** with Pydantic models
- **SQL injection** prevention with SQLAlchemy ORM
- **File upload** security with type validation

## 🚢 Production Deployment

### Environment Setup
1. Set `ENVIRONMENT=production`
2. Use strong `SECRET_KEY`
3. Configure production database
4. Set up SSL/HTTPS
5. Configure production OAuth redirect URIs

### Docker Deployment (Optional)
```bash
# Build backend
cd digi-bot-services
docker build -t digi-bot-backend .

# Build frontend
cd ../digi-setu-ai
docker build -t digi-bot-frontend .
```

## 🎯 Feature Showcase

### **📊 Interactive Data Visualization**
```markdown
AI can generate charts directly in responses:

:::pie-chart
title: Market Share Analysis
data: [
  {"label": "Product A", "value": 45},
  {"label": "Product B", "value": 30},
  {"label": "Product C", "value": 25}
]
:::
```

### **📋 Dynamic Data Tables**
```markdown
AI can create sortable, paginated tables:

:::data-table
title: Performance Metrics
data: [
  {"Metric": "Response Time", "Value": "120ms", "Status": "Good"},
  {"Metric": "Throughput", "Value": "1000/sec", "Status": "Excellent"}
]
:::
```

### **🧮 Advanced Math Rendering**
```latex
$$\int_0^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$

Inline math: $E = mc^2$ and complex equations work seamlessly.
```

### **💻 Enhanced Code Blocks**
```python
# Syntax highlighting for 100+ languages
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### **🎵 Audio Processing**
- Upload audio files for AI transcription
- Whisper integration for accurate speech-to-text
- Support for multiple audio formats
- Generated audio storage and playback

### **🖼️ Image & Media Handling**
- Image upload and analysis with vision models
- File type validation and security
- Organized media storage with database tracking
- PIL/Pillow integration for image processing

### **🤖 AI Tool Execution**
- **Chart Tools**: AI generates interactive visualizations
- **Table Tools**: AI creates structured data displays  
- **Custom Tools**: Extensible tool registry system
- **Real-time Execution**: Tools run during chat streaming

### **📝 Rich Content Containers**
```markdown
::: info
💡 AI can use styled containers for better information presentation
:::

::: warning
⚠️ Important warnings are highlighted appropriately
:::
```

## 🐛 Troubleshooting

### Common Issues

**Google OAuth Setup:**
1. Create project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs: `http://localhost:8000/auth/callback`

**Database Connection:**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Create database
createdb digi_bot_ai

# Test connection
psql postgresql://username:password@localhost/digi_bot_ai
```

**AI Provider Setup:**
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com)
- **Anthropic**: Get API key from [Anthropic Console](https://console.anthropic.com)
- **Grok**: Get API key from [xAI Console](https://console.x.ai)

### Development Issues

**Backend not starting:**
```bash
cd digi-bot-services
source venv/bin/activate
python main.py  # Check error messages
```

**Frontend build issues:**
```bash
cd digi-setu-ai
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests and linting
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Anthropic** for Claude models
- **xAI** for Grok models with real-time search
- **Google** for OAuth authentication services
- **FastAPI** and **Vue.js** communities
- All contributors and testers

---

**Built with ❤️ by the Digi Setu Team**

For support, please open an issue or contact us at support@digisetu.ai