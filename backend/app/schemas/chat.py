"""
Chat Schemas

Pydantic schemas for chat-related API endpoints.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AIProvider(str, Enum):
    """Available AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROK = "grok"


class MessageRole(str, Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessagePartType(str, Enum):
    """Message part types."""
    TEXT = "text"
    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    FILE = "file"


class ChatMessage(BaseModel):
    """Chat message schema."""
    role: MessageRole
    content: str
    files: Optional[List[str]] = None  # File IDs
    metadata: Optional[Dict[str, Any]] = None


class MessagePart(BaseModel):
    """Message part schema."""
    type: MessagePartType
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    order: int = 0


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = None
    project_id: Optional[int] = None
    provider: AIProvider = AIProvider.OPENAI
    model: Optional[str] = None
    files: Optional[List[str]] = None  # File IDs
    ai_settings: Optional[Dict[str, Any]] = None
    stream: bool = True


class ChatResponse(BaseModel):
    """Chat response schema."""
    message_id: int
    conversation_id: int
    content: str
    parts: List[MessagePart] = []
    provider: str
    model: str
    tokens_used: Optional[int] = None
    created_at: datetime


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    type: str  # content, reasoning, tool_call, tool_result, activity, error, finish
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class ActivityUpdate(BaseModel):
    """Activity streaming update."""
    activity: str
    progress: Optional[float] = None  # 0.0 to 1.0
    metadata: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    """Tool call schema."""
    id: str
    type: str = "function"
    function: Dict[str, Any]


class ToolResult(BaseModel):
    """Tool result schema."""
    tool_call_id: str
    output: str
    success: bool = True
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReasoningStep(BaseModel):
    """Reasoning step schema."""
    step: int
    content: str
    timestamp: datetime


class RegenerateRequest(BaseModel):
    """Request to regenerate a message."""
    message_id: int
    provider: Optional[AIProvider] = None
    model: Optional[str] = None
    ai_settings: Optional[Dict[str, Any]] = None


class ConversationSummary(BaseModel):
    """Conversation summary schema."""
    id: int
    title: str
    summary: Optional[str] = None
    message_count: int
    last_message_at: Optional[datetime] = None
    created_at: datetime


class ProviderStatus(BaseModel):
    """AI provider status schema."""
    provider: str
    name: str
    status: str  # healthy, unhealthy, maintenance
    models: List[str]
    response_time: Optional[float] = None
    last_check: datetime


class ProvidersStatusResponse(BaseModel):
    """Response for providers status endpoint."""
    providers: List[ProviderStatus]
    default_provider: str
    total_healthy: int


class ChatSettings(BaseModel):
    """Chat settings schema."""
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=32000)
    top_p: float = Field(1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0)
    stop_sequences: Optional[List[str]] = None


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    title: Optional[str] = None
    project_id: Optional[int] = None
    provider: AIProvider = AIProvider.OPENAI
    model: Optional[str] = None
    ai_settings: Optional[ChatSettings] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = None
    summary: Optional[str] = None
    is_pinned: Optional[bool] = None
    tags: Optional[List[str]] = None


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    id: int
    title: str
    summary: Optional[str] = None
    status: str
    is_pinned: bool
    ai_provider: str
    ai_model: str
    tags: List[str] = []
    message_count: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    project_id: Optional[int] = None


class MessageResponse(BaseModel):
    """Message response schema."""
    id: int
    conversation_id: int
    role: MessageRole
    content: Optional[str] = None
    parts: List[MessagePart] = []
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Conversation history response schema."""
    conversation: ConversationResponse
    messages: List[MessageResponse]
    total_messages: int
    has_more: bool = False
