"""
AI SaaS Platform - Security Module
Authentication, authorization, and security utilities
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing user data (must include 'sub')
        expires_delta: Optional custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    logger.info(f"Token created for user: {data.get('sub', 'unknown')}")
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and return payload
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from token
    
    Args:
        credentials: HTTP Bearer token
    
    Returns:
        User information dictionary
    
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        # In development, allow demo user
        if settings.debug:
            return {
                "sub": "demo_user",
                "email": "demo@aisaas.com",
                "role": "user",
                "plan": "free"
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        payload = verify_token(credentials.credentials)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt in production)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256(f"{password}{salt}".encode())
    return f"{hash_obj.hexdigest()}:{salt}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        stored_hash, salt = hashed.split(":")
        new_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return new_hash == stored_hash
    except:
        return False

def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require admin role"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

def require_premium(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require premium subscription"""
    plan = user.get("plan", "free")
    if plan not in ["premium", "enterprise", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return user

# Export
__all__ = [
    "security",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "hash_password",
    "verify_password",
    "require_admin",
    "require_premium",
]

print("✅ Security module loaded")
