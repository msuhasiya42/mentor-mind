#!/usr/bin/env python3
"""
Example usage of the refactored ContentAggregator service

This demonstrates how to use the modular content aggregation system
with proper async context management.
"""
import asyncio
import logging
from content_aggregator import ContentAggregator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_content_aggregation():
    """Demonstrate content aggregation for different resource types"""
    
    # Create aggregator with context manager for proper cleanup
    async with ContentAggregator() as aggregator:
        topic = "scala"
        enhanced_queries = ["functional programming scala", "scala tutorial"]
        
        # Get different types of resources
        print(f"\n=== Content Aggregation Demo for '{topic}' ===\n")
        
        # Documentation
        print("📚 Getting documentation...")
        docs = await aggregator.get_documentation(topic, enhanced_queries)
        for i, doc in enumerate(docs, 1):
            print(f"  {i}. {doc.title} ({doc.platform})")
            print(f"     URL: {doc.url}")
            print(f"     Description: {doc.description[:100]}...")
        
        # Blogs
        print("\n📝 Getting blog posts...")
        blogs = await aggregator.get_blogs(topic, enhanced_queries)
        for i, blog in enumerate(blogs, 1):
            print(f"  {i}. {blog.title} ({blog.platform})")
            print(f"     URL: {blog.url}")
        
        # YouTube videos
        print("\n🎥 Getting YouTube videos...")
        videos = await aggregator.get_youtube_videos(topic, enhanced_queries)
        for i, video in enumerate(videos, 1):
            print(f"  {i}. {video.title} ({video.platform})")
            print(f"     URL: {video.url}")
        
        # Free courses
        print("\n🆓 Getting free courses...")
        free_courses = await aggregator.get_free_courses(topic, enhanced_queries)
        for i, course in enumerate(free_courses, 1):
            print(f"  {i}. {course.title} ({course.platform}) - {course.price}")
            print(f"     URL: {course.url}")
        
        # Paid courses
        print("\n💰 Getting paid courses...")
        paid_courses = await aggregator.get_paid_courses(topic, enhanced_queries)
        for i, course in enumerate(paid_courses, 1):
            print(f"  {i}. {course.title} ({course.platform}) - {course.price}")
            print(f"     URL: {course.url}")


async def demo_individual_components():
    """Demonstrate using individual components separately"""
    from search_engines import SearchEngineManager
    from fallback_data import FallbackDataProvider
    import aiohttp
    
    print("\n=== Individual Components Demo ===\n")
    
    # Search engine manager
    search_manager = SearchEngineManager()
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing search manager...")
        results = await search_manager.search("python tutorial", session)
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.get('title', 'N/A')}")
    
    # Fallback data provider
    fallback_provider = FallbackDataProvider()
    print("\n📋 Testing fallback data provider...")
    
    # Get predefined documentation sources
    doc_sources = fallback_provider.get_documentation_sources()
    scala_docs = doc_sources.get('scala', [])
    print(f"Found {len(scala_docs)} predefined Scala documentation sources:")
    for doc in scala_docs[:2]:
        print(f"  • {doc.title}: {doc.url}")
    
    # Get fallback blogs
    blogs = fallback_provider.get_fallback_blogs("python")
    print(f"\nFound {len(blogs)} fallback Python blogs:")
    for blog in blogs:
        print(f"  • {blog.title}: {blog.url}")


if __name__ == "__main__":
    print("Content Aggregator Refactoring Demo")
    print("="*50)
    
    # Run the demos
    asyncio.run(demo_content_aggregation())
    asyncio.run(demo_individual_components())
    
    print("\n✅ Demo completed successfully!")
    print("\nKey improvements from refactoring:")
    print("• Separation of concerns with dedicated modules")
    print("• Better error handling and logging")
    print("• Reusable components (search engines, fallback data)")
    print("• Cleaner, more maintainable code structure")
    print("• Proper async context management") 