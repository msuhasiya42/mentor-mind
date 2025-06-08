#!/usr/bin/env python3
"""
Test the FastAPI server with OpenRouter integration
Tests the main API endpoints to ensure they work correctly with OpenRouter.
"""

import asyncio
import requests
import json
import time
import sys
import subprocess
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds

class APITester:
    def __init__(self):
        self.server_process = None
        self.test_results = {}
    
    def start_server(self):
        """Start the FastAPI server in background"""
        print("🚀 Starting FastAPI server...")
        
        try:
            # Change to backend directory and start server
            backend_path = Path(__file__).parent.parent.parent / "backend"
            
            self.server_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for attempt in range(10):
                try:
                    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    print(f"   Waiting for server... (attempt {attempt + 1}/10)")
                    time.sleep(2)
            
            print("❌ Server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            print("🛑 Stopping FastAPI server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            print("✅ Server stopped")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("\n🏥 Testing health endpoint...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health endpoint working:")
                print(f"   Status: {data.get('status')}")
                print(f"   OpenRouter API: {data.get('openrouter_api')}")
                print(f"   Default Model: {data.get('default_model')}")
                print(f"   Available Models: {data.get('available_free_models')}")
                
                self.test_results["health_endpoint"] = {
                    "status": "success",
                    "response": data
                }
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results["health_endpoint"] = {
                    "status": "failed",
                    "status_code": response.status_code
                }
                return False
                
        except Exception as e:
            print(f"❌ Health endpoint error: {str(e)}")
            self.test_results["health_endpoint"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_learning_path_endpoint(self):
        """Test the learning path generation endpoint"""
        print("\n🎯 Testing learning path generation endpoint...")
        
        test_topics = ["Python", "React basics"]
        
        for topic in test_topics:
            try:
                print(f"   Testing topic: '{topic}'")
                
                payload = {"topic": topic}
                start_time = time.time()
                
                response = requests.post(
                    f"{API_BASE_URL}/generate-learning-path",
                    json=payload,
                    timeout=TIMEOUT
                )
                
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    learning_path = data.get("learning_path", {})
                    
                    # Count resources
                    total_resources = sum([
                        len(learning_path.get("docs", [])),
                        len(learning_path.get("blogs", [])),
                        len(learning_path.get("youtube", [])),
                        len(learning_path.get("free_courses", [])),
                        len(learning_path.get("paid_courses", []))
                    ])
                    
                    print(f"   ✅ Generated learning path in {duration:.2f}s:")
                    print(f"      📖 Docs: {len(learning_path.get('docs', []))}")
                    print(f"      📝 Blogs: {len(learning_path.get('blogs', []))}")
                    print(f"      🎥 YouTube: {len(learning_path.get('youtube', []))}")
                    print(f"      🆓 Free Courses: {len(learning_path.get('free_courses', []))}")
                    print(f"      💰 Paid Courses: {len(learning_path.get('paid_courses', []))}")
                    print(f"      📊 Total Resources: {total_resources}")
                    
                    # Show sample resource
                    if learning_path.get("docs"):
                        sample = learning_path["docs"][0]
                        print(f"      Sample: {sample.get('title', 'No title')}")
                    
                    self.test_results[f"learning_path_{topic.replace(' ', '_')}"] = {
                        "status": "success",
                        "duration": duration,
                        "total_resources": total_resources,
                        "breakdown": {
                            "docs": len(learning_path.get("docs", [])),
                            "blogs": len(learning_path.get("blogs", [])),
                            "youtube": len(learning_path.get("youtube", [])),
                            "free_courses": len(learning_path.get("free_courses", [])),
                            "paid_courses": len(learning_path.get("paid_courses", []))
                        }
                    }
                    
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"      Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        print(f"      Error: {response.text}")
                    
                    self.test_results[f"learning_path_{topic.replace(' ', '_')}"] = {
                        "status": "failed",
                        "status_code": response.status_code,
                        "duration": duration
                    }
                    
            except Exception as e:
                print(f"   ❌ Error testing '{topic}': {str(e)}")
                self.test_results[f"learning_path_{topic.replace(' ', '_')}"] = {
                    "status": "error",
                    "error": str(e)
                }
    
    def test_invalid_requests(self):
        """Test API error handling"""
        print("\n🚫 Testing error handling...")
        
        # Test empty topic
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate-learning-path",
                json={"topic": ""},
                timeout=10
            )
            
            if response.status_code == 400:
                print("✅ Empty topic correctly rejected")
                self.test_results["error_handling_empty"] = {"status": "success"}
            else:
                print(f"⚠️  Empty topic response: {response.status_code}")
                self.test_results["error_handling_empty"] = {"status": "unexpected", "code": response.status_code}
                
        except Exception as e:
            print(f"❌ Error testing empty topic: {str(e)}")
            self.test_results["error_handling_empty"] = {"status": "error", "error": str(e)}
        
        # Test missing topic
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate-learning-path",
                json={},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error
                print("✅ Missing topic correctly rejected")
                self.test_results["error_handling_missing"] = {"status": "success"}
            else:
                print(f"⚠️  Missing topic response: {response.status_code}")
                self.test_results["error_handling_missing"] = {"status": "unexpected", "code": response.status_code}
                
        except Exception as e:
            print(f"❌ Error testing missing topic: {str(e)}")
            self.test_results["error_handling_missing"] = {"status": "error", "error": str(e)}
    
    def test_debug_endpoint(self):
        """Test the debug search endpoint"""
        print("\n🔍 Testing debug search endpoint...")
        
        try:
            payload = {"topic": "Python"}
            
            response = requests.post(
                f"{API_BASE_URL}/debug-search",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Debug endpoint working:")
                
                if "error" in data:
                    print(f"   ⚠️  Debug endpoint returned error: {data['error']}")
                    self.test_results["debug_endpoint"] = {"status": "error", "error": data["error"]}
                else:
                    print(f"   LLM Direct Results: {data.get('llm_direct_count', 0)}")
                    if data.get('aggregator_results'):
                        for category, count in data['aggregator_results'].items():
                            print(f"   {category}: {count}")
                    
                    self.test_results["debug_endpoint"] = {
                        "status": "success",
                        "response": data
                    }
            else:
                print(f"❌ Debug endpoint failed: {response.status_code}")
                self.test_results["debug_endpoint"] = {
                    "status": "failed",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            print(f"❌ Debug endpoint error: {str(e)}")
            self.test_results["debug_endpoint"] = {
                "status": "error",
                "error": str(e)
            }
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 API TEST SUMMARY")
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
                print(f"❌ {test_name}: FAILED")
                failed_tests += 1
            elif status in ["unexpected", "warning"]:
                print(f"⚠️  {test_name}: WARNING")
                warning_tests += 1
        
        print(f"\n📈 RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️  Warnings: {warning_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 All API tests passed! Your application is ready to use!")
        elif failed_tests < total_tests / 2:
            print("\n👍 Most API tests passed. Your application should work well.")
        else:
            print("\n⚠️  Many API tests failed. Please check your configuration.")
    
    def save_results(self):
        """Save test results to file"""
        try:
            with open("api_test_results.json", "w") as f:
                json.dump({
                    "timestamp": time.time(),
                    "test_results": self.test_results
                }, f, indent=2, default=str)
            print("\n💾 API test results saved to 'api_test_results.json'")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {str(e)}")

def main():
    """Main test runner"""
    print("🌐 FastAPI + OpenRouter Integration Test")
    print("="*50)
    
    tester = APITester()
    
    try:
        # Start server
        if not tester.start_server():
            print("❌ Could not start server. Please check your configuration.")
            return
        
        # Run tests
        tester.test_health_endpoint()
        tester.test_learning_path_endpoint()
        tester.test_invalid_requests()
        tester.test_debug_endpoint()
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    finally:
        tester.stop_server()
        tester.print_summary()
        tester.save_results()

if __name__ == "__main__":
    main() 