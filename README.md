# 🚀 Digi Setu AI - Advanced AI Assistant Platform

A modern, scalable AI assistant platform with multi-provider orchestration, reasoning display, activity streaming, and comprehensive content handling.

## ✨ Features

### 🧠 **AI Orchestration**
- **GPT-5 as Conductor**: Intelligent task analysis and provider selection
- **Multi-Model Workflows**: OpenAI, Anthropic, Grok coordination
- **Reasoning Generation**: Step-by-step thought process display
- **Activity Streaming**: Privacy-aware, user-friendly progress updates

### 🎨 **Modern UI/UX**
- **Professional Design**: Clean, responsive interface with Digi Setu branding
- **Theme System**: Light/dark/system modes with smooth transitions
- **Responsive Design**: Perfect experience on mobile, tablet, and desktop
- **Accessibility**: WCAG compliant with keyboard navigation

### 💬 **Advanced Chat System**
- **Streaming Responses**: Real-time SSE with proper error handling
- **Message Parts**: Structured content (reasoning, tools, multimodal)
- **Tool Execution**: Step-by-step tool calling with expandable context
- **Content Rendering**: Code, images, tables, JSON, and more

### 📁 **Project Management**
- **Organization**: Projects with conversation grouping
- **Collaboration**: Role-based access and team features
- **History**: Persistent conversation and message storage

## 🏗️ Architecture

### Frontend (Vue.js/Nuxt.js)
```
frontend/
├── components/
│   ├── layout/           # Layout components
│   ├── chat/            # Chat-related components
│   └── ui/              # Reusable UI components
├── composables/         # Vue composables
├── assets/css/          # Design system and styles
└── pages/               # Application pages
```

### Backend (FastAPI/Python)
```
backend/
├── app/
│   ├── core/            # Core configuration and database
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── schemas/         # Pydantic schemas
├── requirements.txt     # Python dependencies
└── Dockerfile          # Container configuration
```

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose**
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** (or use Docker)
- **Redis** (or use Docker)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd digi-setu-demo
```

### 2. Run the Setup Script
```bash
./start-development.sh
```

### 3. Configure Environment Variables

**Backend** (`backend/.env`):
```env
# AI Provider API Keys (Required)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROK_API_KEY=your-grok-api-key-here

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/digi_setu_ai

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
```

**Frontend** (`frontend/.env`):
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

### 4. Start the Applications

**Option A: Development Mode**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option B: Docker Compose**
```bash
docker-compose up
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### AI Providers

The system supports multiple AI providers:

| Provider | Models | Features |
|----------|--------|----------|
| **OpenAI** | GPT-5, GPT-4o, GPT-4o-mini | Tools, Vision, 1M context |
| **Anthropic** | Claude-4, Claude-3.5-sonnet | Analysis, Safety, 200k context |
| **Grok** | Grok-4, Grok-4-vision | Real-time search, 256k context |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `DEFAULT_AI_PROVIDER` | Default AI provider | `openai` |
| `MAX_TOKENS` | Maximum tokens per request | `4000` |
| `ENABLE_METRICS` | Enable Prometheus metrics | `true` |

## 🛠️ Development

### Backend Development

**Install Dependencies**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run Tests**:
```bash
pytest
```

**Database Migrations**:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

**Code Quality**:
```bash
black .
isort .
flake8
mypy .
```

### Frontend Development

**Install Dependencies**:
```bash
cd frontend
npm install
```

**Development Server**:
```bash
npm run dev
```

**Build for Production**:
```bash
npm run build
npm run start
```

**Linting**:
```bash
npm run lint
npm run lint:fix
```

## 📊 Monitoring

### Health Checks
- **Backend**: `GET /api/v1/health`
- **Database**: `GET /api/v1/health/db`
- **AI Providers**: `GET /api/v1/chat/providers/status`

### Metrics (Prometheus)
- Request/response metrics
- AI provider performance
- Database connection stats
- Error rates and latencies

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with Sentry
- Performance monitoring

## 🔒 Security

### Authentication
- JWT-based authentication
- Secure password hashing (bcrypt)
- Token expiration and refresh

### API Security
- CORS configuration
- Rate limiting
- Input validation
- SQL injection prevention

### Data Privacy
- Activity streaming privacy mode
- Sensitive data filtering
- Secure file upload handling

## 🚢 Deployment

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
1. Set `ENVIRONMENT=production`
2. Configure secure `SECRET_KEY`
3. Set up SSL/TLS certificates
4. Configure monitoring and logging
5. Set up database backups

### Scaling
- Horizontal scaling with load balancers
- Database read replicas
- Redis clustering
- CDN for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

### Code Standards
- **Python**: Black, isort, flake8, mypy
- **JavaScript/Vue**: ESLint, Prettier
- **Commits**: Conventional commits
- **Documentation**: Comprehensive docstrings

## 📝 API Documentation

### Chat Endpoints
- `POST /api/v1/chat/stream` - Streaming chat
- `POST /api/v1/chat` - Non-streaming chat
- `POST /api/v1/chat/regenerate/{message_id}` - Regenerate message

### Project Endpoints
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Conversation Endpoints
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations/{id}` - Get conversation
- `PUT /api/v1/conversations/{id}` - Update conversation

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**:
```bash
# Check PostgreSQL is running
docker-compose up postgres

# Verify connection string
echo $DATABASE_URL
```

**AI Provider API Errors**:
```bash
# Check API keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test provider status
curl http://localhost:8000/api/v1/chat/providers/status
```

**Frontend Build Issues**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- xAI for Grok models
- FastAPI and Vue.js communities
- All contributors and testers

---

**Built with ❤️ by the Digi Setu Team**

For support, please open an issue or contact us at support@digisetu.ai