#!/usr/bin/env python3
"""
Server startup script for Mentor Mind Backend
Run this file to start the FastAPI server
"""
import uvicorn
import logging
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings

def main():
    """Start the FastAPI server"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        settings.validate_config()
        logger.info("✅ Configuration validated successfully")
        
        logger.info("🚀 Starting Mentor Mind Backend Server...")
        logger.info(f"📍 Server will be available at: http://{settings.API_HOST}:{settings.API_PORT}")
        logger.info("📖 API Documentation: http://localhost:8000/docs")
        logger.info("🏥 Health Check: http://localhost:8000/health")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )
        
    except ValueError as e:
        logger.error(f"❌ Configuration Error: {e}")
        logger.error("💡 Make sure you have created a .env file with your Hugging Face API token")
        logger.error("   Example: HUGGINGFACE_API_TOKEN=hf_your_token_here")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 