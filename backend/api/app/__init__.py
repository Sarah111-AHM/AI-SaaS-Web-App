"""
AI SaaS Platform - API Application Package
Main FastAPI application module
"""

__version__ = "1.0.0"
__author__ = "AI SaaS Team"
__description__ = "Modern AI-powered SaaS Platform API"

# Export main components
from .main import app
from .config import *
from .dependencies import *

# List what's available when importing from this package
__all__ = [
    "app",
    "APP_NAME",
    "VERSION",
    "DEBUG",
    "API_PREFIX",
    "SECRET_KEY",
    "OPENAI_API_KEY",
    "get_current_user",
    "require_auth",
    "optional_auth",
    "security",
]

print(f"✅ {APP_NAME} v{__version__} package loaded")
