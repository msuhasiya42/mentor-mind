import os
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict, Any

# Import constants from constants.py
from constants import (
    API_HOST, API_PORT, OPENROUTER_API_BASE, DEFAULT_MODEL,
    FREE_MODELS, FALLBACK_MODELS, RATE_LIMIT_WARNING_THRESHOLD,
    get_openrouter_headers, get_model_info
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
    # Sensitive Configuration - Only keep API key here
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    
    # Import all constants from constants.py
    OPENROUTER_API_BASE: str = OPENROUTER_API_BASE
    API_HOST: str = API_HOST
    API_PORT: int = API_PORT
    DEFAULT_MODEL: str = DEFAULT_MODEL
    FREE_MODELS = FREE_MODELS
    FALLBACK_MODELS = FALLBACK_MODELS
    RATE_LIMIT_WARNING_THRESHOLD: int = RATE_LIMIT_WARNING_THRESHOLD
    
    @property
    def openrouter_headers(self) -> dict:
        """Get headers for OpenRouter API requests"""
        return get_openrouter_headers(self.OPENROUTER_API_KEY)
    
    def get_model_info(self, model_key: str = None) -> dict:
        """Get information about a specific model or the default model"""
        return get_model_info(model_key)
    
    def validate_config(self) -> bool:
        """Validate OpenRouter configuration"""
        if not self.OPENROUTER_API_KEY:
            print("⚠️  OPENROUTER_API_KEY not found!")
            return False
        
        return True

# Create global settings instance
settings = Settings() 

def setup_logging():
    """Configure comprehensive logging for the entire application"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
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
    
    # Create file handler for all logs
    file_handler = logging.FileHandler(
        f"{log_dir}/mentor_mind_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Create error file handler
    error_handler = logging.FileHandler(
        f"{log_dir}/mentor_mind_errors_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(error_handler)
    
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
    logging.getLogger(__name__).info("=== LOGGING SYSTEM INITIALIZED ===")
    logging.getLogger(__name__).info(f"Log files created in: {os.path.abspath(log_dir)}")
    logging.getLogger(__name__).info("Full detailed logs: mentor_mind_YYYYMMDD.log")
    logging.getLogger(__name__).info("Error logs: mentor_mind_errors_YYYYMMDD.log")
    
    return True 