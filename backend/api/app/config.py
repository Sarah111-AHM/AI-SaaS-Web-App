"""
🚀 AI SaaS Platform - App Configuration
Application-specific settings and constants
"""

import os
from typing import List

# ========== Application Constants ==========
APP_NAME = "AI SaaS Platform"
VERSION = "2.0.0"
DESCRIPTION = "Modern AI-powered SaaS Platform"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# ========== API Configuration ==========
API_PREFIX = "/api"
DOCS_URL = "/docs" if DEBUG else None
REDOC_URL = "/redoc" if DEBUG else None

# ========== Security ==========
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# ========== CORS ==========
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Parse CORS origins from environment variable if exists
cors_env = os.getenv("BACKEND_CORS_ORIGINS")
if cors_env:
    BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]

# ========== AI Services ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Default AI models
DEFAULT_CHAT_MODEL = "gpt-3.5-turbo"
DEFAULT_IMAGE_MODEL = "dall-e-3"
DEFAULT_CODE_MODEL = "gpt-4"

# ========== Rate Limiting ==========
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 60  # requests per minute
RATE_LIMIT_PERIOD = 60  # seconds

# ========== File Upload ==========
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4"}
UPLOAD_DIR = "uploads"

# ========== Database ==========
DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "aisaas")

# ========== Redis ==========
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# ========== Email ==========
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = os.getenv("EMAILS_FROM_EMAIL", "noreply@aisaas.com")
EMAILS_FROM_NAME = os.getenv("EMAILS_FROM_NAME", APP_NAME)

# ========== Frontend ==========
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# ========== Feature Flags ==========
FEATURE_CHAT_ENABLED = True
FEATURE_IMAGES_ENABLED = True
FEATURE_CODE_ENABLED = True
FEATURE_VOICE_ENABLED = False
FEATURE_AGENTS_ENABLED = False

# Export all constants
__all__ = [
    "APP_NAME",
    "VERSION",
    "DESCRIPTION",
    "ENVIRONMENT",
    "DEBUG",
    "API_PREFIX",
    "DOCS_URL",
    "REDOC_URL",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "BACKEND_CORS_ORIGINS",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GROQ_API_KEY",
    "DEFAULT_CHAT_MODEL",
    "DEFAULT_IMAGE_MODEL",
    "DEFAULT_CODE_MODEL",
    "RATE_LIMIT_ENABLED",
    "RATE_LIMIT_REQUESTS",
    "RATE_LIMIT_PERIOD",
    "MAX_UPLOAD_SIZE",
    "ALLOWED_EXTENSIONS",
    "UPLOAD_DIR",
    "DATABASE_URL",
    "POSTGRES_SERVER",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "REDIS_URL",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "EMAILS_FROM_EMAIL",
    "EMAILS_FROM_NAME",
    "FRONTEND_URL",
    "FEATURE_CHAT_ENABLED",
    "FEATURE_IMAGES_ENABLED",
    "FEATURE_CODE_ENABLED",
    "FEATURE_VOICE_ENABLED",
    "FEATURE_AGENTS_ENABLED",
]
