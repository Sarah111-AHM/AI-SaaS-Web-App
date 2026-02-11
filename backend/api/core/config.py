"""
AI SaaS Platform - Core Configuration
Advanced configuration settings using pydantic
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings using pydantic"""
    
    # App Info
    app_name: str = "AI SaaS Platform"
    version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True
    
    # API
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    database_url: Optional[str] = None
    postgres_server: str = "localhost"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "aisaas"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    
    # AI Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # File Upload
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    upload_dir: str = "uploads"
    
    # Rate Limiting
    rate_limit_requests: int = 100  # per minute
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

print(f"✅ Core config loaded: {settings.app_name} v{settings.version}")
