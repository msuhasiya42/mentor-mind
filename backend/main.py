from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time
import uuid

from services.learning_path_generator import LearningPathGenerator
from models import LearningPathRequest, LearningPathResponse, PydanticResource, PydanticLearningPath
from config import settings, setup_logging
from constants import APP_TITLE, APP_DESCRIPTION, APP_VERSION, ALLOWED_ORIGINS

# Initialize comprehensive logging first
setup_logging()

# Get logger for this module
logger = logging.getLogger(__name__)

# Initialize the learning path generator
learning_path_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    global learning_path_generator
    
    logger.info("="*80)
    logger.info("🚀 MENTOR MIND APPLICATION STARTUP")
    logger.info("="*80)
    
    # Startup logic
    try:
        logger.info("⚡ Starting configuration validation...")
        # Validate configuration
        settings.validate_config()
        logger.info("✅ Configuration validated successfully")
        
        logger.info("⚡ Initializing learning path generator...")
        # Initialize the learning path generator
        learning_path_generator = LearningPathGenerator()
        logger.info("✅ Learning path generator initialized with Expert AI Tutor")
        
        # Log configuration status
        logger.info(f"🔧 API Configuration:")
        logger.info(f"   - Host: {settings.API_HOST}")
        logger.info(f"   - Port: {settings.API_PORT}")
        logger.info(f"   - OpenRouter API: {'✅ Configured' if settings.OPENROUTER_API_KEY else '❌ Not configured'}")
        logger.info(f"   - Default Model: {settings.DEFAULT_MODEL}")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}", exc_info=True)
        # Continue with basic functionality if OpenRouter key is missing
        learning_path_generator = LearningPathGenerator()
        logger.warning("⚠️ Started with limited AI functionality due to configuration issues")
    
    logger.info("🎯 Application ready to serve requests")
    logger.info("="*80)
    
    # App is running
    yield
    
    logger.info("="*80)
    logger.info("🛑 MENTOR MIND APPLICATION SHUTDOWN")
    logger.info("="*80)
    
    # Shutdown logic
    if learning_path_generator:
        try:
            logger.info("🧹 Cleaning up resources...")
            await learning_path_generator.close()
            logger.info("✅ Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {str(e)}", exc_info=True)
    
    logger.info("👋 Application shutdown complete")

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests with detailed flow tracking"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log incoming request
    logger.info("="*60)
    logger.info(f"📥 INCOMING REQUEST [ID: {request_id}]")
    logger.info(f"   Method: {request.method}")
    logger.info(f"   URL: {request.url}")
    logger.info(f"   Client: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"   User-Agent: {request.headers.get('user-agent', 'Unknown')}")
    
    # Add request ID to request state for downstream logging
    request.state.request_id = request_id
    request.state.start_time = start_time
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"📤 RESPONSE [ID: {request_id}]")
        logger.info(f"   Status: {response.status_code}")
        logger.info(f"   Processing Time: {process_time:.3f}s")
        logger.info(f"   Response Size: {response.headers.get('content-length', 'Unknown')} bytes")
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        logger.info("="*60)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"💥 REQUEST ERROR [ID: {request_id}]")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Processing Time: {process_time:.3f}s")
        logger.error("="*60, exc_info=True)
        raise

def convert_dataclass_to_pydantic(dataclass_obj, resource_list):
    """Convert dataclass Resource to Pydantic Resource"""
    pydantic_resources = []
    for resource in resource_list:
        pydantic_resource = PydanticResource(
            title=resource.title,
            url=resource.url,
            description=resource.description,
            platform=resource.platform,
            price=resource.price
        )
        pydantic_resources.append(pydantic_resource)
    return pydantic_resources

@app.get("/")
async def root(request: Request):
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"🏠 Root endpoint accessed [ID: {request_id}]")
    return {"message": "Welcome to Mentor Mind API - Now with Expert AI Tutor!"}

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"🏥 Health check requested [ID: {request_id}]")
    
    try:
        # Check if OpenRouter API key is configured
        openrouter_status = "configured" if settings.OPENROUTER_API_KEY else "not configured"
        
        # Get available models info
        available_models = len(settings.FREE_MODELS) if hasattr(settings, 'FREE_MODELS') else 0
        
        health_data = {
            "status": "healthy",
            "openrouter_api": openrouter_status,
            "default_model": settings.DEFAULT_MODEL,
            "available_free_models": available_models,
            "version": f"{APP_VERSION} (Expert AI Tutor)",
            "features": ["single_llm_call", "expert_persona", "curated_resources"]
        }
        
        logger.info(f"✅ Health check successful [ID: {request_id}] - OpenRouter: {openrouter_status}")
        return health_data
        
    except Exception as e:
        logger.error(f"❌ Health check failed [ID: {request_id}]: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/generate-learning-path", response_model=LearningPathResponse)
async def generate_learning_path(request: LearningPathRequest, http_request: Request):
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    start_time = getattr(http_request.state, 'start_time', time.time())
    
    logger.info("🎯 LEARNING PATH GENERATION REQUEST")
    logger.info(f"   Request ID: {request_id}")
    logger.info(f"   Topic: '{request.topic}'")
    logger.info(f"   Topic Length: {len(request.topic)} characters")
    
    try:
        # Validate input
        if not request.topic.strip():
            logger.warning(f"❌ Empty topic provided [ID: {request_id}]")
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        if not learning_path_generator:
            logger.error(f"❌ Learning path generator not initialized [ID: {request_id}]")
            raise HTTPException(status_code=500, detail="Learning path generator not initialized")
        
        cleaned_topic = request.topic.strip()
        logger.info(f"✅ Input validation passed [ID: {request_id}] - Cleaned topic: '{cleaned_topic}'")
        
        # Generate the learning path using Expert AI Tutor (returns dataclass)
        logger.info(f"🚀 Starting learning path generation [ID: {request_id}]")
        learning_path_dataclass = await learning_path_generator.generate_path(cleaned_topic)
        
        # Convert dataclass to Pydantic model
        logger.info(f"🔄 Converting dataclass to Pydantic model [ID: {request_id}]")
        learning_path_pydantic = PydanticLearningPath(
            docs=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.docs),
            blogs=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.blogs),
            youtube=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.youtube),
            free_courses=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.free_courses),
            paid_courses=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.paid_courses)
        )
        
        # Create response
        response = LearningPathResponse(
            topic=cleaned_topic,
            learning_path=learning_path_pydantic
        )
        
        # Log final summary
        total_resources = (
            len(learning_path_dataclass.docs) + 
            len(learning_path_dataclass.blogs) + 
            len(learning_path_dataclass.youtube) + 
            len(learning_path_dataclass.free_courses) + 
            len(learning_path_dataclass.paid_courses)
        )
        total_time = time.time() - start_time
        
        logger.info(f"✅ LEARNING PATH GENERATION COMPLETED [ID: {request_id}]")
        logger.info(f"   Topic: '{cleaned_topic}'")
        logger.info(f"   Total Resources: {total_resources}")
        logger.info(f"   - Docs: {len(learning_path_dataclass.docs)}")
        logger.info(f"   - Blogs: {len(learning_path_dataclass.blogs)}")
        logger.info(f"   - YouTube: {len(learning_path_dataclass.youtube)}")
        logger.info(f"   - Free Courses: {len(learning_path_dataclass.free_courses)}")
        logger.info(f"   - Paid Courses: {len(learning_path_dataclass.paid_courses)}")
        logger.info(f"   Total Processing Time: {total_time:.3f}s")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"💥 LEARNING PATH GENERATION FAILED [ID: {request_id}]")
        logger.error(f"   Topic: '{request.topic}'")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Processing Time: {total_time:.3f}s")
        logger.error("   Stack trace:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Mentor Mind server directly...")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 