#!/usr/bin/env python3
"""
Test script to verify OpenRouter API setup and free models
Run this script to test your OpenRouter configuration before using the main application.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from config import settings
from services.ai_processor import AIProcessor

async def test_openrouter_setup():
    """Test OpenRouter API setup"""
    print("🧪 Testing OpenRouter Configuration...")
    print("=" * 50)
    
    # Test configuration
    if not settings.validate_config():
        print("\n❌ Configuration validation failed!")
        print("Please check your .env file and add your OpenRouter API key.")
        return False
    
    print("\n🤖 Testing AI Processor...")
    
    # Initialize AI processor
    ai_processor = AIProcessor()
    
    try:
        # Test 1: Generate search queries
        print("\n📝 Test 1: Generating search queries for 'Python programming'...")
        queries = await ai_processor.generate_search_queries("Python programming")
        
        if queries:
            print(f"✅ Generated {len(queries)} search queries:")
            for i, query in enumerate(queries, 1):
                print(f"   {i}. {query}")
        else:
            print("⚠️  No queries generated, but fallback should work")
        
        # Test 2: Content summarization
        print("\n📄 Test 2: Testing content summarization...")
        test_content = """
        Python is a high-level, interpreted programming language with dynamic semantics. 
        Its high-level built-in data structures, combined with dynamic typing and dynamic binding, 
        make it very attractive for Rapid Application Development, as well as for use as a scripting 
        or glue language to connect existing components together. Python's simple, easy to learn 
        syntax emphasizes readability and therefore reduces the cost of program maintenance.
        """
        
        summary = await ai_processor.summarize_content(test_content, max_length=100)
        print(f"✅ Content summarized: {summary}")
        
        # Test 3: Resource classification
        print("\n🔍 Test 3: Testing resource classification...")
        from services.ai_processor import Resource
        
        test_resource = Resource(
            title="Python Programming Tutorial for Beginners",
            url="https://example.com/python-tutorial",
            description="Complete guide to learning Python programming from scratch",
            platform="YouTube"
        )
        
        classification = await ai_processor.classify_resource_type(test_resource)
        print(f"✅ Resource classified as: {classification}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 Tips for using OpenRouter:")
        print("   - You have 50 free requests per day (1000 with $10 credit)")
        print("   - DeepSeek model is excellent for coding tasks")
        print("   - Rate limits reset daily")
        print("   - Consider adding $10 credit for higher limits")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False
        
    finally:
        # Cleanup
        await ai_processor.close()

async def test_specific_model(model_name: str):
    """Test a specific OpenRouter model"""
    print(f"\n🎯 Testing specific model: {model_name}")
    
    ai_processor = AIProcessor()
    
    try:
        # Test direct API call
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello and tell me your model name in one sentence."}
        ]
        
        response = await ai_processor._call_openrouter_api(messages, model_name, max_tokens=50)
        
        if response:
            print(f"✅ {model_name} responded: {response}")
            return True
        else:
            print(f"❌ {model_name} did not respond")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {model_name}: {str(e)}")
        return False
        
    finally:
        await ai_processor.close()

def print_setup_instructions():
    """Print setup instructions for users"""
    print("🚀 OpenRouter Setup Instructions")
    print("=" * 40)
    print("1. Go to https://openrouter.ai")
    print("2. Sign up for a free account")
    print("3. Get your API key from the dashboard")
    print("4. Create a .env file in the project root:")
    print("   OPENROUTER_API_KEY=your_key_here")
    print("\n💰 Optional: Add $10 credit for higher rate limits")
    print("   - Free tier: 50 requests/day")
    print("   - With $10 credit: 1000 requests/day")
    print("\n🎯 Available Free Models:")
    for key, model_info in settings.FREE_MODELS.items():
        print(f"   - {model_info['model_name']}")
        print(f"     {model_info['description']}")

async def main():
    """Main test function"""
    print("🌟 OpenRouter Free Models Test Suite")
    print("=" * 50)
    
    # Check if API key is set
    if not settings.OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment!")
        print_setup_instructions()
        return
    
    # Run basic tests
    success = await test_openrouter_setup()
    
    if success:
        print("\n🔍 Would you like to test individual models? (y/n)")
        try:
            choice = input().lower().strip()
            if choice == 'y':
                print("\nTesting individual models...")
                for model_name in settings.FALLBACK_MODELS:
                    await test_specific_model(model_name)
                    await asyncio.sleep(1)  # Small delay between tests
        except KeyboardInterrupt:
            print("\n👋 Testing interrupted by user")
        except:
            pass  # Handle any input issues gracefully
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 