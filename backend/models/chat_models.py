from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = None

class AIProvider(str, Enum):
    OPENAI = "openai"
    GROK = "grok"
    ANTHROPIC = "anthropic"

class ChatRequest(BaseModel):
    messages: List[Message]
    provider: AIProvider = AIProvider.OPENAI
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500
    stream: bool = True

class ChatResponse(BaseModel):
    message: str
    provider: str
    model: str
    usage: Optional[dict] = None

class ProviderInfo(BaseModel):
    id: str
    name: str
    models: List[str]
    status: str = "active"

class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]
