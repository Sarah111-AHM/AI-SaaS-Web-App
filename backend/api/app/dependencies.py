"""
🚀 AI SaaS Platform - FastAPI Dependencies
Dependency injection for API endpoints
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import logging

from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DEBUG,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_PERIOD,
)

logger = logging.getLogger(__name__)

# ========== Security ==========
security = HTTPBearer(auto_error=False)

# In-memory rate limiting store (use Redis in production)
_rate_limit_store = {}

# ========== Token Functions ==========
def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing user data (must include 'sub' key)
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    # Set expiration
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    # Create token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Token created for user: {data.get('sub')}")
    
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ========== Dependency Functions ==========
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Get current user from JWT token
    
    Dependency for endpoints requiring authentication
    
    Args:
        credentials: HTTP Bearer token
    
    Returns:
        User information dictionary
    """
    if not credentials:
        if DEBUG:
            # Return demo user in development mode
            return {
                "user_id": "demo_user",
                "email": "demo@aisaas.com",
                "role": "user",
                "subscription": "free",
                "is_authenticated": False,
                "rate_limit": 100,
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        payload = verify_token(credentials.credentials)
        
        # Extract user info
        user_id = payload.get("sub", "unknown")
        email = payload.get("email", f"{user_id}@aisaas.com")
        role = payload.get("role", "user")
        subscription = payload.get("subscription", "free")
        
        # Determine rate limit based on subscription
        rate_limit = {
            "free": 100,
            "pro": 1000,
            "enterprise": 10000,
        }.get(subscription, 100)
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "subscription": subscription,
            "is_authenticated": True,
            "rate_limit": rate_limit,
            "token_payload": payload,
        }
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None
    
    For endpoints that work for both authenticated and unauthenticated users
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

# ========== Rate Limiting ==========
def rate_limit_dependency(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_optional_user)
) -> None:
    """
    Rate limiting dependency
    
    Limits requests based on user authentication status
    """
    if not RATE_LIMIT_ENABLED:
        return
    
    # Determine rate limit key
    if current_user and current_user.get("is_authenticated"):
        # Authenticated users get higher limits
        key = f"user:{current_user['user_id']}"
        limit = current_user.get("rate_limit", RATE_LIMIT_REQUESTS)
    else:
        # IP-based limiting for anonymous users
        key = f"ip:{request.client.host}"
        limit = RATE_LIMIT_REQUESTS // 2  # Half for anonymous
    
    # Simple in-memory rate limiting (use Redis in production)
    current_time = datetime.utcnow().timestamp()
    
    if key in _rate_limit_store:
        timestamps = _rate_limit_store[key]
        
        # Remove old timestamps
        timestamps = [t for t in timestamps if current_time - t < RATE_LIMIT_PERIOD]
        
        # Check if limit exceeded
        if len(timestamps) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(RATE_LIMIT_PERIOD)}
            )
        
        timestamps.append(current_time)
        _rate_limit_store[key] = timestamps
    else:
        _rate_limit_store[key] = [current_time]

# ========== Admin Protection ==========
def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require admin role for endpoint access
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_pro_subscription(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Require Pro or higher subscription
    """
    subscription = current_user.get("subscription", "free")
    if subscription not in ["pro", "enterprise", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required"
        )
    return current_user

# ========== Export Dependencies ==========
__all__ = [
    "security",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "get_optional_user",
    "rate_limit_dependency",
    "require_admin",
    "require_pro_subscription",
]
