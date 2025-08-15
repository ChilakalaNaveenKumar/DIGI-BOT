from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union
from enum import Enum

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image" 
    AUDIO = "audio"
    JSON = "json"
    MARKDOWN = "markdown"
    TABLE = "table"
    DIAGRAM = "diagram"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    REASONING = "reasoning"
    ERROR = "error"
    STRUCTURED = "structured"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class FileInfo(BaseModel):
    filename: Optional[str] = Field(default=None)
    mediaType: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    size: Optional[int] = Field(default=None)

class ToolInfo(BaseModel):
    name: str
    description: Optional[str] = Field(default=None)
    parameters: Optional[Dict[str, Any]] = Field(default=None)

class EnhancedMessage(BaseModel):
    role: MessageRole
    content: str
    reasoning: Optional[str] = Field(default=None)
    files: List[FileInfo] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: Optional[str] = Field(default=None)

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = Field(default=None)

class AIProvider(str, Enum):
    OPENAI = "openai"
    GROK = "grok"
    ANTHROPIC = "anthropic"

class ChatRequest(BaseModel):
    messages: List[Union[Message, EnhancedMessage]]
    provider: AIProvider = AIProvider.OPENAI
    model: Optional[str] = Field(default=None)
    # temperature: Optional[float] = Field(default=0.7)  # Removed - not supported by some models
    max_tokens: Optional[int] = Field(default=256000)
    stream: bool = Field(default=True)
    # Enhanced AI SDK 5 features
    enableReasoning: Optional[bool] = Field(default=False)
    enableToolCalling: Optional[bool] = Field(default=False)
    tools: List[ToolInfo] = Field(default_factory=list)
    files: List[FileInfo] = Field(default_factory=list)
    streamMode: Optional[str] = Field(default="standard")

class ChatResponse(BaseModel):
    message: str
    provider: str
    model: str
    usage: Optional[dict] = Field(default=None)

class ProviderInfo(BaseModel):
    id: str
    name: str
    models: List[str]
    status: str = Field(default="active")
    description: Optional[str] = Field(default=None)
    reasoning: Optional[bool] = Field(default=False)
    toolCalling: Optional[bool] = Field(default=False)
    multiModal: Optional[bool] = Field(default=False)

class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = Field(default=None)

class ToolResult(BaseModel):
    id: str
    output: Any
    success: bool = Field(default=True)
    error: Optional[str] = Field(default=None)

class MultimodalContent(BaseModel):
    type: ContentType
    data: Any  # Can be text, base64 image, audio data, JSON object, etc.
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    format: Optional[str] = Field(default=None)  # e.g., "markdown", "json", "png", "wav"
    url: Optional[str] = Field(default=None)  # For generated images/audio
    
class EnhancedChatResponse(BaseModel):
    # Legacy fields for backward compatibility
    content: Optional[str] = Field(default=None)
    reasoning: Optional[str] = Field(default=None)
    tool_call: Optional[ToolCall] = Field(default=None)
    tool_result: Optional[ToolResult] = Field(default=None)
    
    # Enhanced multimodal fields
    multimodal_content: List[MultimodalContent] = Field(default_factory=list)
    content_type: ContentType = Field(default=ContentType.TEXT)
    structured_data: Optional[Dict[str, Any]] = Field(default=None)
    
    # Provider info
    provider: str
    model: Optional[str] = Field(default=None)
    error: Optional[str] = Field(default=None)
    
    # Streaming metadata
    is_complete: bool = Field(default=False)
    chunk_id: Optional[str] = Field(default=None)
