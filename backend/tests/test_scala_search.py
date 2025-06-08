#!/usr/bin/env python3
import asyncio
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import ContentAggregator, SearchEngineManager, FallbackDataProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scala_search():
    """Test the refactored ContentAggregator with Scala searches"""
    print("Testing Scala search with refactored modular functionality...")
    
    # Test individual components first
    print("=" * 50)
    print("1. Testing FallbackDataProvider...")
    fallback_provider = FallbackDataProvider()
    
    # Test documentation sources
    doc_sources = fallback_provider.get_documentation_sources()
    scala_docs = doc_sources.get('scala', [])
    print(f"Predefined Scala docs: {len(scala_docs)}")
    for i, doc in enumerate(scala_docs[:3]):
        print(f"  {i+1}. {doc.title} - {doc.url}")
    
    # Test fallback blogs
    scala_blogs = fallback_provider.get_fallback_blogs('scala')
    print(f"Fallback Scala blogs: {len(scala_blogs)}")
    for i, blog in enumerate(scala_blogs[:3]):
        print(f"  {i+1}. {blog.title} - {blog.url}")
    
    # Test curated search results
    curated_results = fallback_provider.get_curated_search_results('scala programming tutorial')
    print(f"Curated search results: {len(curated_results)}")
    for i, result in enumerate(curated_results[:3]):
        print(f"  {i+1}. {result.get('title', 'N/A')} - {result.get('url', 'N/A')}")
    
    print("=" * 50)
    print("2. Testing SearchEngineManager...")
    search_manager = SearchEngineManager()
    
    import aiohttp
    async with aiohttp.ClientSession() as session:
        try:
            search_results = await search_manager.search('scala programming tutorial', session)
            print(f"Search engine results: {len(search_results)}")
            for i, result in enumerate(search_results[:3]):
                print(f"  {i+1}. {result.get('title', 'N/A')}")
                print(f"     URL: {result.get('url', 'N/A')}")
                print(f"     Description: {result.get('description', 'N/A')[:100]}...")
        except Exception as e:
            print(f"Search engine error: {e}")
    
    print("=" * 50)
    print("3. Testing full ContentAggregator functionality...")
    
    async with ContentAggregator() as aggregator:
        try:
            # Test documentation search
            print("📚 Testing documentation search...")
            docs = await aggregator.get_documentation('scala', [])
            print(f"Documentation search found {len(docs)} results")
            
            for i, doc in enumerate(docs[:3]):
                print(f"  {i+1}. {doc.title}")
                print(f"     URL: {doc.url}")
                print(f"     Platform: {doc.platform}")
                print()
            
            # Test blog search
            print("📝 Testing blog search...")
            blogs = await aggregator.get_blogs('scala', ['functional programming'])
            print(f"Blog search found {len(blogs)} results")
            
            for i, blog in enumerate(blogs[:3]):
                print(f"  {i+1}. {blog.title}")
                print(f"     URL: {blog.url}")
                print(f"     Platform: {blog.platform}")
                print()
            
            # Test YouTube search
            print("🎥 Testing YouTube search...")
            videos = await aggregator.get_youtube_videos('scala', [])
            print(f"YouTube search found {len(videos)} results")
            
            for i, video in enumerate(videos[:3]):
                print(f"  {i+1}. {video.title}")
                print(f"     URL: {video.url}")
                print(f"     Platform: {video.platform}")
                print()
            
            # Test free courses search
            print("🆓 Testing free courses search...")
            free_courses = await aggregator.get_free_courses('scala', [])
            print(f"Free courses search found {len(free_courses)} results")
            
            for i, course in enumerate(free_courses[:3]):
                print(f"  {i+1}. {course.title}")
                print(f"     URL: {course.url}")
                print(f"     Platform: {course.platform}")
                print(f"     Price: {course.price}")
                print()
            
            # Test paid courses search
            print("💰 Testing paid courses search...")
            paid_courses = await aggregator.get_paid_courses('scala', [])
            print(f"Paid courses search found {len(paid_courses)} results")
            
            for i, course in enumerate(paid_courses[:3]):
                print(f"  {i+1}. {course.title}")
                print(f"     URL: {course.url}")
                print(f"     Platform: {course.platform}")
                print(f"     Price: {course.price}")
                print()
            
            print("✅ All ContentAggregator tests completed successfully!")
            
        except Exception as e:
            print(f"❌ ContentAggregator test error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scala_search()) 