"""
Configuration management for Digi Bot Services
Unified configuration with environment variable support and security features.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Digi Bot Services"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security
    SECRET_KEY: str = Field(
        default=None,
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # Short-lived access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")  # Long-lived refresh tokens
    ALLOWED_HOSTS: str = Field(default=None, env="ALLOWED_HOSTS")
    
    # Cookie Security (HIPAA Compliance)
    COOKIE_SECURE: bool = Field(default=False, env="COOKIE_SECURE")  # Set to True in production with HTTPS
    COOKIE_DOMAIN: Optional[str] = Field(default=None, env="COOKIE_DOMAIN")  # Set to your domain in production
    COOKIE_HTTPONLY: bool = Field(default=True, env="COOKIE_HTTPONLY")  # Prevent XSS attacks
    
    # CSRF Protection
    CSRF_PROTECTION_ENABLED: bool = Field(default=True, env="CSRF_PROTECTION_ENABLED")
    
    # Session Security
    SESSION_TIMEOUT_MINUTES: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")  # Auto-logout after inactivity
    MAX_CONCURRENT_SESSIONS: int = Field(default=3, env="MAX_CONCURRENT_SESSIONS")  # Limit concurrent sessions per user
    
    # CORS
    CORS_ORIGINS: str = Field(
        default=None,
        env="CORS_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default=None,
        env="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET") 
    GOOGLE_REDIRECT_URI: str = Field(default=None, env="GOOGLE_REDIRECT_URI")
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    GROK_API_KEY: Optional[str] = Field(default=None, env="GROK_API_KEY")
    
    # AI Configuration
    DEFAULT_AI_PROVIDER: str = Field(default="anthropic", env="DEFAULT_AI_PROVIDER")
    DEFAULT_AI_MODEL: str = Field(default="claude-sonnet-4-20250514", env="DEFAULT_AI_MODEL")
    MAX_TOKENS: int = Field(default=32000, env="MAX_TOKENS")
    REASONING_BUDGET: int = Field(default=64000, env="REASONING_BUDGET")  # Large budget for complex reasoning
    TEMPERATURE: float = Field(default=0.5, env="TEMPERATURE")
    ENABLE_INTERLEAVED_THINKING: bool = Field(default=True, env="ENABLE_INTERLEAVED_THINKING")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    ALLOWED_FILE_TYPES: str = Field(
       default=None,
        env="ALLOWED_FILE_TYPES"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Privacy & Security Settings
    DATA_RETENTION_DAYS: int = Field(default=30, env="DATA_RETENTION_DAYS")  # Auto-delete conversations after X days
    ENABLE_AUDIT_LOGGING: bool = Field(default=True, env="ENABLE_AUDIT_LOGGING")  # Track data access
    HASH_USER_IDENTIFIERS: bool = Field(default=True, env="HASH_USER_IDENTIFIERS")  # Hash sensitive IDs
    STORE_CONVERSATION_CONTENT: bool = Field(default=False, env="STORE_CONVERSATION_CONTENT")  # Don't store full chat content
    ENABLE_DATA_ENCRYPTION: bool = Field(default=True, env="ENABLE_DATA_ENCRYPTION")  # Encrypt sensitive fields
    ANONYMIZE_LOGS: bool = Field(default=True, env="ANONYMIZE_LOGS")  # Remove PII from logs
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level setting."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @validator("DEFAULT_AI_PROVIDER")
    def validate_ai_provider(cls, v):
        """Validate AI provider setting."""
        allowed = ["openai", "anthropic", "grok"]
        if v not in allowed:
            raise ValueError(f"AI provider must be one of {allowed}")
        return v
    
    # Helper methods to parse comma-separated strings
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    def get_allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]
    
    def get_allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [file_type.strip() for file_type in self.ALLOWED_FILE_TYPES.split(",") if file_type.strip()]
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    COOKIE_SECURE: bool = True  # Force HTTPS cookies in production


class TestingSettings(Settings):
    """Testing environment settings."""
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://test_user:test_pass@localhost/test_db"
    LOG_LEVEL: str = "WARNING"


def get_environment_settings() -> Settings:
    """Get settings based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()