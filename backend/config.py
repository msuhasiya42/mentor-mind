import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

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