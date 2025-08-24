# Conversation Service

This directory contains all conversation management services for the Digi Bot application.

## Structure

```
app/services/conversation/
├── __init__.py                     # Module exports and documentation
├── core/                          # Core conversation components
│   ├── __init__.py
│   └── conversation_manager.py    # Advanced conversation management and orchestration
├── service/                       # Conversation service implementations
│   ├── __init__.py
│   └── conversation_service.py    # Core conversation CRUD operations
├── router/                        # FastAPI routers for conversation endpoints
│   ├── __init__.py
│   └── conversations_router.py    # Conversation API routes
└── README.md                      # This documentation
```

## Components

### Core Components

#### ConversationManager (`core/conversation_manager.py`)
Advanced conversation management including:
- Conversation orchestration and coordination
- Integration with AI providers
- Complex conversation workflows
- Multi-service coordination

### Service Components

#### ConversationService (`service/conversation_service.py`)
Core conversation CRUD operations:
- Create, read, update, delete conversations
- Conversation status management
- User conversation management
- Database operations

### Router Components

#### Conversations Router (`router/conversations_router.py`)
FastAPI router providing conversation endpoints:
- GET /api/conversations - List user conversations
- POST /api/conversations - Create new conversation
- GET /api/conversations/{id} - Get specific conversation
- PUT /api/conversations/{id} - Update conversation
- DELETE /api/conversations/{id} - Delete conversation

## Usage

```python
from app.services.conversation import (
    ConversationManager,
    ConversationService,
    conversations_router
)

# Use in FastAPI app
app.include_router(conversations_router)

# Use services
conversation_service = ConversationService(db)
conversation_manager = ConversationManager(db)
```

## Features

- **Conversation Management**: Complete CRUD operations for conversations
- **Status Tracking**: Active/deleted conversation status management
- **User Isolation**: Conversations are isolated per user
- **Performance Optimized**: Efficient database queries and caching
- **AI Integration**: Seamless integration with AI providers
