#!/usr/bin/env python3
import asyncio
import sys
import logging
from services.content_aggregator import ContentAggregator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scala_search():
    aggregator = ContentAggregator()
    try:
        print("Testing Scala search with fallback functionality...")
        
        # Test DuckDuckGo search first
        print("=" * 50)
        print("1. Testing DuckDuckGo search...")
        session = await aggregator._get_session()
        results = await aggregator._search_duckduckgo('scala programming tutorial', session)
        print(f"DuckDuckGo search found {len(results)} results")
        
        for i, result in enumerate(results[:3]):
            print(f"{i+1}. {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Description: {result.get('description', 'N/A')[:100]}...")
            print()
        
        # Test fallback search methods individually
        print("=" * 50)
        print("2. Testing SearX search...")
        try:
            searx_results = await aggregator._search_searx('scala programming tutorial')
            print(f"SearX search found {len(searx_results)} results")
            
            for i, result in enumerate(searx_results[:3]):
                print(f"{i+1}. {result.get('title', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Description: {result.get('description', 'N/A')[:100]}...")
                print()
        except Exception as e:
            print(f"SearX search error: {e}")
        
        print("=" * 50)
        print("3. Testing Bing browser search...")
        try:
            bing_results = await aggregator._search_bing_browser('scala programming tutorial')
            print(f"Bing browser search found {len(bing_results)} results")
            
            for i, result in enumerate(bing_results[:3]):
                print(f"{i+1}. {result.get('title', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Description: {result.get('description', 'N/A')[:100]}...")
                print()
        except Exception as e:
            print(f"Bing browser search error: {e}")
        
        print("=" * 50)
        print("4. Testing Startpage search...")
        try:
            startpage_results = await aggregator._search_startpage('scala programming tutorial')
            print(f"Startpage search found {len(startpage_results)} results")
            
            for i, result in enumerate(startpage_results[:3]):
                print(f"{i+1}. {result.get('title', 'N/A')}")
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Description: {result.get('description', 'N/A')[:100]}...")
                print()
        except Exception as e:
            print(f"Startpage search error: {e}")
        
        print("=" * 50)
        print("5. Testing curated fallback results...")
        curated_results = aggregator._get_curated_search_results('scala programming tutorial')
        print(f"Curated search found {len(curated_results)} results")
        
        for i, result in enumerate(curated_results):
            print(f"{i+1}. {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Description: {result.get('description', 'N/A')}")
            print()
        
        print("=" * 50)
        print("6. Testing full fallback chain...")
        fallback_results = await aggregator._search_fallback('scala programming tutorial', session)
        print(f"Fallback chain found {len(fallback_results)} results")
        
        for i, result in enumerate(fallback_results[:5]):
            print(f"{i+1}. {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Description: {result.get('description', 'N/A')[:100]}...")
            print()
        
        # Test full documentation search
        print("=" * 50)
        print("7. Testing full documentation search...")
        docs = await aggregator.get_documentation('scala', [])
        print(f"Documentation search found {len(docs)} results")
        
        for i, doc in enumerate(docs):
            print(f"{i+1}. {doc.title}")
            print(f"   URL: {doc.url}")
            print(f"   Platform: {doc.platform}")
            print()
            
        # Test blog search
        print("=" * 50)
        print("8. Testing blog search...")
        blogs = await aggregator.get_blogs('scala', [])
        print(f"Blog search found {len(blogs)} results")
        
        for i, blog in enumerate(blogs):
            print(f"{i+1}. {blog.title}")
            print(f"   URL: {blog.url}")
            print(f"   Platform: {blog.platform}")
            print()
        
        # Test YouTube search
        print("=" * 50)
        print("9. Testing YouTube search...")
        videos = await aggregator.get_youtube_videos('scala', [])
        print(f"YouTube search found {len(videos)} results")
        
        for i, video in enumerate(videos):
            print(f"{i+1}. {video.title}")
            print(f"   URL: {video.url}")
            print(f"   Platform: {video.platform}")
            print()
            
        # Test course search
        print("=" * 50)
        print("10. Testing free courses search...")
        courses = await aggregator.get_free_courses('scala', [])
        print(f"Free courses search found {len(courses)} results")
        
        for i, course in enumerate(courses):
            print(f"{i+1}. {course.title}")
            print(f"   URL: {course.url}")
            print(f"   Platform: {course.platform}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await aggregator.close()

if __name__ == "__main__":
    asyncio.run(test_scala_search()) 