# Mentor Mind Backend

AI-Powered Learning Path Generator using FastAPI and Hugging Face

## 🚀 Features

- ✅ **AI-Enhanced Search Queries**: Uses Hugging Face API for intelligent search query generation
- ✅ **Multi-Source Content Aggregation**: Gathers resources from docs, blogs, YouTube, and courses
- ✅ **Smart Resource Ranking**: AI-powered relevance scoring and ranking
- ✅ **Graceful Fallback**: Works even when external APIs are unavailable
- ✅ **RESTful API**: Clean FastAPI endpoints with automatic documentation
- ✅ **Virtual Environment**: Isolated dependencies for clean development

## 📋 Prerequisites

- Python 3.8+
- Hugging Face Account (free)
- pip package manager

## 🛠️ Setup Instructions

### 1. Create Virtual Environment
```bash
cd mentor-mind/backend
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get Hugging Face API Token
1. Go to [https://huggingface.co/](https://huggingface.co/)
2. Create a free account or sign in
3. Go to Settings → Access Tokens
4. Create a new token with "Read" permissions
5. Copy the token (starts with `hf_`)

### 4. Configure Environment
```bash
# Create .env file from template
cp env.example .env

# Edit .env file and add your token
nano .env  # or use your preferred editor
```

Your `.env` file should look like:
```bash
HUGGINGFACE_API_TOKEN=hf_your_actual_token_here
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_MODEL=gpt2
TEXT_GENERATION_MODEL=tiiuae/falcon-7b-instruct
```

### 5. Test Setup
```bash
python test_setup.py
```

## 🚀 Running the Server

### Option 1: Using the startup script (Recommended)
```bash
python start_server.py
```

### Option 2: Direct uvicorn
```bash
python main.py
```

### Option 3: Using uvicorn command
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Endpoints

### Health Check
```bash
GET /health
```

### Generate Learning Path
```bash
POST /generate-learning-path
Content-Type: application/json

{
    "topic": "Python programming"
}
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

### Test Setup
```bash
python test_setup.py
```

### Test Learning Path Generation
```bash
python test_api.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Generate learning path
curl -X POST "http://localhost:8000/generate-learning-path" \
     -H "Content-Type: application/json" \
     -d '{"topic": "React.js"}'
```

## 🏗️ Project Structure

```
backend/
├── main.py                    # FastAPI application
├── config.py                  # Configuration management
├── start_server.py           # Server startup script
├── test_setup.py             # Setup validation
├── test_api.py               # API testing
├── requirements.txt          # Dependencies
├── .env                      # Environment variables (create this)
├── env.example               # Environment template
├── venv/                     # Virtual environment
└── services/
    ├── __init__.py
    ├── ai_processor.py       # Hugging Face integration
    ├── content_aggregator.py # Content collection
    └── learning_path_generator.py  # Main logic
```

## 🔧 PyCharm Setup

1. **Open Project**: Open the `mentor-mind/backend` folder in PyCharm
2. **Configure Interpreter**:
   - Go to Settings → Project → Python Interpreter
   - Click the gear icon → Add → Existing Environment
   - Select `mentor-mind/backend/venv/bin/python`
3. **Run Configuration**:
   - Create a new Python run configuration
   - Script path: `start_server.py`
   - Working directory: `mentor-mind/backend`

## 🔍 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
```

**2. Hugging Face API Errors**
- Check your API token in `.env` file
- Verify token has "Read" permissions
- Some models may be temporarily unavailable (fallback will work)

**3. Port Already in Use**
```bash
# Change port in .env file
API_PORT=8001
```

**4. Dependencies Issues**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## 📊 API Response Example

```json
{
    "topic": "Python programming",
    "learning_path": {
        "docs": [
            {
                "title": "Python Tutorial",
                "url": "https://docs.python.org/3/tutorial/",
                "description": "Official Python tutorial",
                "platform": "Python.org",
                "price": "Free"
            }
        ],
        "blogs": [...],
        "youtube": [...],
        "free_courses": [...],
        "paid_courses": [...]
    }
}
```

## 🌟 Next Steps

1. **Frontend Integration**: Connect with your React frontend
2. **Database**: Add persistence for learning paths
3. **User Authentication**: Add user accounts and saved paths
4. **Enhanced AI**: Implement more sophisticated AI models
5. **Caching**: Add Redis for better performance

## 📄 License

This project is part of the Mentor Mind application.

---

**Happy Learning! 🎓** 