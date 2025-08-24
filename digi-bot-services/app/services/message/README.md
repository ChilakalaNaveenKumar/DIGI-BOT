# Message Service

This directory contains all message management services for the Digi Bot application.

## Structure

```
app/services/message/
├── __init__.py                     # Module exports and documentation
├── core/                          # Core message components (reserved for future use)
│   └── __init__.py
├── service/                       # Message service implementations
│   ├── __init__.py
│   ├── message_service.py         # Core message CRUD operations
│   └── message_part_service.py    # Message parts handling
├── router/                        # FastAPI routers for message endpoints
│   ├── __init__.py
│   └── stream_router.py          # Message streaming API routes
└── README.md                      # This documentation
```

## Components

### Service Components

#### MessageService (`service/message_service.py`)
Core message CRUD operations:
- Create, read, update, delete messages
- Message content management
- AI provider tracking
- Token count and performance metrics
- Message history management

#### MessagePartService (`service/message_part_service.py`)
Message parts handling:
- Multi-part message support
- File attachments
- Rich content handling
- Message part ordering

### Router Components

#### Stream Router (`router/stream_router.py`)
FastAPI router providing message streaming endpoints:
- POST /api/stream/chat - Stream AI responses
- Real-time message streaming
- AI provider integration
- Token usage tracking

## Usage

```python
from app.services.message import (
    MessageService,
    MessagePartService,
    stream_router
)

# Use in FastAPI app
app.include_router(stream_router)

# Use services
message_service = MessageService(db)
message_part_service = MessagePartService(db)
```

## Features

- **Message Management**: Complete CRUD operations for messages
- **Streaming Support**: Real-time AI response streaming
- **Multi-part Messages**: Support for complex message structures
- **AI Integration**: Seamless integration with multiple AI providers
- **Performance Tracking**: Token usage and response time metrics
- **Rich Content**: Support for text, files, and other content types
