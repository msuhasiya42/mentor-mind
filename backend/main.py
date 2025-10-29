from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import List
import logging
import time
import uuid

from services.learning_path_generator import LearningPathGenerator
from models import LearningPathRequest, LearningPathResponse, PydanticResource, PydanticLearningPath
from config import settings, setup_logging
from constants import APP_TITLE, APP_DESCRIPTION, APP_VERSION, ALLOWED_ORIGINS
from database.db import get_db, init_db
from database import crud

# Initialize comprehensive logging first
setup_logging()

# Get logger for this module
logger = logging.getLogger(__name__)

# Global variable for learning path generator
learning_path_generator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan event handler"""
    logger.info("🚀 MENTOR MIND APPLICATION STARTUP")

    try:
        # Initialize database
        logger.info("⚡ Initializing database...")
        try:
            init_db()
            logger.info("✅ Database initialized successfully")
        except Exception as db_error:
            logger.error(f"❌ Database initialization failed: {str(db_error)}", exc_info=True)
            logger.warning("⚠️ App will continue but database features may not work")
            # Continue startup even if DB fails

        # Validate configuration
        logger.info("⚡ Validating configuration...")
        if not settings.OPENROUTER_API_KEY:
            logger.warning("⚠️ OpenRouter API key not configured")
        else:
            logger.info("✅ Configuration validated")

        # Initialize learning path generator
        logger.info("⚡ Initializing services...")
        global learning_path_generator
        try:
            learning_path_generator = LearningPathGenerator()
            logger.info("✅ Services initialized")
        except Exception as init_error:
            logger.error(f"❌ Failed to initialize LearningPathGenerator: {str(init_error)}", exc_info=True)
            logger.warning("⚠️ Generator will be initialized on first request instead")
            # Don't fail startup, generator will be created on-demand

        logger.info("🎯 Application ready to serve requests")

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}", exc_info=True)
        # Don't raise to allow app to start in degraded mode

    yield  # Server is running

    # Cleanup
    logger.info("🧹 Application shutdown starting...")
    try:
        if learning_path_generator:
            await learning_path_generator.close()
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

        # Check database status
        db_status = "unknown"
        try:
            from database.db import SessionLocal
            from sqlalchemy import inspect
            db = SessionLocal()
            try:
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                db_status = f"connected ({len(tables)} tables)"
            finally:
                db.close()
        except Exception as db_err:
            db_status = f"error: {str(db_err)[:50]}"

        health_data = {
            "status": "healthy",
            "database": db_status,
            "openrouter_api": openrouter_status,
            "default_model": settings.DEFAULT_MODEL,
            "available_free_models": available_models,
            "version": f"{APP_VERSION} (Expert AI Tutor)",
            "features": ["single_llm_call", "expert_persona", "curated_resources", "persistent_storage"]
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
    global learning_path_generator
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    start_time = getattr(http_request.state, 'start_time', time.time())

    logger.info(f"🎯 Generating learning path: '{request.topic}' [ID: {request_id}]")

    try:
        # Validate input
        if not request.topic.strip():
            logger.warning(f"❌ Empty topic provided [ID: {request_id}]")
            raise HTTPException(status_code=400, detail="Topic cannot be empty")

        cleaned_topic = request.topic.strip()

        # Initialize generator if not already initialized (fallback for serverless)
        if learning_path_generator is None:
            logger.warning(f"⚠️ Generator not initialized, creating new instance [ID: {request_id}]")
            learning_path_generator = LearningPathGenerator()

        # Generate the learning path using Expert AI Tutor (returns dataclass)
        learning_path_dataclass = await learning_path_generator.generate_learning_path(cleaned_topic)
        
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

        # Save to database (get DB session)
        try:
            from database.db import SessionLocal
            db = SessionLocal()
            try:
                # Prepare data for storage
                data_to_store = {
                    "topic": cleaned_topic,
                    "learning_path": {
                        "docs": [{"title": r.title, "url": r.url, "description": r.description, "platform": r.platform, "price": r.price} for r in learning_path_pydantic.docs],
                        "blogs": [{"title": r.title, "url": r.url, "description": r.description, "platform": r.platform, "price": r.price} for r in learning_path_pydantic.blogs],
                        "youtube": [{"title": r.title, "url": r.url, "description": r.description, "platform": r.platform, "price": r.price} for r in learning_path_pydantic.youtube],
                        "free_courses": [{"title": r.title, "url": r.url, "description": r.description, "platform": r.platform, "price": r.price} for r in learning_path_pydantic.free_courses]
                    }
                }
                saved_path = crud.create_learning_path(db, cleaned_topic, data_to_store)
                logger.info(f"💾 Saved to database with ID: {saved_path.id} [ID: {request_id}]")

                # Add ID to response for frontend to use
                response.id = saved_path.id
            finally:
                db.close()
        except Exception as e:
            logger.error(f"⚠️ Failed to save to database: {str(e)} [ID: {request_id}]")
            # Don't fail the request if DB save fails

        return response
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"💥 Generation failed: {str(e)} in {total_time:.2f}s [ID: {request_id}]")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {str(e)}")


# ==================== New Database Endpoints ====================

@app.get("/learning-paths")
async def get_all_learning_paths(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all saved learning paths."""
    try:
        paths = crud.get_all_learning_paths(db, skip=skip, limit=limit)
        result = []
        for path in paths:
            result.append({
                "id": path.id,
                "topic": path.topic,
                "created_at": path.created_at.isoformat() if path.created_at else None,
                "data": path.get_data()
            })
        logger.info(f"📚 Retrieved {len(result)} learning paths")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to retrieve learning paths: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/learning-paths/{path_id}")
async def get_learning_path(path_id: int, db: Session = Depends(get_db)):
    """Get a specific learning path by ID."""
    try:
        path = crud.get_learning_path(db, path_id)
        if not path:
            raise HTTPException(status_code=404, detail="Learning path not found")

        logger.info(f"📖 Retrieved learning path ID: {path_id}")
        return {
            "id": path.id,
            "topic": path.topic,
            "created_at": path.created_at.isoformat() if path.created_at else None,
            "data": path.get_data()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to retrieve learning path {path_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/learning-paths/{path_id}/action")
async def track_action(path_id: int, action_type: str, db: Session = Depends(get_db)):
    """Track user actions like downloads or views."""
    try:
        # Verify learning path exists
        path = crud.get_learning_path(db, path_id)
        if not path:
            raise HTTPException(status_code=404, detail="Learning path not found")

        # Validate action type
        valid_actions = ["viewed", "downloaded_pdf", "downloaded_doc"]
        if action_type not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action type. Must be one of: {valid_actions}")

        # Create action
        action = crud.create_user_action(db, path_id, action_type)
        logger.info(f"✅ Tracked action '{action_type}' for learning path {path_id}")

        return {"success": True, "action_id": action.id, "action_type": action_type}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to track action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall statistics."""
    try:
        stats = crud.get_statistics(db)
        logger.info(f"📊 Retrieved statistics")
        return stats
    except Exception as e:
        logger.error(f"❌ Failed to retrieve statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/init-db")
async def initialize_database():
    """Manually trigger database initialization (creates tables if they don't exist)."""
    try:
        logger.info("📦 Manual database initialization requested")
        init_db()
        return {
            "success": True,
            "message": "Database tables created successfully",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Manual database initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Mentor Mind server directly...")
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT) 