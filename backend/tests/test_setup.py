#!/usr/bin/env python3
"""
Test script to verify Hugging Face integration setup
"""
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import settings
    from services.ai_processor import AIProcessor
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_config():
    """Test configuration"""
    print("\n📋 Testing Configuration...")
    
    try:
        if settings.HUGGINGFACE_API_TOKEN:
            print("✅ Hugging Face API token found")
            print(f"✅ API Host: {settings.API_HOST}")
            print(f"✅ API Port: {settings.API_PORT}")
            print(f"✅ Text Generation Model: {settings.TEXT_GENERATION_MODEL}")
        else:
            print("❌ Hugging Face API token not found in environment variables")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    return True

async def test_ai_processor():
    """Test AI processor"""
    print("\n🤖 Testing AI Processor...")
    
    ai_processor = AIProcessor()
    
    try:
        # Test search query generation
        queries = await ai_processor.generate_search_queries("Python programming")
        print(f"✅ Generated {len(queries)} search queries:")
        for i, query in enumerate(queries, 1):
            print(f"   {i}. {query}")
        
        # Clean up
        await ai_processor.close()
        print("✅ AI processor cleanup successful")
        
    except Exception as e:
        print(f"❌ AI processor error: {e}")
        return False
    
    return True

async def test_api_health():
    """Test API health check (if server is running)"""
    print("\n🏥 Testing API Health...")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://{settings.API_HOST}:{settings.API_PORT}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ API is running and healthy")
                        print(f"   Status: {data.get('status')}")
                        print(f"   Hugging Face API: {data.get('huggingface_api')}")
                        print(f"   Version: {data.get('version')}")
                        return True
            except aiohttp.ClientConnectorError:
                print("ℹ️  API server is not running (this is OK for setup testing)")
                return True
                
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

async def main():
    print("🚀 Mentor Mind Backend Setup Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = await test_config()
    
    # Test AI processor
    ai_ok = await test_ai_processor() if config_ok else False
    
    # Test API health
    api_ok = await test_api_health()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   AI Processor: {'✅ PASS' if ai_ok else '❌ FAIL'}")
    print(f"   API Health: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if config_ok and ai_ok:
        print("\n🎉 Setup is ready! You can now start the server with:")
        print("   python main.py")
    else:
        print("\n⚠️  Please fix the issues above before running the server.")
        print("\n💡 Make sure you have:")
        print("   1. Created a .env file with your Hugging Face API token")
        print("   2. Installed all dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    asyncio.run(main()) 