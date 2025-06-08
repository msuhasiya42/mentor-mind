import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List, Tuple

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
    # OpenRouter Configuration - Free Models 2025
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_BASE: str = "https://openrouter.ai/api/v1"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # FREE OpenRouter Models (as of 2025)
    # These models are available for free with OpenRouter
    FREE_MODELS = {
        "deepseek": {
            "model_name": "deepseek/deepseek-chat-v3-0324:free",
            "description": "High-performance model excellent for coding and reasoning",
            "max_tokens": 4096,
            "good_for": ["coding", "reasoning", "general_chat"]
        },
        "qwen": {
            "model_name": "qwen/qwen-2.5-7b-instruct:free", 
            "description": "Good general purpose model",
            "max_tokens": 4096,
            "good_for": ["general_chat", "text_generation"]
        },
        "llama": {
            "model_name": "meta-llama/llama-3.1-8b-instruct:free",
            "description": "Meta's open source model, good for various tasks",
            "max_tokens": 4096,
            "good_for": ["text_generation", "summarization"]
        },
        "gemma": {
            "model_name": "google/gemma-2-9b-it:free",
            "description": "Google's efficient model",
            "max_tokens": 4096,
            "good_for": ["instruction_following", "text_generation"]
        }
    }
    
    # Default model (DeepSeek is highly rated for coding tasks)
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "deepseek/deepseek-chat-v3-0324:free")
    
    # Fallback models in order of preference
    FALLBACK_MODELS: List[str] = [
        "deepseek/deepseek-chat-v3-0324:free",
        "qwen/qwen-2.5-7b-instruct:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free"
    ]
    
    # Rate limiting info (important for free tier)
    # Default: 50 requests/day, with $10 credit: 1000 requests/day
    RATE_LIMIT_WARNING_THRESHOLD: int = 45  # Warn when approaching daily limit
    
    @property
    def openrouter_headers(self) -> dict:
        """Get headers for OpenRouter API requests"""
        if not self.OPENROUTER_API_KEY:
            return {"Content-Type": "application/json"}
        
        return {
            "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # Optional: your app URL
            "X-Title": "Mentor Mind"  # Optional: your app name
        }
    
    def get_model_info(self, model_key: str = None) -> dict:
        """Get information about a specific model or the default model"""
        if not model_key:
            # Find the default model info
            for key, info in self.FREE_MODELS.items():
                if info["model_name"] == self.DEFAULT_MODEL:
                    return info
            # If default not found, return first available
            return list(self.FREE_MODELS.values())[0]
        
        return self.FREE_MODELS.get(model_key, list(self.FREE_MODELS.values())[0])
    
    def validate_config(self) -> bool:
        """Validate OpenRouter configuration"""
        if not self.OPENROUTER_API_KEY:
            print("⚠️  OPENROUTER_API_KEY not found!")
            return False
        
        
        return True

# Create global settings instance
settings = Settings() 