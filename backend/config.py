import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # Hugging Face Configuration
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "meta/llama-3-8b-instruct")
    TEXT_GENERATION_MODEL: str = os.getenv("TEXT_GENERATION_MODEL", "mistralai/Mistral-Small-3.1-instruct")
    
    @property
    def huggingface_headers(self):
        """Get headers for Hugging Face API requests"""
        if not self.HUGGINGFACE_API_TOKEN:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
        
        return {
            "Authorization": f"Bearer {self.HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def validate_config(self):
        """Validate that required configuration is present"""
        if not self.HUGGINGFACE_API_TOKEN:
            raise ValueError("HUGGINGFACE_API_TOKEN is required but not found in environment variables")
        return True

# Create global settings instance
settings = Settings() 