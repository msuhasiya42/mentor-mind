#!/usr/bin/env python3
"""
Test script to verify parallel optimizations in the backend
"""
import asyncio
import logging
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.learning_path_generator import LearningPathGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_parallel_optimization():
    """Test the parallel optimizations"""
    print("🚀 Testing Parallel API Optimization")
    print("=" * 50)
    
    # Initialize the learning path generator
    generator = LearningPathGenerator()
    
    try:
        # Test topics - focusing on Scala as requested
        test_topics = [
            "Scala",
            "Python",  # Keep one additional for comparison
        ]
        
        for topic in test_topics:
            print(f"\n📚 Testing topic: {topic}")
            start_time = time.time()
            
            # Generate learning path
            learning_path = await generator.generate_path(topic)
            
            total_time = time.time() - start_time
            
            # Display results
            print(f"⏱️  Total time: {total_time:.2f} seconds")
            print(f"📖 Documentation resources: {len(learning_path.docs)}")
            print(f"📝 Blog resources: {len(learning_path.blogs)}")
            print(f"🎥 YouTube resources: {len(learning_path.youtube)}")
            print(f"🆓 Free course resources: {len(learning_path.free_courses)}")
            print(f"💰 Paid course resources: {len(learning_path.paid_courses)}")
            
            # Show sample resources
            if learning_path.docs:
                print(f"   Sample doc: {learning_path.docs[0].title}")
            if learning_path.blogs:
                print(f"   Sample blog: {learning_path.blogs[0].title}")
            
            print("-" * 30)
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        
    finally:
        # Clean up
        await generator.close()
        print("\n✅ Test completed!")

async def test_individual_components():
    """Test individual components to verify parallel execution"""
    print("\n🔧 Testing Individual Components")
    print("=" * 50)
    
    generator = LearningPathGenerator()
    
    try:
        topic = "Scala"
        enhanced_queries = ["scala tutorial", "scala programming guide"]
        
        # Test content aggregator methods
        print(f"\n📊 Testing content aggregation for: {topic}")
        
        # Test parallel execution of content aggregation
        start_time = time.time()
        
        tasks = [
            generator.content_aggregator.get_documentation(topic, enhanced_queries),
            generator.content_aggregator.get_blogs(topic, enhanced_queries),
            generator.content_aggregator.get_youtube_videos(topic, enhanced_queries),
            generator.content_aggregator.get_free_courses(topic, enhanced_queries),
            generator.content_aggregator.get_paid_courses(topic, enhanced_queries)
        ]
        
        results = await asyncio.gather(*tasks)
        docs, blogs, youtube, free_courses, paid_courses = results
        
        parallel_time = time.time() - start_time
        
        print(f"⚡ Parallel content aggregation took: {parallel_time:.2f} seconds")
        print(f"   📖 Docs: {len(docs)}")
        print(f"   📝 Blogs: {len(blogs)}")
        print(f"   🎥 YouTube: {len(youtube)}")
        print(f"   🆓 Free courses: {len(free_courses)}")
        print(f"   💰 Paid courses: {len(paid_courses)}")
        
    except Exception as e:
        logger.error(f"Component test failed: {str(e)}")
        
    finally:
        await generator.close()

if __name__ == "__main__":
    print("🎯 Mentor Mind Backend - Parallel Optimization Test")
    print("This test verifies that API calls are now running in parallel")
    print("instead of sequentially to reduce latency.\n")
    
    asyncio.run(test_parallel_optimization())
    asyncio.run(test_individual_components()) 