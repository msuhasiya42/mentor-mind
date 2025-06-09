"""
Application Constants - Non-sensitive configuration values
Keep only OPENROUTER_API_KEY in .env file, everything else goes here.
"""

from typing import List, Dict

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# OpenRouter API Configuration
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# Default Model Configuration
DEFAULT_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# FREE OpenRouter Models (as of 2025)
# These models are available for free with OpenRouter
FREE_MODELS: Dict[str, Dict] = {
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

# Fallback models in order of preference
FALLBACK_MODELS: List[str] = [
    "deepseek/deepseek-chat-v3-0324:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free"
]

# Rate limiting info (important for free tier)
# Default: 50 requests/day, with $10 credit: 1000 requests/day
RATE_LIMIT_WARNING_THRESHOLD = 45  # Warn when approaching daily limit

# App metadata
APP_TITLE = "Mentor Mind API"
APP_DESCRIPTION = "AI-Powered Learning Path Generator with Expert AI Tutor"
APP_VERSION = "2.0.0"

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000", 
    "http://localhost:5173"  # React dev servers
]

# OpenRouter Headers Configuration
def get_openrouter_headers(api_key: str = None) -> dict:
    """Get headers for OpenRouter API requests"""
    if not api_key:
        return {"Content-Type": "application/json"}
    
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",  # Optional: your app URL
        "X-Title": "Mentor Mind"  # Optional: your app name
    }

def get_model_info(model_key: str = None) -> dict:
    """Get information about a specific model or the default model"""
    if not model_key:
        # Find the default model info
        for key, info in FREE_MODELS.items():
            if info["model_name"] == DEFAULT_MODEL:
                return info
        # If default not found, return first available
        return list(FREE_MODELS.values())[0]
    
    return FREE_MODELS.get(model_key, list(FREE_MODELS.values())[0]) 