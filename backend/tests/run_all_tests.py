#!/usr/bin/env python3
"""
Master test runner for OpenRouter integration
Runs all tests in sequence and provides a comprehensive report.
Updated to work with organized test directory structure.
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import os

class TestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.base_dir = Path(__file__).parent  # backend/tests
        self.project_root = self.base_dir.parent.parent  # project root
    
    def run_test_script(self, script_path, description):
        """Run a test script and capture results"""
        print(f"\n{'='*60}")
        print(f"🧪 Running: {description}")
        print(f"📄 Script: {script_path}")
        print('='*60)
        
        try:
            start_time = time.time()
            
            # Change to project root directory to run tests
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Change back to original directory
            os.chdir(original_cwd)
            
            duration = time.time() - start_time
            
            print(result.stdout)
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            
            success = result.returncode == 0
            
            self.test_results[str(script_path)] = {
                "description": description,
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                print(f"✅ {description} completed successfully in {duration:.2f}s")
            else:
                print(f"❌ {description} failed with return code {result.returncode}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after 5 minutes")
            self.test_results[str(script_path)] = {
                "description": description,
                "success": False,
                "duration": 300,
                "error": "timeout"
            }
            return False
            
        except Exception as e:
            print(f"💥 Error running {description}: {str(e)}")
            self.test_results[str(script_path)] = {
                "description": description,
                "success": False,
                "error": str(e)
            }
            return False
    
    def check_prerequisites(self):
        """Check if prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if .env file exists in project root
        env_file = self.project_root / ".env"
        if not env_file.exists():
            print("❌ .env file not found in project root!")
            print("   Please create .env file with your OpenRouter API key")
            return False
        
        # Check if API key is set (not the placeholder)
        try:
            with open(env_file, "r") as f:
                content = f.read()
                if "your_openrouter_api_key_here" in content:
                    print("❌ Please replace 'your_openrouter_api_key_here' with your actual OpenRouter API key in .env")
                    return False
                if "OPENROUTER_API_KEY=" not in content:
                    print("❌ OPENROUTER_API_KEY not found in .env file")
                    return False
        except Exception as e:
            print(f"❌ Could not read .env file: {str(e)}")
            return False
        
        # Check if required modules are available
        try:
            import aiohttp
            import requests
            print("✅ Required modules available")
        except ImportError as e:
            print(f"❌ Missing required module: {str(e)}")
            print("   Please run: pip install -r backend/requirements.txt")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def run_all_tests(self):
        """Run all OpenRouter integration tests in organized structure"""
        
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix the issues above.")
            return False
        
        print("\n🚀 Starting comprehensive OpenRouter integration test suite...")
        print(f"⏰ Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Test directory structure:")
        print(f"   📂 OpenRouter tests: {self.base_dir / 'openrouter'}")
        print(f"   📂 Integration tests: {self.base_dir / 'integration'}")
        print(f"   📂 Legacy tests: {self.base_dir / 'legacy'}")
        print(f"   📂 Utility tests: {self.base_dir / 'utils'}")
        
        # Test sequence organized by category
        test_categories = [
            {
                "name": "🔌 OpenRouter Core Tests",
                "tests": [
                    (self.base_dir / "openrouter" / "test_openrouter_setup.py", "Basic OpenRouter API Setup"),
                    (self.base_dir / "openrouter" / "test_deepseek_r1_openrouter.py", "DeepSeek R1 Model Testing"),
                ]
            },
            {
                "name": "🎯 Integration Tests", 
                "tests": [
                    (self.base_dir / "openrouter" / "test_learning_path_openrouter.py", "Learning Path Generator"),
                    (self.base_dir / "openrouter" / "test_api_openrouter.py", "FastAPI Server Integration"),
                    (self.base_dir / "integration" / "test_ai_detailed.py", "AI Processing Integration"),
                ]
            },
            {
                "name": "🔧 Utility Tests",
                "tests": [
                    (self.base_dir / "utils" / "test_direct_api.py", "Direct API Testing"),
                    (self.base_dir / "utils" / "test_import.py", "Import Testing"),
                ]
            }
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for category in test_categories:
            print(f"\n{category['name']}")
            print("─" * 50)
            
            for script_path, description in category["tests"]:
                if script_path.exists():
                    total_tests += 1
                    if self.run_test_script(script_path, description):
                        passed_tests += 1
                else:
                    print(f"⚠️  Skipping {description} - file not found: {script_path}")
                
                # Small delay between tests
                time.sleep(1)
        
        # Generate final report
        self.generate_final_report(total_tests, passed_tests)
        
        return passed_tests == total_tests
    
    def run_legacy_tests(self):
        """Run legacy HuggingFace tests (for comparison)"""
        print("\n🏛️  Running Legacy Tests (for reference)")
        print("─" * 50)
        
        legacy_tests = [
            (self.base_dir / "legacy" / "test_hf_fix.py", "HuggingFace Fix Test"),
            (self.base_dir / "legacy" / "test_new_hf_api.py", "New HF API Test"),
        ]
        
        for script_path, description in legacy_tests:
            if script_path.exists():
                print(f"📄 Found legacy test: {description}")
                # Note: We don't run these as they may fail due to API changes
            else:
                print(f"📄 Legacy test not found: {script_path}")
    
    def generate_final_report(self, total_tests, passed_tests):
        """Generate comprehensive final report"""
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        print(f"⏰ Total Duration: {total_duration:.2f} seconds")
        print(f"📋 Total Test Suites: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📝 Detailed Results:")
        for script_path, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result.get("duration", 0)
            print(f"   {status} {result['description']} ({duration:.2f}s)")
            
            if not result["success"] and "error" in result:
                print(f"      Error: {result['error']}")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if passed_tests == total_tests:
            print("🎉 EXCELLENT! All tests passed. Your OpenRouter integration is working perfectly!")
            print("   ✅ OpenRouter API connection is working")
            print("   ✅ AI-powered query generation is working")
            print("   ✅ Learning path generation is working") 
            print("   ✅ FastAPI server integration is working")
            print("\n🚀 Your application is ready for production use!")
            
        elif passed_tests >= total_tests * 0.75:
            print("👍 GOOD! Most tests passed. Your integration is mostly working.")
            print("   🔧 Some minor issues may need attention.")
            
        elif passed_tests >= total_tests * 0.5:
            print("⚠️  PARTIAL! Some tests passed but there are significant issues.")
            print("   🔧 Please review the failed tests and fix the issues.")
            
        else:
            print("❌ POOR! Most tests failed. There are major issues with the integration.")
            print("   🔧 Please check:")
            print("      - Your OpenRouter API key is correct")
            print("      - You have internet connection")
            print("      - All dependencies are installed")
        
        # Save comprehensive report
        self.save_comprehensive_report(total_tests, passed_tests, success_rate)
        
        # Provide next steps
        print("\n📋 NEXT STEPS:")
        if passed_tests == total_tests:
            print("   1. Your application is ready to use!")
            print("   2. Start the server: cd backend && python main.py")
            print("   3. Start the frontend: cd frontend && npm run dev")
            print("   4. Visit http://localhost:5173 to use your application")
        else:
            print("   1. Review the failed tests above")
            print("   2. Check your .env file has the correct OpenRouter API key")
            print("   3. Ensure all dependencies are installed: pip install -r backend/requirements.txt")
            print("   4. Re-run this test suite: python run_all_tests.py")
        
        print(f"\n📄 Detailed logs saved to 'comprehensive_test_report.json'")
    
    def save_comprehensive_report(self, total_tests, passed_tests, success_rate):
        """Save comprehensive test report to file"""
        try:
            report = {
                "timestamp": time.time(),
                "start_time": self.start_time,
                "total_duration": time.time() - self.start_time,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate": success_rate
                },
                "test_results": self.test_results,
                "assessment": self.get_assessment(success_rate),
                "recommendations": self.get_recommendations(passed_tests, total_tests)
            }
            
            with open("comprehensive_test_report.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
                
        except Exception as e:
            print(f"⚠️  Could not save comprehensive report: {str(e)}")
    
    def get_assessment(self, success_rate):
        """Get assessment based on success rate"""
        if success_rate == 100:
            return "excellent"
        elif success_rate >= 75:
            return "good"
        elif success_rate >= 50:
            return "partial"
        else:
            return "poor"
    
    def get_recommendations(self, passed_tests, total_tests):
        """Get recommendations based on test results"""
        if passed_tests == total_tests:
            return [
                "Application is ready for use",
                "Consider adding $10 credit to OpenRouter for higher rate limits",
                "Monitor usage in OpenRouter dashboard"
            ]
        else:
            return [
                "Review failed tests",
                "Verify OpenRouter API key",
                "Check internet connection",
                "Ensure all dependencies are installed",
                "Re-run tests after fixes"
            ]

def main():
    """Main test runner"""
    print("🧪 OpenRouter Integration - Comprehensive Test Suite")
    print("="*60)
    print("This will run all tests to verify your OpenRouter integration.")
    print("Estimated time: 3-5 minutes")
    print()
    
    runner = TestRunner()
    
    try:
        success = runner.run_all_tests()
        
        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Please review the report above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 