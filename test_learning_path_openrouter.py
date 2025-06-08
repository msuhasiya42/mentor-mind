#!/usr/bin/env python3
"""
Comprehensive test suite for Learning Path Generator with OpenRouter integration
Tests the full end-to-end functionality of the learning path generation system.
"""

import asyncio
import sys
import os
import json
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from config import settings
from services.learning_path_generator import LearningPathGenerator
from services.ai_processor import AIProcessor

class LearningPathTester:
    def __init__(self):
        self.learning_path_generator = None
        self.ai_processor = None
        self.test_results = {}
        
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        
        # Validate configuration
        if not settings.validate_config():
            print("❌ Configuration validation failed!")
            return False
            
        # Initialize services
        self.learning_path_generator = LearningPathGenerator()
        self.ai_processor = AIProcessor()
        
        print("✅ Test environment setup complete")
        return True
    
    async def test_openrouter_connection(self):
        """Test basic OpenRouter API connection"""
        print("\n🔌 Testing OpenRouter API connection...")
        
        try:
            # Test direct API call
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Please respond with 'OpenRouter connection successful'"}
            ]
            
            response = await self.ai_processor._call_openrouter_api(messages, max_tokens=50)
            
            if response and "successful" in response.lower():
                print("✅ OpenRouter API connection successful")
                self.test_results["openrouter_connection"] = {"status": "success", "response": response}
                return True
            else:
                print(f"⚠️  OpenRouter responded but unexpected content: {response}")
                self.test_results["openrouter_connection"] = {"status": "partial", "response": response}
                return True
                
        except Exception as e:
            print(f"❌ OpenRouter API connection failed: {str(e)}")
            self.test_results["openrouter_connection"] = {"status": "failed", "error": str(e)}
            return False
    
    async def test_query_generation(self):
        """Test AI-powered search query generation"""
        print("\n📝 Testing AI-powered search query generation...")
        
        test_topics = ["Python programming", "React development", "Machine Learning"]
        
        for topic in test_topics:
            try:
                start_time = time.time()
                queries = await self.ai_processor.generate_search_queries(topic)
                duration = time.time() - start_time
                
                if queries and len(queries) > 0:
                    print(f"✅ Generated {len(queries)} queries for '{topic}' in {duration:.2f}s:")
                    for i, query in enumerate(queries[:3], 1):  # Show first 3
                        print(f"   {i}. {query}")
                    
                    self.test_results[f"query_generation_{topic.replace(' ', '_')}"] = {
                        "status": "success",
                        "query_count": len(queries),
                        "duration": duration,
                        "sample_queries": queries[:3]
                    }
                else:
                    print(f"⚠️  No queries generated for '{topic}', using fallback")
                    self.test_results[f"query_generation_{topic.replace(' ', '_')}"] = {
                        "status": "fallback",
                        "duration": duration
                    }
                    
            except Exception as e:
                print(f"❌ Query generation failed for '{topic}': {str(e)}")
                self.test_results[f"query_generation_{topic.replace(' ', '_')}"] = {
                    "status": "failed",
                    "error": str(e)
                }
    
    async def test_resource_ranking(self):
        """Test AI-powered resource ranking"""
        print("\n📊 Testing AI-powered resource ranking...")
        
        try:
            # Create some sample resources
            from services.ai_processor import Resource
            
            sample_resources = [
                Resource(
                    title="Python Official Tutorial",
                    url="https://docs.python.org/3/tutorial/",
                    description="Official Python tutorial covering all basics",
                    platform="Official Documentation"
                ),
                Resource(
                    title="Python Crash Course Video",
                    url="https://youtube.com/example",
                    description="Quick Python tutorial video",
                    platform="YouTube"
                ),
                Resource(
                    title="Advanced Python Tricks",
                    url="https://blog.example.com/python",
                    description="Advanced Python programming techniques",
                    platform="Blog"
                )
            ]
            
            start_time = time.time()
            ranked_resources = await self.ai_processor.rank_resources(sample_resources, "Python programming")
            duration = time.time() - start_time
            
            if ranked_resources:
                print(f"✅ Successfully ranked {len(ranked_resources)} resources in {duration:.2f}s:")
                for i, resource in enumerate(ranked_resources, 1):
                    print(f"   {i}. {resource.title} ({resource.platform})")
                
                self.test_results["resource_ranking"] = {
                    "status": "success",
                    "resource_count": len(ranked_resources),
                    "duration": duration,
                    "top_resource": ranked_resources[0].title if ranked_resources else None
                }
            else:
                print("⚠️  Resource ranking returned empty list")
                self.test_results["resource_ranking"] = {
                    "status": "empty",
                    "duration": duration
                }
                
        except Exception as e:
            print(f"❌ Resource ranking failed: {str(e)}")
            self.test_results["resource_ranking"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def test_content_summarization(self):
        """Test content summarization capability"""
        print("\n📄 Testing content summarization...")
        
        try:
            test_content = """
            Python is a high-level, interpreted programming language with dynamic semantics. 
            Its high-level built-in data structures, combined with dynamic typing and dynamic binding, 
            make it very attractive for Rapid Application Development, as well as for use as a scripting 
            or glue language to connect existing components together. Python's simple, easy to learn 
            syntax emphasizes readability and therefore reduces the cost of program maintenance. 
            Python supports modules and packages, which encourages program modularity and code reuse.
            """
            
            start_time = time.time()
            summary = await self.ai_processor.summarize_content(test_content, max_length=100)
            duration = time.time() - start_time
            
            if summary and len(summary) <= 120:  # Allow some margin
                print(f"✅ Content summarized successfully in {duration:.2f}s:")
                print(f"   Original: {len(test_content)} chars")
                print(f"   Summary: {len(summary)} chars")
                print(f"   Content: {summary}")
                
                self.test_results["content_summarization"] = {
                    "status": "success",
                    "original_length": len(test_content),
                    "summary_length": len(summary),
                    "duration": duration,
                    "compression_ratio": len(summary) / len(test_content)
                }
            else:
                print(f"⚠️  Summarization result may be incorrect: {len(summary)} chars")
                self.test_results["content_summarization"] = {
                    "status": "warning",
                    "summary_length": len(summary),
                    "duration": duration
                }
                
        except Exception as e:
            print(f"❌ Content summarization failed: {str(e)}")
            self.test_results["content_summarization"] = {
                "status": "failed",
                "error": str(e)
            }
    
    async def test_full_learning_path_generation(self):
        """Test complete learning path generation"""
        print("\n🎯 Testing full learning path generation...")
        
        test_topics = ["React", "Python basics"]
        
        for topic in test_topics:
            try:
                print(f"\n   Testing topic: '{topic}'")
                start_time = time.time()
                
                learning_path = await self.learning_path_generator.generate_path(topic)
                duration = time.time() - start_time
                
                # Count total resources
                total_resources = (
                    len(learning_path.docs) + 
                    len(learning_path.blogs) + 
                    len(learning_path.youtube) + 
                    len(learning_path.free_courses) + 
                    len(learning_path.paid_courses)
                )
                
                if total_resources > 0:
                    print(f"   ✅ Generated learning path with {total_resources} resources in {duration:.2f}s:")
                    print(f"      📖 Docs: {len(learning_path.docs)}")
                    print(f"      📝 Blogs: {len(learning_path.blogs)}")
                    print(f"      🎥 YouTube: {len(learning_path.youtube)}")
                    print(f"      🆓 Free Courses: {len(learning_path.free_courses)}")
                    print(f"      💰 Paid Courses: {len(learning_path.paid_courses)}")
                    
                    # Show sample resource
                    if learning_path.docs:
                        sample = learning_path.docs[0]
                        print(f"      Sample doc: {sample.title}")
                    elif learning_path.blogs:
                        sample = learning_path.blogs[0]
                        print(f"      Sample blog: {sample.title}")
                    
                    self.test_results[f"learning_path_{topic.replace(' ', '_')}"] = {
                        "status": "success",
                        "total_resources": total_resources,
                        "duration": duration,
                        "breakdown": {
                            "docs": len(learning_path.docs),
                            "blogs": len(learning_path.blogs),
                            "youtube": len(learning_path.youtube),
                            "free_courses": len(learning_path.free_courses),
                            "paid_courses": len(learning_path.paid_courses)
                        }
                    }
                else:
                    print(f"   ⚠️  No resources found for '{topic}'")
                    self.test_results[f"learning_path_{topic.replace(' ', '_')}"] = {
                        "status": "empty",
                        "duration": duration
                    }
                    
            except Exception as e:
                print(f"   ❌ Learning path generation failed for '{topic}': {str(e)}")
                self.test_results[f"learning_path_{topic.replace(' ', '_')}"] = {
                    "status": "failed",
                    "error": str(e)
                }
    
    async def test_model_fallbacks(self):
        """Test model fallback mechanism"""
        print("\n🔄 Testing model fallback mechanism...")
        
        try:
            # Test each model individually
            for i, model in enumerate(settings.FALLBACK_MODELS):
                try:
                    print(f"   Testing model {i+1}: {model}")
                    
                    messages = [
                        {"role": "user", "content": "Say 'Model working' in exactly two words."}
                    ]
                    
                    response = await self.ai_processor._call_openrouter_api(messages, model, max_tokens=20)
                    
                    if response:
                        print(f"   ✅ {model}: {response.strip()}")
                        if f"model_fallback_test" not in self.test_results:
                            self.test_results["model_fallback_test"] = {}
                        self.test_results["model_fallback_test"][model] = {"status": "success", "response": response.strip()}
                    else:
                        print(f"   ❌ {model}: No response")
                        if f"model_fallback_test" not in self.test_results:
                            self.test_results["model_fallback_test"] = {}
                        self.test_results["model_fallback_test"][model] = {"status": "no_response"}
                        
                except Exception as e:
                    print(f"   ❌ {model}: Error - {str(e)}")
                    if f"model_fallback_test" not in self.test_results:
                        self.test_results["model_fallback_test"] = {}
                    self.test_results["model_fallback_test"][model] = {"status": "error", "error": str(e)}
                
                # Small delay between model tests
                await asyncio.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Model fallback testing failed: {str(e)}")
            self.test_results["model_fallback_test"] = {"status": "failed", "error": str(e)}
    
    async def cleanup(self):
        """Cleanup test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        try:
            if self.learning_path_generator:
                await self.learning_path_generator.close()
            if self.ai_processor:
                await self.ai_processor.close()
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warning_tests = 0
        
        for test_name, result in self.test_results.items():
            total_tests += 1
            status = result.get("status", "unknown")
            
            if status == "success":
                print(f"✅ {test_name}: PASSED")
                passed_tests += 1
            elif status in ["failed", "error"]:
                print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                failed_tests += 1
            elif status in ["warning", "partial", "empty", "fallback"]:
                print(f"⚠️  {test_name}: WARNING - {status}")
                warning_tests += 1
            else:
                print(f"❓ {test_name}: UNKNOWN - {status}")
        
        print("\n📈 RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️  Warnings: {warning_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 All critical tests passed! OpenRouter integration is working!")
        elif failed_tests < total_tests / 2:
            print("\n👍 Most tests passed. OpenRouter integration is mostly working.")
        else:
            print("\n⚠️  Many tests failed. Please check your OpenRouter API key and network connection.")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "warnings": warning_tests,
            "failed": failed_tests,
            "success_rate": success_rate
        }
    
    def save_results(self):
        """Save test results to file"""
        try:
            with open("openrouter_test_results.json", "w") as f:
                json.dump({
                    "timestamp": time.time(),
                    "test_results": self.test_results,
                    "summary": self.print_summary()
                }, f, indent=2, default=str)
            print("\n💾 Test results saved to 'openrouter_test_results.json'")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {str(e)}")

async def main():
    """Main test runner"""
    print("🧪 OpenRouter Learning Path Generator Test Suite")
    print("="*60)
    
    tester = LearningPathTester()
    
    try:
        # Setup
        if not await tester.setup():
            print("❌ Setup failed. Please check your configuration.")
            return
        
        # Run tests
        await tester.test_openrouter_connection()
        await tester.test_query_generation()
        await tester.test_resource_ranking()
        await tester.test_content_summarization()
        await tester.test_model_fallbacks()
        await tester.test_full_learning_path_generation()
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    finally:
        await tester.cleanup()
        tester.print_summary()
        tester.save_results()

if __name__ == "__main__":
    asyncio.run(main()) 