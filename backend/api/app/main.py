"""
🚀 AI SaaS Platform - Main API
Modern AI-powered SaaS Platform with multi-model support
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import openai
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import time

# ========== Configuration ==========
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# ========== FastAPI App ==========
app = FastAPI(
    title="AI SaaS Platform API",
    description="Modern AI-powered SaaS Platform with ChatGPT, DALL-E, and more",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "AI SaaS Team",
        "url": "https://github.com/Sarah111-AHM/AI-SaaS-Web-App",
        "email": "support@aisaas.example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# ========== CORS Middleware ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ========== Security ==========
security = HTTPBearer()

# ========== Pydantic Models ==========
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=4000, description="User message to send to AI")
    model: str = Field(default="gpt-3.5-turbo", description="AI model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Creativity level (0-2)")
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens in response")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Explain quantum computing in simple terms",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }

class ImageRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt for image generation")
    size: str = Field(default="1024x1024", description="Image size")
    style: Optional[str] = Field(default="vivid", description="Image style")
    quality: Optional[str] = Field(default="standard", description="Image quality")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "A cute cat coding on a laptop, digital art",
                "size": "1024x1024",
                "style": "vivid",
                "quality": "standard"
            }
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    environment: str = Field(..., description="Current environment")

# ========== Global Variables ==========
app_start_time = time.time()
openai_client = None

# ========== Helper Functions ==========
def get_openai_client():
    """Initialize OpenAI client"""
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. AI features will not work.")
            return None
        openai_client = openai.OpenAI(api_key=api_key)
    return openai_client

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key (simplified for development)"""
    # For development, accept any token or skip auth
    # In production, validate against database
    token = credentials.credentials if credentials else "demo-token"
    
    # Simple demo validation
    valid_tokens = ["demo-token", "test-token", os.getenv("API_TOKEN", "")]
    if token not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": "demo-user", "token": token[:10] + "..."}

# ========== API Endpoints ==========
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🚀 Welcome to AI SaaS Platform API",
        "version": "2.0.0",
        "description": "Modern AI-powered SaaS Platform",
        "endpoints": {
            "chat": "/api/chat (POST)",
            "image": "/api/image (POST)",
            "health": "/api/health (GET)",
            "models": "/api/models (GET)",
            "docs": "/api/docs"
        },
        "repository": "https://github.com/Sarah111-AHM/AI-SaaS-Web-App",
        "status": "operational"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health and status"""
    uptime = time.time() - app_start_time
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        uptime_seconds=round(uptime, 2),
        environment=os.getenv("ENVIRONMENT", "development")
    )

@app.get("/api/models", tags=["AI"])
async def list_available_models():
    """List available AI models"""
    return {
        "chat_models": {
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4-vision-preview"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "google": ["gemini-pro", "gemini-ultra"],
            "meta": ["llama-2", "llama-3"]
        },
        "image_models": {
            "openai": ["dall-e-2", "dall-e-3"],
            "stability": ["stable-diffusion-xl", "stable-diffusion-3"],
            "midjourney": ["v5", "v6"]
        },
        "embedding_models": ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]
    }

@app.post("/api/chat", tags=["AI"])
async def chat_completion(
    request: ChatRequest,
    auth: dict = Depends(verify_api_key)
):
    """
    Chat with AI models (OpenAI GPT)
    
    Send a message to AI and get a response.
    Supports streaming (to be implemented).
    """
    try:
        logger.info(f"Chat request from user {auth.get('user_id')} using model {request.model}")
        
        client = get_openai_client()
        if client is None:
            return {
                "success": False,
                "error": "OpenAI API not configured. Please set OPENAI_API_KEY in .env file.",
                "demo_response": "Hello! This is a demo response. Configure OpenAI API key for real AI responses."
            }
        
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=request.model,
            messages=[
                {
                    "role": "system", 
                    "content": """You are a helpful AI assistant for the AI SaaS Platform. 
                    Be concise, accurate, and friendly. If asked about your capabilities,
                    mention you're part of an AI SaaS platform with multiple models."""
                },
                {"role": "user", "content": request.message}
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False
        )
        
        # Extract response
        ai_response = response.choices[0].message.content
        usage = response.usage
        
        return {
            "success": True,
            "response": ai_response,
            "model": request.model,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "estimated_cost_usd": round((usage.total_tokens / 1000) * 0.002, 4)  # Approximate cost
            },
            "user_id": auth.get("user_id"),
            "timestamp": datetime.now().isoformat()
        }
        
    except openai.AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OpenAI API key"
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

@app.post("/api/image", tags=["AI"])
async def generate_image(
    request: ImageRequest,
    auth: dict = Depends(verify_api_key)
):
    """
    Generate image from text prompt using DALL-E
    
    Create AI-generated images from text descriptions.
    """
    try:
        logger.info(f"Image generation request: {request.prompt[:50]}...")
        
        client = get_openai_client()
        if client is None:
            return {
                "success": False,
                "error": "OpenAI API not configured",
                "demo_image_url": "https://via.placeholder.com/1024x1024/4F46E5/FFFFFF?text=AI+Generated+Image+Placeholder"
            }
        
        # Make API call to DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=request.prompt,
            size=request.size,
            quality=request.quality,
            style=request.style,
            n=1
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        return {
            "success": True,
            "image_url": image_url,
            "revised_prompt": revised_prompt,
            "model": "dall-e-3",
            "size": request.size,
            "quality": request.quality,
            "user_id": auth.get("user_id"),
            "timestamp": datetime.now().isoformat(),
            "note": "Generated image will expire after 1 hour (OpenAI limitation)"
        }
        
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )

# ========== Middleware ==========
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = "2.0.0"
    response.headers["X-Environment"] = os.getenv("ENVIRONMENT", "development")
    return response

# ========== Application Events ==========
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 50)
    logger.info("🚀 AI SaaS Platform API Starting Up")
    logger.info(f"📁 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"🔗 OpenAPI Docs: http://localhost:8000/api/docs")
    logger.info(f"📚 ReDoc: http://localhost:8000/api/redoc")
    logger.info("=" * 50)
    
    # Initialize OpenAI client
    client = get_openai_client()
    if client:
        logger.info("✅ OpenAI client initialized successfully")
    else:
        logger.warning("⚠️ OpenAI API key not found. AI features will not work.")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 AI SaaS Platform API shutting down...")

# ========== Run Application ==========
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )
