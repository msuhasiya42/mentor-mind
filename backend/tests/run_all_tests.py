#!/usr/bin/env python3
"""
Test runner for all ContentAggregator tests
"""
import sys
import os
import asyncio
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_file(test_file):
    """Run a specific test file and return the result"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), test_file)
        ], capture_output=False, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"✅ {test_file} passed")
            return True
        else:
            print(f"❌ {test_file} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting ContentAggregator Test Suite")
    print("="*60)
    
    # List of test files to run
    test_files = [
        'test_refactored_content_aggregator.py',
        'test_scala_search.py'
    ]
    
    # Check which test files exist
    existing_tests = []
    tests_dir = os.path.dirname(__file__)
    
    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        if os.path.exists(test_path):
            existing_tests.append(test_file)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    if not existing_tests:
        print("❌ No test files found!")
        return False
    
    print(f"📋 Found {len(existing_tests)} test files to run:")
    for test in existing_tests:
        print(f"  • {test}")
    
    # Run each test
    results = []
    for test_file in existing_tests:
        success = run_test_file(test_file)
        results.append((test_file, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_file, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_file:<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 