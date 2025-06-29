from typing import List, Dict

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# API Endpoints
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
OPENAI_API_BASE = "https://api.openai.com/v1"

# Default Model Configuration
DEFAULT_MODEL = "gemini-2.5-flash-lite-preview-06-17"  # Set this as default

# Model Configurations
MODELS: Dict[str, Dict] = {
    # Gemini Models
    "gemini-2.5-flash-lite-preview-06-17": {
        "provider": "gemini",
        "description": "Google's Gemini 2.5 Flash-Lite Preview (06-17) - Fastest, best for high-volume text",
        "max_tokens": 1048576,
        "good_for": ["text_generation", "resource_curation", "low-latency"],
        "endpoint": "/models/gemini-1.5-flash:generateContent"  # Uses same endpoint as other Gemini Flash models
    },
    "gemini-1.5-flash": {
        "provider": "gemini",
        "description": "Google's fastest model, great for general use",
        "max_tokens": 1048576,
        "good_for": ["general_chat", "coding", "reasoning", "summarization"],
        "endpoint": "/models/gemini-1.5-flash:generateContent"
    },
    "gemini-1.5-pro": {
        "provider": "gemini",
        "description": "Google's most capable model, great for complex tasks",
        "max_tokens": 1048576,
        "good_for": ["complex_tasks", "reasoning", "coding"],
        "endpoint": "/models/gemini-1.5-pro:generateContent"
    },

    # OpenAI Models
    "gpt-4o-mini": {
        "provider": "openai",
        "description": "OpenAI's efficient model, great balance of capability and speed",
        "max_tokens": 4096,
        "good_for": ["general_chat", "coding", "reasoning"],
        "endpoint": "/chat/completions"
    },
    "gpt-4o": {
        "provider": "openai",
        "description": "OpenAI's most capable model",
        "max_tokens": 128000,
        "good_for": ["complex_tasks", "reasoning", "coding"],
        "endpoint": "/chat/completions"
    }
}

# Fallback models in order of preference
FALLBACK_MODELS: List[str] = [
    "gemini-2.5-flash-lite-preview-06-17",  # Most generous free quota
    "gemini-1.5-flash",
    "gpt-4o-mini",
]

# Rate limiting info (important for free tier)
RATE_LIMIT_WARNING_THRESHOLD = 45  # Warn when approaching daily limit

# App metadata
APP_TITLE = "Mentor Mind API"
APP_DESCRIPTION = "AI-Powered Learning Path Generator with Expert AI Tutor"
APP_VERSION = "2.0.0"

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # React dev servers
    "https://ai-resource-curator.netlify.app",  # Production frontend
    "https://*.netlify.app"  # All Netlify preview deployments
]


# OpenRouter Headers Configuration
def get_openrouter_headers(api_key: str = None) -> dict:
    """Get headers for OpenRouter API requests"""
    if not api_key:
        return {"Content-Type": "application/json"}

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Mentor Mind"
    }


def get_model_info(model_key: str = None) -> dict:
    """Get information about a specific model or the default model"""
    if not model_key:
        return MODELS.get(DEFAULT_MODEL, list(MODELS.values())[0])
    if model_key in MODELS:
        return MODELS[model_key]
    return list(MODELS.values())[0]


def get_model_provider(model_key: str) -> str:
    """Get the provider for a given model key"""
    model_info = get_model_info(model_key)
    return model_info.get('provider', 'not found')