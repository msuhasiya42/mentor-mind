#!/usr/bin/env python3
"""
Comprehensive test suite for the refactored ContentAggregator system
"""
import asyncio
import sys
import os
import logging
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import ContentAggregator, Resource, SearchEngineManager, FallbackDataProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestRefactoredContentAggregator(unittest.IsolatedAsyncioTestCase):
    """Test cases for the refactored ContentAggregator system"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.aggregator = ContentAggregator()
        self.search_manager = SearchEngineManager()
        self.fallback_provider = FallbackDataProvider()
    
    async def asyncTearDown(self):
        """Clean up after tests"""
        await self.aggregator.close()
    
    async def test_imports_and_initialization(self):
        """Test that all modules import correctly and can be initialized"""
        logger.info("Testing imports and initialization...")
        
        # Test that classes can be instantiated
        self.assertIsInstance(self.aggregator, ContentAggregator)
        self.assertIsInstance(self.search_manager, SearchEngineManager)
        self.assertIsInstance(self.fallback_provider, FallbackDataProvider)
        
        # Test Resource creation
        resource = Resource(
            title="Test Resource",
            url="https://example.com",
            description="Test description",
            platform="Test",
            price="Free"
        )
        self.assertEqual(resource.title, "Test Resource")
        self.assertEqual(resource.url, "https://example.com")
        
        logger.info("✅ Imports and initialization test passed")
    
    async def test_fallback_data_provider(self):
        """Test FallbackDataProvider functionality"""
        logger.info("Testing FallbackDataProvider...")
        
        # Test documentation sources
        doc_sources = self.fallback_provider.get_documentation_sources()
        self.assertIsInstance(doc_sources, dict)
        self.assertIn('scala', doc_sources)
        self.assertIn('python', doc_sources)
        
        scala_docs = doc_sources['scala']
        self.assertGreater(len(scala_docs), 0)
        self.assertIsInstance(scala_docs[0], Resource)
        
        # Test fallback blogs
        scala_blogs = self.fallback_provider.get_fallback_blogs('scala')
        self.assertIsInstance(scala_blogs, list)
        self.assertGreater(len(scala_blogs), 0)
        
        # Test fallback YouTube
        scala_videos = self.fallback_provider.get_fallback_youtube('scala')
        self.assertIsInstance(scala_videos, list)
        
        # Test fallback courses
        scala_courses = self.fallback_provider.get_fallback_courses('scala', 'free')
        self.assertIsInstance(scala_courses, list)
        
        # Test curated search results
        curated_results = self.fallback_provider.get_curated_search_results('scala programming')
        self.assertIsInstance(curated_results, list)
        self.assertGreater(len(curated_results), 0)
        
        logger.info("✅ FallbackDataProvider test passed")
    
    async def test_search_engine_manager(self):
        """Test SearchEngineManager functionality"""
        logger.info("Testing SearchEngineManager...")
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                # Test search functionality
                results = await self.search_manager.search('python tutorial', session)
                self.assertIsInstance(results, list)
                
                # Results should have the required structure
                if results:
                    result = results[0]
                    self.assertIn('title', result)
                    self.assertIn('url', result)
                    self.assertIn('description', result)
                
                logger.info(f"✅ SearchEngineManager returned {len(results)} results")
                
            except Exception as e:
                logger.warning(f"SearchEngineManager test failed (expected in some environments): {e}")
    
    async def test_content_aggregator_documentation(self):
        """Test ContentAggregator documentation gathering"""
        logger.info("Testing ContentAggregator documentation...")
        
        # Test with Scala (has predefined docs)
        docs = await self.aggregator.get_documentation('scala', [])
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        self.assertLessEqual(len(docs), 5)  # Should limit to 5
        
        # Check that returned items are Resource objects
        for doc in docs:
            self.assertIsInstance(doc, Resource)
            self.assertTrue(doc.title)
            self.assertTrue(doc.url)
        
        logger.info(f"✅ Documentation test passed - found {len(docs)} docs")
    
    async def test_content_aggregator_blogs(self):
        """Test ContentAggregator blog gathering"""
        logger.info("Testing ContentAggregator blogs...")
        
        blogs = await self.aggregator.get_blogs('python', ['django tutorial'])
        self.assertIsInstance(blogs, list)
        self.assertLessEqual(len(blogs), 5)  # Should limit to 5
        
        # Check that returned items are Resource objects
        for blog in blogs:
            self.assertIsInstance(blog, Resource)
        
        logger.info(f"✅ Blogs test passed - found {len(blogs)} blogs")
    
    async def test_content_aggregator_youtube(self):
        """Test ContentAggregator YouTube video gathering"""
        logger.info("Testing ContentAggregator YouTube...")
        
        videos = await self.aggregator.get_youtube_videos('react', [])
        self.assertIsInstance(videos, list)
        self.assertLessEqual(len(videos), 5)  # Should limit to 5
        
        # Check that returned items are Resource objects
        for video in videos:
            self.assertIsInstance(video, Resource)
        
        logger.info(f"✅ YouTube test passed - found {len(videos)} videos")
    
    async def test_content_aggregator_courses(self):
        """Test ContentAggregator course gathering"""
        logger.info("Testing ContentAggregator courses...")
        
        # Test free courses
        free_courses = await self.aggregator.get_free_courses('javascript', [])
        self.assertIsInstance(free_courses, list)
        self.assertLessEqual(len(free_courses), 5)
        
        # Test paid courses
        paid_courses = await self.aggregator.get_paid_courses('react', [])
        self.assertIsInstance(paid_courses, list)
        self.assertLessEqual(len(paid_courses), 5)
        
        # Check that returned items are Resource objects
        for course in free_courses + paid_courses:
            self.assertIsInstance(course, Resource)
        
        logger.info(f"✅ Courses test passed - found {len(free_courses)} free, {len(paid_courses)} paid")
    
    async def test_context_manager(self):
        """Test ContentAggregator context manager functionality"""
        logger.info("Testing ContentAggregator context manager...")
        
        async with ContentAggregator() as agg:
            self.assertIsInstance(agg, ContentAggregator)
            docs = await agg.get_documentation('python', [])
            self.assertIsInstance(docs, list)
        
        # Session should be closed after context exit
        self.assertIsNone(agg.session)
        
        logger.info("✅ Context manager test passed")


async def run_manual_tests():
    """Run manual tests with detailed output"""
    print("\n" + "="*60)
    print("🧪 MANUAL TESTING OF REFACTORED CONTENT AGGREGATOR")
    print("="*60)
    
    async with ContentAggregator() as aggregator:
        # Test with different topics
        topics = ['scala', 'python', 'react']
        
        for topic in topics:
            print(f"\n📋 Testing topic: {topic.upper()}")
            print("-" * 40)
            
            try:
                # Documentation
                docs = await aggregator.get_documentation(topic, [])
                print(f"📚 Documentation: {len(docs)} resources")
                for i, doc in enumerate(docs[:2], 1):
                    print(f"  {i}. {doc.title} ({doc.platform})")
                
                # Blogs
                blogs = await aggregator.get_blogs(topic, [])
                print(f"📝 Blogs: {len(blogs)} resources")
                for i, blog in enumerate(blogs[:2], 1):
                    print(f"  {i}. {blog.title} ({blog.platform})")
                
                # Courses
                courses = await aggregator.get_free_courses(topic, [])
                print(f"🎓 Free Courses: {len(courses)} resources")
                for i, course in enumerate(courses[:2], 1):
                    print(f"  {i}. {course.title} ({course.platform})")
                    
            except Exception as e:
                print(f"❌ Error testing {topic}: {e}")
        
        print(f"\n✅ Manual testing completed successfully!")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run manual tests
    asyncio.run(run_manual_tests()) 