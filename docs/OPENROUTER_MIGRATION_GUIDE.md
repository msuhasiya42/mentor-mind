# 🚀 OpenRouter Migration Guide

## Overview

This guide helps you migrate from Hugging Face to OpenRouter's free models. OpenRouter provides access to powerful AI models including DeepSeek (excellent for coding), completely free with reasonable rate limits.

## Why OpenRouter?

✅ **Free Access**: Multiple high-quality models available for free  
✅ **Better Reliability**: More stable than Hugging Face Inference API  
✅ **Excellent Coding Models**: DeepSeek is one of the best free models for coding tasks  
✅ **OpenAI Compatible**: Uses standard OpenAI API format  
✅ **Multiple Models**: Fallback to different models automatically  

## Migration Steps

### 1. Get OpenRouter API Key

1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

### 2. Update Environment Variables

Create or update your `.env` file:

```bash
# Replace Hugging Face token with OpenRouter key
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Set preferred model (default is DeepSeek)
DEFAULT_MODEL=deepseek/deepseek-chat-v3-0324:free
```

### 3. Install Dependencies

Update your Python environment:

```bash
# Install new dependencies
pip install -r backend/requirements.txt

# Or install manually
pip install openai>=1.55.0
```

### 4. Test Your Setup

Run the test script to verify everything works:

```bash
python test_openrouter_setup.py
```

## Available Free Models

| Model | Best For | Description |
|-------|----------|-------------|
| `deepseek/deepseek-chat-v3-0324:free` | **Coding, Reasoning** | High-performance model, excellent for programming tasks |
| `qwen/qwen-2.5-7b-instruct:free` | General Purpose | Good all-around model for various tasks |
| `meta-llama/llama-3.1-8b-instruct:free` | Text Generation | Meta's open-source model |
| `google/gemma-2-9b-it:free` | Instruction Following | Google's efficient model |

## Rate Limits

- **Free Tier**: 50 requests per day
- **With $10 Credit**: 1,000 requests per day
- **Recommendation**: Add $10 credit for comfortable usage

## Key Changes Made

### Configuration (`backend/config.py`)
- ✅ Replaced Hugging Face settings with OpenRouter configuration
- ✅ Added free model definitions with descriptions
- ✅ Implemented automatic fallback between models
- ✅ Added rate limiting awareness

### AI Processor (`backend/services/ai_processor.py`)
- ✅ Switched from Hugging Face API to OpenRouter
- ✅ Uses OpenAI-compatible message format
- ✅ Improved error handling and model fallbacks
- ✅ Better query generation using chat format
- ✅ Enhanced resource ranking with AI assistance

### Dependencies (`backend/requirements.txt`)
- ✅ Removed heavy ML dependencies (transformers, torch, sentence-transformers)
- ✅ Added lightweight openai library
- ✅ Reduced overall package size significantly

## Usage Examples

### Basic API Call
```python
from config import settings
from services.ai_processor import AIProcessor

ai_processor = AIProcessor()

# Generate search queries
queries = await ai_processor.generate_search_queries("Python programming")

# Summarize content
summary = await ai_processor.summarize_content(long_text, max_length=150)

# Classify resources
resource_type = await ai_processor.classify_resource_type(resource)
```

### Custom Model Selection
```python
# Use specific model
response = await ai_processor._call_openrouter_api(
    messages=[
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Explain Python classes"}
    ],
    model="deepseek/deepseek-chat-v3-0324:free"
)
```

## Performance Comparison

| Feature | Hugging Face | OpenRouter |
|---------|--------------|------------|
| **Reliability** | ⚠️ Often fails | ✅ Very stable |
| **Model Quality** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Setup Complexity** | ⚠️ Complex | ✅ Simple |
| **Rate Limits** | ⚠️ Unclear | ✅ Clear (50/day, 1000 with credit) |
| **Coding Tasks** | ⭐⭐ | ⭐⭐⭐⭐⭐ (DeepSeek) |
| **Dependencies** | ❌ Heavy | ✅ Lightweight |

## Troubleshooting

### Common Issues

**❌ "OpenRouter API key not found"**
- Check your `.env` file has `OPENROUTER_API_KEY=your_key`
- Ensure `.env` is in the project root directory

**❌ "Rate limit exceeded"**
- You've hit the 50 request daily limit
- Consider adding $10 credit for 1000 requests/day
- Limits reset daily

**❌ "Model not responding"**
- The system automatically tries fallback models
- Check your internet connection
- Verify your API key is valid

**❌ "Import errors"**
- Run `pip install -r backend/requirements.txt`
- Make sure you're in the right virtual environment

### Testing Individual Models

```bash
# Test specific models
python -c "
import asyncio
from backend.services.ai_processor import AIProcessor

async def test():
    ai = AIProcessor()
    result = await ai._call_openrouter_api([
        {'role': 'user', 'content': 'Hello, which model are you?'}
    ], 'deepseek/deepseek-chat-v3-0324:free')
    print(result)

asyncio.run(test())
"
```

## Best Practices

1. **Start with DeepSeek**: It's excellent for coding and technical tasks
2. **Add $10 Credit**: Dramatically improves the experience (1000 vs 50 requests/day)
3. **Monitor Usage**: Check your OpenRouter dashboard for usage stats
4. **Use Fallbacks**: The system automatically tries multiple models
5. **Cache Results**: Store responses locally when possible to reduce API calls

## Migration Checklist

- [ ] Get OpenRouter API key
- [ ] Update `.env` file
- [ ] Install new dependencies (`pip install -r backend/requirements.txt`)
- [ ] Run test script (`python test_openrouter_setup.py`)
- [ ] Optional: Add $10 credit for higher limits
- [ ] Test your application functionality
- [ ] Monitor usage in OpenRouter dashboard

## Support

- **OpenRouter Docs**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **Model Information**: Check the OpenRouter website for latest model availability
- **Rate Limits**: View current limits in your OpenRouter dashboard

## Summary

The migration to OpenRouter provides:
- ✅ Better reliability than Hugging Face
- ✅ Access to state-of-the-art models for free
- ✅ Simplified setup and maintenance
- ✅ Excellent performance for coding tasks
- ✅ Clear and reasonable rate limits

Your Mentor Mind application will be more stable and performant with OpenRouter! 