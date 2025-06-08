#!/usr/bin/env python3
"""
Debug script to test LLM search engine directly
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

from backend.services.search_engines import LLMSearchEngine
from backend.services.content_aggregator import ContentAggregator

async def test_llm_search_directly():
    """Test LLM search engine directly"""
    print("🔍 Testing LLM Search Engine Directly")
    print("=" * 50)
    
    search_engine = LLMSearchEngine()
    
    try:
        resources = await search_engine.search("AI")
        print(f"✅ LLM Search returned {len(resources)} resources")
        
        for i, resource in enumerate(resources[:3], 1):
            print(f"\n{i}. {resource.get('title', 'No title')}")
            print(f"   Type: {resource.get('type', 'unknown')}")
            print(f"   Platform: {resource.get('platform', 'unknown')}")
            print(f"   Persona: {resource.get('persona_source', 'unknown')}")
            print(f"   URL: {resource.get('url', 'no url')[:60]}...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await search_engine.close()

async def test_content_aggregator():
    """Test content aggregator"""
    print("\n\n📊 Testing Content Aggregator")
    print("=" * 50)
    
    aggregator = ContentAggregator()
    
    try:
        # Test getting all resources
        all_resources = await aggregator.get_all_resources("AI", [])
        
        print("Results from content aggregator:")
        for category, resources in all_resources.items():
            print(f"  {category}: {len(resources)} resources")
            if resources:
                print(f"    Sample: {resources[0].title}")
        
        # Test individual methods
        print("\nTesting individual methods:")
        docs = await aggregator.get_documentation("AI", [])
        print(f"  Documentation: {len(docs)} resources")
        
        blogs = await aggregator.get_blogs("AI", [])
        print(f"  Blogs: {len(blogs)} resources")
        
        youtube = await aggregator.get_youtube_videos("AI", [])
        print(f"  YouTube: {len(youtube)} resources")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        await aggregator.close()

if __name__ == "__main__":
    asyncio.run(test_llm_search_directly())
    asyncio.run(test_content_aggregator()) 