#!/usr/bin/env python3
"""
Test script to test the learning path generation API
"""
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.learning_path_generator import LearningPathGenerator

async def test_learning_path():
    """Test learning path generation"""
    print("🚀 Testing Learning Path Generation")
    print("=" * 50)
    
    generator = LearningPathGenerator()
    
    try:
        print("Generating learning path for 'Python programming'...")
        learning_path = await generator.generate_path("Python programming")
        
        print(f"\n📚 Results:")
        print(f"   Docs: {len(learning_path.docs)} resources")
        print(f"   Blogs: {len(learning_path.blogs)} resources")
        print(f"   YouTube: {len(learning_path.youtube)} resources")
        print(f"   Free Courses: {len(learning_path.free_courses)} resources")
        print(f"   Paid Courses: {len(learning_path.paid_courses)} resources")
        
        # Show first few resources
        if learning_path.docs:
            print(f"\n📖 Sample Documentation:")
            for i, doc in enumerate(learning_path.docs[:2], 1):
                print(f"   {i}. {doc.title}")
                if doc.url:
                    print(f"      URL: {doc.url}")
        
        if learning_path.blogs:
            print(f"\n📝 Sample Blogs:")
            for i, blog in enumerate(learning_path.blogs[:2], 1):
                print(f"   {i}. {blog.title}")
                if blog.url:
                    print(f"      URL: {blog.url}")
        
        print("\n✅ Learning path generation successful!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await generator.close()

if __name__ == "__main__":
    asyncio.run(test_learning_path()) 