import os
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict, Any

# Import constants from constants.py
from constants import (
    API_HOST, API_PORT,
    DEFAULT_MODEL, MODELS, FALLBACK_MODELS, RATE_LIMIT_WARNING_THRESHOLD,
    get_openrouter_headers
)

# Load environment variables - try both backend/.env and project_root/.env
backend_env_path = Path(__file__).parent / '.env'  # backend/.env
project_env_path = Path(__file__).parent.parent / '.env'  # project_root/.env

# Try backend/.env first, then project_root/.env
if backend_env_path.exists():
    load_dotenv(backend_env_path)
elif project_env_path.exists():
    load_dotenv(project_env_path)
else:
    # Try to load from environment variables directly
    load_dotenv()

class Settings:
    # Sensitive Configuration - API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")

    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

    # Import all constants from constants.py
    API_HOST: str = API_HOST
    API_PORT: int = API_PORT
    DEFAULT_MODEL: str = DEFAULT_MODEL
    MODELS = MODELS
    FALLBACK_MODELS = FALLBACK_MODELS  # Fallback model order
    RATE_LIMIT_WARNING_THRESHOLD: int = RATE_LIMIT_WARNING_THRESHOLD
    
    @property
    def openrouter_headers(self) -> dict:
        """Get headers for OpenRouter API requests"""
        return get_openrouter_headers(self.OPENROUTER_API_KEY)
        
    @property
    def openai_headers(self) -> dict:
        """Get headers for OpenAI API requests"""
        return {
            "Authorization": f"Bearer {self.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
    def validate_config(self) -> bool:
        """Validate API configuration"""
        if not self.GEMINI_API_KEY and not self.OPENAI_API_KEY and not self.OPENROUTER_API_KEY:
            print("⚠️  No API keys found! Please set at least one of: GEMINI_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY")
            return False
        return True
        
    def get_available_providers(self) -> list:
        """Get list of available LLM providers based on API keys"""
        providers = []
        if self.GEMINI_API_KEY:
            providers.append("gemini")
        if self.OPENAI_API_KEY:
            providers.append("openai")
        if self.OPENROUTER_API_KEY:
            providers.append("openrouter")
        return providers

# Create global settings instance
settings = Settings() 

def setup_logging():
    """Configure comprehensive logging for the entire application"""
    # Create formatter with detailed information
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | LINE:%(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console formatter (less verbose for console)
    console_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-5s | %(name)-15s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Create handlers list
    handlers = []
    log_dir = None
    
    # Only attempt file logging if not in Vercel environment
    if not os.environ.get('VERCEL'):
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(
                f"{log_dir}/mentor_mind_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            handlers.append(file_handler)
        except OSError as e:
            # If we can't create the logs directory, just log to console
            print(f"Warning: Could not create logs directory - {str(e)}")
            log_dir = None
    
    # Always add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Add all configured handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Configure specific loggers
    logging.getLogger('asyncio').setLevel(logging.INFO)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Set up specific loggers for different components
    loggers_config = {
        'services.learning_path_generator': logging.DEBUG,
        'services.expert_ai_tutor': logging.DEBUG,
        'services.resource_curator': logging.DEBUG,
        'services.ai_response_parser': logging.DEBUG,
        'main': logging.DEBUG,
        'uvicorn.access': logging.WARNING,  # Reduce uvicorn noise
        'uvicorn.error': logging.INFO,
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Log the setup completion
    logger = logging.getLogger(__name__)
    logger.info("=== LOGGING SYSTEM INITIALIZED ===")
    
    if log_dir and os.path.exists(log_dir):
        logger.info(f"Log files created in: {os.path.abspath(log_dir)}")
        logger.info("Full detailed logs: mentor_mind_YYYYMMDD.log")
        logger.info("Error logs: mentor_mind_errors_YYYYMMDD.log")
    else:
        logger.info("Running in serverless environment - logging to console only")
    
    return True 