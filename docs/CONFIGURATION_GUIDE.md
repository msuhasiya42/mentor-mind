# Configuration Guide

## Overview
The application configuration has been refactored to separate sensitive and non-sensitive settings for better security and maintainability.

## File Structure

### 🔒 `.env` file (Sensitive Data Only)
Contains only sensitive information that should not be committed to version control:
```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
```

### 📋 `constants.py` (Non-sensitive Configuration)
Contains all non-sensitive configuration that can be shared across the team:
- `DEFAULT_MODEL` - Current AI model to use
- `API_HOST` and `API_PORT` - Server configuration
- `FREE_MODELS` - Available free OpenRouter models
- `FALLBACK_MODELS` - Model priority order
- `ALLOWED_ORIGINS` - CORS configuration
- `APP_TITLE`, `APP_DESCRIPTION`, `APP_VERSION` - App metadata
- Helper functions for model info and headers

### ⚙️ `config.py` (Settings Management)
Handles environment variable loading and provides a unified settings interface:
- Loads sensitive data from `.env` file
- Imports constants from `constants.py`
- Provides validation and helper methods

## Usage

### Accessing Configuration
```python
from config import settings

# All configuration is available through the settings object
api_key = settings.OPENROUTER_API_KEY  # From .env
model = settings.DEFAULT_MODEL         # From constants.py
host = settings.API_HOST              # From constants.py
```

### Adding New Configuration

#### For Non-sensitive Settings:
1. Add the constant to `constants.py`
2. Import it in `config.py` and add to Settings class
3. Access via `settings.YOUR_CONSTANT`

#### For Sensitive Settings:
1. Add to `.env.example` with placeholder value
2. Add to Settings class in `config.py` using `os.getenv()`
3. Access via `settings.YOUR_SETTING`

## Benefits

✅ **Security**: Sensitive data stays in `.env` file  
✅ **Visibility**: Non-sensitive settings are easily discoverable  
✅ **Maintainability**: Clear separation of concerns  
✅ **Team Collaboration**: Constants are visible to all team members  
✅ **Backward Compatibility**: All existing code continues to work  

## Migration Notes

This refactoring maintains full backward compatibility. All existing code that accesses `settings.DEFAULT_MODEL`, `settings.API_HOST`, etc. continues to work without any changes. 