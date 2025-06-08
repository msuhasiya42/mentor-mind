"""
FastAPI entry point for Vercel deployment
Similar structure to server.js in advanced-task-manager
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from main import app

# This is the ASGI application that Vercel will serve
# Export the app for Vercel (must be named 'app')
app = app 