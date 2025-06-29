from fastapi import FastAPI, HTTPException, Request, Depends
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan event handler"""
    logger.info("🚀 MENTOR MIND APPLICATION STARTUP")
    
    try:
        # Validate configuration
        logger.info("⚡ Validating configuration...")
        if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY:
            logger.warning("⚠️ 'Gemini' API and 'OpenAI' key not configured")
        else:
            logger.info("✅ Configuration validated")
        
        # Initialize learning path generator
        logger.info("⚡ Initializing services...")
        try:
            generator = LearningPathGenerator()
            # Test the generator is working
            if not hasattr(generator, 'generate_learning_path'):
                raise AttributeError("LearningPathGenerator is missing required method 'generate_learning_path'")
            
            # Store the generator in the app state
            app.state.learning_path_generator = generator
            logger.info("✅ Services initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LearningPathGenerator: {str(e)}", exc_info=True)
            app.state.learning_path_generator = None
            raise
        
        logger.info("🎯 Application ready to serve requests")
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}", exc_info=True)
        raise
    finally:
        # Cleanup
        logger.info("🧹 Application shutdown starting...")
        try:
            if hasattr(app.state, 'learning_path_generator') and app.state.learning_path_generator:
                await app.state.learning_path_generator.close()
                logger.info("✅ Services cleaned up")
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

# Dependency to get the learning path generator
async def get_learning_path_generator(request: Request) -> LearningPathGenerator:
    """Dependency to get the learning path generator from app state"""
    generator = getattr(request.app.state, 'learning_path_generator', None)
    if generator is None:
        raise HTTPException(
            status_code=503,
            detail="Learning path generator is not available. Please check server logs."
        )
    return generator

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests with essential info"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Log incoming request (only for non-health endpoints)
    if request.url.path not in ["/health"]:
        logger.info(f"📥 {request.method} {request.url.path} [ID: {request_id}]")
    
    # Add request ID to request state for downstream logging
    request.state.request_id = request_id
    request.state.start_time = start_time
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response (only for non-health endpoints or if there's an error)
        if request.url.path not in ["/health"] or response.status_code >= 400:
            logger.info(f"📤 {response.status_code} in {process_time:.2f}s [ID: {request_id}]")
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"💥 Request failed: {str(e)} [ID: {request_id}]")
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


@app.post("/generate-learning-path", response_model=LearningPathResponse)
async def generate_learning_path(
    request: LearningPathRequest,
    http_request: Request,
    generator: LearningPathGenerator = Depends(get_learning_path_generator)
):
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    start_time = getattr(http_request.state, 'start_time', time.time())
    
    logger.info(f"🎯 Generating learning path: '{request.topic}' [ID: {request_id}]")
    
    try:            
        # Validate input
        if not request.topic.strip():
            logger.warning(f"❌ Empty topic provided [ID: {request_id}]")
            raise HTTPException(status_code=400, detail="Topic cannot be empty")

        cleaned_topic = request.topic.strip()
        
        # Generate the learning path using Expert AI Tutor (returns dataclass)
        try:
            learning_path_dataclass = await generator.generate_learning_path(cleaned_topic)
        except Exception as e:
            error_msg = f"Failed to generate learning path: {str(e)}"
            logger.error(f"❌ {error_msg} [ID: {request_id}]", exc_info=True)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Convert dataclass to Pydantic model
        learning_path_pydantic = PydanticLearningPath(
            docs=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.docs),
            blogs=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.blogs),
            youtube=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.youtube),
            free_courses=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.free_courses),
        )
        
        # Create response
        response = LearningPathResponse(
            topic=cleaned_topic,
            learning_path=learning_path_pydantic
        )
        
        # Log completion
        total_resources = (
            len(learning_path_dataclass.docs) + 
            len(learning_path_dataclass.blogs) + 
            len(learning_path_dataclass.youtube) + 
            len(learning_path_dataclass.free_courses) 
        )
        total_time = time.time() - start_time
        
        logger.info(f"✅ Generated {total_resources} resources in {total_time:.2f}s [ID: {request_id}]")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"💥 Generation failed: {str(e)} in {total_time:.2f}s [ID: {request_id}]")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Mentor Mind server directly...")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 