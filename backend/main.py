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
        logger.info("✅ Learning path generator initialized")
        
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
    description="AI-Powered Learning Path Generator",
    version="1.0.0",
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
    return {"message": "Welcome to Mentor Mind API"}

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
            "version": "2.0.0 (OpenRouter)"
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
        
        logger.info(f"Generating learning path for topic: {request.topic}")
        
        # Generate the learning path (returns dataclass)
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
        
        logger.info(f"Successfully generated learning path for: {request.topic}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {str(e)}")

@app.post("/debug-search")
async def debug_search(request: LearningPathRequest):
    """Debug endpoint to test search functionality directly"""
    try:
        from services.content_aggregator import ContentAggregator
        from services.search_engines import LLMSearchEngine
        
        # Test LLM search engine directly
        llm_search = LLMSearchEngine()
        llm_resources = await llm_search.search(request.topic)
        await llm_search.close()
        
        # Test content aggregator
        aggregator = ContentAggregator()
        all_resources = await aggregator.get_all_resources(request.topic, [])
        await aggregator.close()
        
        return {
            "topic": request.topic,
            "llm_direct_count": len(llm_resources),
            "llm_sample": llm_resources[0] if llm_resources else None,
            "aggregator_results": {
                category: len(resources) for category, resources in all_resources.items()
            },
            "aggregator_samples": {
                category: resources[0].title if resources else "No resources"
                for category, resources in all_resources.items()
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 