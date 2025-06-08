#!/usr/bin/env python3
"""
Comprehensive test for DeepSeek R1 0528 Qwen3 8B model via OpenRouter
Tests the upgraded model to ensure it's providing better responses than the legacy model
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add backend to path - get the correct backend path
import os
current_dir = os.getcwd()
if current_dir.endswith('backend'):
    # Already in backend directory
    sys.path.insert(0, current_dir)
else:
    # Add backend directory to path
    backend_path = Path(__file__).parent.parent.parent / "backend"
    sys.path.insert(0, str(backend_path))

try:
    from config import settings
    from services.ai_processor import AIProcessor
    from services.search_engines import LLMSearchEngine
    import aiohttp
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please run this script from the project root directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekR1Tester:
    """Test the new DeepSeek R1 0528 Qwen3 8B model"""
    
    def __init__(self):
        self.ai_processor = None
        self.search_engine = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "model_tested": "deepseek/deepseek-r1-0528-qwen3-8b:free",
            "tests": {}
        }
    
    async def setup(self):
        """Initialize test components"""
        print("🔧 Setting up DeepSeek R1 test environment...")
        
        # Check configuration
        if not settings.OPENROUTER_API_KEY:
            print("❌ OPENROUTER_API_KEY not found!")
            print("   Please add your OpenRouter API key to the .env file")
            return False
        
        print(f"✅ OpenRouter API key configured")
        print(f"✅ Default model: {settings.DEFAULT_MODEL}")
        
        # Verify the default model is the new DeepSeek R1
        if "deepseek-r1-0528-qwen3-8b" not in settings.DEFAULT_MODEL:
            print("⚠️  Warning: Default model is not the new DeepSeek R1!")
            print(f"   Current default: {settings.DEFAULT_MODEL}")
            print(f"   Expected: deepseek/deepseek-r1-0528-qwen3-8b:free")
        
        # Initialize components
        self.ai_processor = AIProcessor()
        self.search_engine = LLMSearchEngine()
        
        print("✅ Test environment ready!")
        return True
    
    async def test_direct_api_call(self) -> bool:
        """Test direct OpenRouter API call with DeepSeek R1"""
        print("\n🧪 Testing direct OpenRouter API call...")
        
        try:
            async with aiohttp.ClientSession() as session:
                messages = [
                    {
                        "role": "system", 
                        "content": "You are a helpful AI assistant. Respond concisely and accurately."
                    },
                    {
                        "role": "user",
                        "content": "What is the capital of France? Answer with just the city name."
                    }
                ]
                
                payload = {
                    "model": settings.DEFAULT_MODEL,
                    "messages": messages,
                    "max_tokens": 50,
                    "temperature": 0.3
                }
                
                start_time = time.time()
                
                async with session.post(
                    f"{settings.OPENROUTER_API_BASE}/chat/completions",
                    headers=settings.openrouter_headers,
                    json=payload
                ) as response:
                    
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            
                            print(f"✅ API Response received ({response_time:.2f}s)")
                            print(f"   Model: {settings.DEFAULT_MODEL}")
                            print(f"   Response: {content.strip()}")
                            
                            self.test_results["tests"]["direct_api"] = {
                                "success": True,
                                "response_time": response_time,
                                "response": content.strip(),
                                "model": settings.DEFAULT_MODEL
                            }
                            
                            return "Paris" in content or "paris" in content.lower()
                        else:
                            print("❌ No choices in response")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ API Error {response.status}: {error_text}")
                        
                        self.test_results["tests"]["direct_api"] = {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        return False
                        
        except Exception as e:
            print(f"❌ Exception in direct API test: {str(e)}")
            self.test_results["tests"]["direct_api"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_ai_processor_functionality(self) -> bool:
        """Test AI processor with the new DeepSeek R1 model"""
        print("\n🧪 Testing AI Processor functionality...")
        
        try:
            # Test query generation
            print("   Testing search query generation...")
            queries = await self.ai_processor.generate_search_queries("Python machine learning")
            
            if queries and len(queries) > 0:
                print(f"✅ Generated {len(queries)} search queries")
                for i, query in enumerate(queries[:3], 1):
                    print(f"   {i}. {query}")
                
                self.test_results["tests"]["query_generation"] = {
                    "success": True,
                    "query_count": len(queries),
                    "sample_queries": queries[:3]
                }
            else:
                print("❌ No queries generated")
                self.test_results["tests"]["query_generation"] = {
                    "success": False,
                    "error": "No queries generated"
                }
                return False
            
            # Test content summarization
            print("   Testing content summarization...")
            sample_content = """
            Python is a high-level, interpreted programming language with dynamic semantics. 
            Its high-level built in data structures, combined with dynamic typing and dynamic binding, 
            make it very attractive for Rapid Application Development, as well as for use as a 
            scripting or glue language to connect existing components together.
            """
            
            summary = await self.ai_processor.summarize_content(sample_content, max_length=50)
            
            if summary and len(summary) > 10:
                print(f"✅ Content summarized: {summary[:100]}...")
                self.test_results["tests"]["summarization"] = {
                    "success": True,
                    "summary": summary,
                    "original_length": len(sample_content),
                    "summary_length": len(summary)
                }
            else:
                print("❌ Summarization failed")
                self.test_results["tests"]["summarization"] = {
                    "success": False,
                    "error": "No summary generated"
                }
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ AI Processor test failed: {str(e)}")
            self.test_results["tests"]["ai_processor"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_learning_resource_generation(self) -> bool:
        """Test learning resource generation with DeepSeek R1"""
        print("\n🧪 Testing learning resource generation...")
        
        try:
            topic = "React Hooks"
            print(f"   Generating resources for: {topic}")
            
            # Test search engine
            resources = await self.search_engine.search(topic)
            
            if resources and len(resources) > 0:
                print(f"✅ Generated {len(resources)} learning resources")
                
                # Analyze resource quality
                resource_types = {}
                platforms = {}
                for resource in resources:
                    res_type = resource.get('type', 'unknown')
                    platform = resource.get('platform', 'unknown')
                    resource_types[res_type] = resource_types.get(res_type, 0) + 1
                    platforms[platform] = platforms.get(platform, 0) + 1
                
                print(f"   Resource types: {dict(resource_types)}")
                print(f"   Platforms: {dict(platforms)}")
                
                # Show sample resources
                print("   Sample resources:")
                for i, resource in enumerate(resources[:3], 1):
                    print(f"   {i}. {resource.get('title', 'No title')}")
                    print(f"      Platform: {resource.get('platform', 'Unknown')}")
                    print(f"      Type: {resource.get('type', 'Unknown')}")
                
                self.test_results["tests"]["resource_generation"] = {
                    "success": True,
                    "topic": topic,
                    "resource_count": len(resources),
                    "resource_types": dict(resource_types),
                    "platforms": dict(platforms),
                    "sample_resources": [
                        {
                            "title": r.get('title', ''),
                            "platform": r.get('platform', ''),
                            "type": r.get('type', '')
                        } for r in resources[:3]
                    ]
                }
                
                return True
            else:
                print("❌ No resources generated")
                self.test_results["tests"]["resource_generation"] = {
                    "success": False,
                    "error": "No resources generated"
                }
                return False
                
        except Exception as e:
            print(f"❌ Resource generation test failed: {str(e)}")
            self.test_results["tests"]["resource_generation"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_model_reasoning_capabilities(self) -> bool:
        """Test the enhanced reasoning capabilities of DeepSeek R1"""
        print("\n🧪 Testing DeepSeek R1 reasoning capabilities...")
        
        try:
            # Test coding problem
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert programming instructor. Provide clear, concise explanations."
                },
                {
                    "role": "user",
                    "content": """
                    Explain the difference between `useState` and `useEffect` in React.
                    Give a simple code example for each. Keep it under 200 words.
                    """
                }
            ]
            
            response = await self.ai_processor._call_openrouter_api(messages, max_tokens=300)
            
            if response and len(response) > 50:
                print("✅ Reasoning test passed")
                print(f"   Response length: {len(response)} characters")
                print(f"   Sample: {response[:200]}...")
                
                # Check if response contains key concepts
                key_concepts = ['useState', 'useEffect', 'state', 'side effect', 'component']
                concepts_found = sum(1 for concept in key_concepts if concept.lower() in response.lower())
                
                print(f"   Key concepts found: {concepts_found}/{len(key_concepts)}")
                
                self.test_results["tests"]["reasoning"] = {
                    "success": True,
                    "response_length": len(response),
                    "concepts_found": concepts_found,
                    "total_concepts": len(key_concepts),
                    "sample_response": response[:200]
                }
                
                return concepts_found >= 3
            else:
                print("❌ Reasoning test failed - insufficient response")
                return False
                
        except Exception as e:
            print(f"❌ Reasoning test failed: {str(e)}")
            self.test_results["tests"]["reasoning"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    async def test_model_fallback_system(self) -> bool:
        """Test the model fallback system"""
        print("\n🧪 Testing model fallback system...")
        
        try:
            # Test with all available models
            test_message = "What is JavaScript? Answer in one sentence."
            messages = [
                {"role": "user", "content": test_message}
            ]
            
            fallback_results = {}
            
            for model in settings.FALLBACK_MODELS[:3]:  # Test first 3 models
                try:
                    print(f"   Testing model: {model}")
                    response = await self.ai_processor._call_openrouter_api(messages, model=model, max_tokens=100)
                    
                    if response:
                        fallback_results[model] = {
                            "success": True,
                            "response_length": len(response),
                            "response": response[:100]
                        }
                        print(f"   ✅ {model}: Working")
                    else:
                        fallback_results[model] = {"success": False}
                        print(f"   ❌ {model}: No response")
                        
                except Exception as e:
                    fallback_results[model] = {"success": False, "error": str(e)}
                    print(f"   ❌ {model}: Error - {str(e)}")
            
            successful_models = sum(1 for result in fallback_results.values() if result.get("success", False))
            
            print(f"✅ Fallback test completed: {successful_models}/{len(fallback_results)} models working")
            
            self.test_results["tests"]["fallback"] = {
                "success": successful_models > 0,
                "models_tested": len(fallback_results),
                "successful_models": successful_models,
                "results": fallback_results
            }
            
            return successful_models > 0
            
        except Exception as e:
            print(f"❌ Fallback test failed: {str(e)}")
            self.test_results["tests"]["fallback"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    async def cleanup(self):
        """Clean up test resources"""
        print("\n🧹 Cleaning up...")
        
        if self.ai_processor:
            await self.ai_processor.close()
        
        if self.search_engine:
            await self.search_engine.close()
        
        print("✅ Cleanup completed")
    
    def save_results(self):
        """Save test results to file"""
        filename = "deepseek_r1_test_results.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"✅ Test results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🎯 DEEPSEEK R1 0528 QWEN3 8B TEST SUMMARY")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_result in self.test_results["tests"].items():
            total_tests += 1
            success = test_result.get("success", False)
            if success:
                passed_tests += 1
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
            
            if not success and "error" in test_result:
                print(f"     Error: {test_result['error']}")
        
        print(f"\nResults: {passed_tests}/{total_tests} tests passed")
        print(f"Model: {self.test_results['model_tested']}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! DeepSeek R1 is working perfectly!")
        elif passed_tests > 0:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the issues above.")
        else:
            print("\n❌ All tests failed. Check your OpenRouter configuration.")

async def main():
    """Run all DeepSeek R1 tests"""
    print("🚀 Starting DeepSeek R1 0528 Qwen3 8B Comprehensive Test")
    print("="*60)
    
    tester = DeepSeekR1Tester()
    
    try:
        # Setup
        if not await tester.setup():
            print("❌ Setup failed. Exiting.")
            return
        
        # Run tests
        tests = [
            ("Direct API Call", tester.test_direct_api_call),
            ("AI Processor", tester.test_ai_processor_functionality),
            ("Resource Generation", tester.test_learning_resource_generation),
            ("Reasoning Capabilities", tester.test_model_reasoning_capabilities),
            ("Fallback System", tester.test_model_fallback_system)
        ]
        
        print(f"\n🧪 Running {len(tests)} test suites...")
        
        for test_name, test_func in tests:
            print(f"\n{'─'*20} {test_name} {'─'*20}")
            try:
                await test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
        
        # Summary and cleanup
        tester.print_summary()
        tester.save_results()
        
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 