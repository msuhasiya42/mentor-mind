from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import logging

from services.learning_path_generator import LearningPathGenerator
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mentor Mind API",
    description="AI-Powered Learning Path Generator",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the learning path generator
learning_path_generator = None

class LearningPathRequest(BaseModel):
    topic: str

class Resource(BaseModel):
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""

class LearningPath(BaseModel):
    blogs: List[Resource] = []
    docs: List[Resource] = []
    youtube: List[Resource] = []
    free_courses: List[Resource] = []
    paid_courses: List[Resource] = []

class LearningPathResponse(BaseModel):
    topic: str
    learning_path: LearningPath

def convert_dataclass_to_pydantic(dataclass_obj, resource_list):
    """Convert dataclass Resource to Pydantic Resource"""
    pydantic_resources = []
    for resource in resource_list:
        pydantic_resource = Resource(
            title=resource.title,
            url=resource.url,
            description=resource.description,
            platform=resource.platform,
            price=resource.price
        )
        pydantic_resources.append(pydantic_resource)
    return pydantic_resources

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global learning_path_generator
    try:
        # Validate configuration
        settings.validate_config()
        logger.info("Configuration validated successfully")
        
        # Initialize the learning path generator
        learning_path_generator = LearningPathGenerator()
        logger.info("Learning path generator initialized")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        # Continue without Hugging Face if token is missing
        learning_path_generator = LearningPathGenerator()
        logger.warning("Started with limited functionality due to configuration issues")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    global learning_path_generator
    if learning_path_generator:
        try:
            await learning_path_generator.close()
            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to Mentor Mind API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if Hugging Face token is configured
        hf_status = "configured" if settings.HUGGINGFACE_API_TOKEN else "not configured"
        
        return {
            "status": "healthy",
            "huggingface_api": hf_status,
            "version": "1.0.0"
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
        learning_path_pydantic = LearningPath(
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 