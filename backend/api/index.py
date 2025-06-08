import sys
import os
from pathlib import Path

# Ensure we can import from the current backend directory
current_dir = Path(__file__).parent.parent  # backend directory
sys.path.insert(0, str(current_dir))

try:
    # Import the FastAPI app from the same backend directory
    from main import app as fastapi_app
    print("✅ Successfully imported FastAPI app from backend/main.py")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Fallback to a simple FastAPI app if main import fails
    from fastapi import FastAPI
    fastapi_app = FastAPI()
    
    @fastapi_app.get("/")
    async def root():
        return {"message": "Fallback API - Main app import failed", "error": str(e)}

# This is the ASGI application that Vercel will serve
app = fastapi_app 