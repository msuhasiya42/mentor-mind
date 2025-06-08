#!/usr/bin/env python3
"""
Simple test script for Mentor Mind backend
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.learning_path_generator import LearningPathGenerator

async def test_learning_path_generator():
    """Test the learning path generator"""
    print("🧪 Testing Mentor Mind Learning Path Generator...")
    
    generator = LearningPathGenerator()
    
    # Test with a simple topic
    test_topic = "React"
    print(f"📚 Generating learning path for: {test_topic}")
    
    try:
        learning_path = await generator.generate_path(test_topic)
        
        print(f"✅ Successfully generated learning path!")
        print(f"📖 Documentation resources: {len(learning_path.docs)}")
        print(f"📝 Blog resources: {len(learning_path.blogs)}")
        print(f"🎥 YouTube resources: {len(learning_path.youtube)}")
        print(f"🆓 Free courses: {len(learning_path.free_courses)}")
        print(f"💰 Paid courses: {len(learning_path.paid_courses)}")
        
        # Print some sample resources
        if learning_path.docs:
            print(f"\n📖 Sample documentation:")
            for doc in learning_path.docs[:2]:
                print(f"  - {doc.title}: {doc.url}")
        
        if learning_path.blogs:
            print(f"\n📝 Sample blogs:")
            for blog in learning_path.blogs[:2]:
                print(f"  - {blog.title}: {blog.url}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🧠 Mentor Mind Test Suite")
    print("=" * 40)
    
    success = await test_learning_path_generator()
    
    if success:
        print("\n✅ All tests passed! Mentor Mind is working correctly.")
        print("\n🚀 You can now start the full application with:")
        print("   ./start.sh")
        print("\n   Or manually:")
        print("   Backend:  cd backend && python main.py")
        print("   Frontend: cd frontend && npm run dev")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 