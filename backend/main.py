from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from services.learning_path_generator import LearningPathGenerator
from models import LearningPathRequest, LearningPathResponse, PydanticResource, PydanticLearningPath
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the learning path generator
learning_path_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    global learning_path_generator
    
    # Startup logic
    try:
        # Validate configuration
        settings.validate_config()
        logger.info("✅ Configuration validated successfully")
        
        # Initialize the learning path generator
        learning_path_generator = LearningPathGenerator()
        logger.info("✅ Learning path generator initialized with Expert AI Tutor")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        # Continue with basic functionality if OpenRouter key is missing
        learning_path_generator = LearningPathGenerator()
        logger.warning("⚠️ Started with limited AI functionality due to configuration issues")
    
    # App is running
    yield
    
    # Shutdown logic
    if learning_path_generator:
        try:
            await learning_path_generator.close()
            logger.info("🧹 Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

app = FastAPI(
    title="Mentor Mind API",
    description="AI-Powered Learning Path Generator with Expert AI Tutor",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def root():
    return {"message": "Welcome to Mentor Mind API - Now with Expert AI Tutor!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if OpenRouter API key is configured
        openrouter_status = "configured" if settings.OPENROUTER_API_KEY else "not configured"
        
        # Get available models info
        available_models = len(settings.FREE_MODELS) if hasattr(settings, 'FREE_MODELS') else 0
        
        return {
            "status": "healthy",
            "openrouter_api": openrouter_status,
            "default_model": settings.DEFAULT_MODEL,
            "available_free_models": available_models,
            "version": "2.0.0 (Expert AI Tutor)",
            "features": ["single_llm_call", "expert_persona", "curated_resources"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/generate-learning-path", response_model=LearningPathResponse)
async def generate_learning_path(request: LearningPathRequest):
    try:
        if not request.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        if not learning_path_generator:
            raise HTTPException(status_code=500, detail="Learning path generator not initialized")
        
        logger.info(f"Generating expert learning path for topic: {request.topic}")
        
        # Generate the learning path using Expert AI Tutor (returns dataclass)
        learning_path_dataclass = await learning_path_generator.generate_path(request.topic.strip())
        
        # Convert dataclass to Pydantic model
        learning_path_pydantic = PydanticLearningPath(
            docs=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.docs),
            blogs=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.blogs),
            youtube=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.youtube),
            free_courses=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.free_courses),
            paid_courses=convert_dataclass_to_pydantic(learning_path_dataclass, learning_path_dataclass.paid_courses)
        )
        
        response = LearningPathResponse(
            topic=request.topic.strip(),
            learning_path=learning_path_pydantic
        )
        
        logger.info(f"Successfully generated expert learning path for: {request.topic}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 