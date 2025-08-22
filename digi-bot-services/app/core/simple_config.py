"""
Simple Configuration for Digi Bot Services
Clean, working configuration without complex parsing issues.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Simple application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Digi Bot Services"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-this-in-production-please-make-it-very-long-and-secure"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./digi_bot_services.db"
    )
    DATABASE_ECHO: bool = Field(default=False)
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="") 
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/auth/callback")
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_API_KEY: str = Field(default="")
    GROK_API_KEY: Optional[str] = Field(default=None)
    
    # AI Configuration
    DEFAULT_AI_PROVIDER: str = Field(default="anthropic")
    MAX_TOKENS: int = Field(default=50000)
    REASONING_BUDGET: int = Field(default=3000)
    TEMPERATURE: float = Field(default=0.7)
    
    # File Storage
    UPLOAD_DIR: str = Field(default="uploads")
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024)  # 50MB
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
