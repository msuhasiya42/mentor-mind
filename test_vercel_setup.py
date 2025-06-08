#!/usr/bin/env python3
"""
Test script to verify Vercel setup works locally
Run this to test your setup before deploying to Vercel
"""

import sys
import os
import asyncio
import json

# Test import of the API handler
try:
    from backend.api.index import app
    print("✅ Successfully imported FastAPI app from backend/api/index.py")
except ImportError as e:
    print(f"❌ Failed to import FastAPI app: {e}")
    sys.exit(1)

# Test if the app is properly configured
try:
    # Check if it's a FastAPI app
    from fastapi import FastAPI
    if isinstance(app, FastAPI):
        print("✅ App is a valid FastAPI instance")
    else:
        print(f"❌ App is not a FastAPI instance, got: {type(app)}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error checking app type: {e}")
    sys.exit(1)

# Test basic endpoints
async def test_endpoints():
    """Test the basic endpoints"""
    from fastapi.testclient import TestClient
    
    try:
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Root endpoint (/) works")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint (/health) works")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   OpenRouter API: {data.get('openrouter_api')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

if __name__ == "__main__":
    print("🧪 Testing Vercel setup for Mentor Mind API...")
    print("=" * 50)
    
    # Run endpoint tests
    asyncio.run(test_endpoints())
    
    print("=" * 50)
    print("🎉 Setup test completed!")
    print("\nNext steps:")
    print("1. Commit and push your code to Git")
    print("2. Deploy to Vercel using the dashboard or CLI")
    print("3. Set your OPENROUTER_API_KEY in Vercel environment variables")
    print("4. Test your deployed API endpoints")
    print("\nSee DEPLOYMENT.md for detailed instructions!") 