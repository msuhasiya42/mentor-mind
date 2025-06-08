#!/usr/bin/env python3
"""
Main test runner for mentor-mind project.
Runs tests from the organized backend/tests structure.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import and run the main test suite
from tests.run_all_tests import TestRunner

def main():
    """Main entry point for running all tests"""
    print("🚀 Mentor Mind - Comprehensive Test Suite")
    print("=" * 60)
    print("📁 Project Structure:")
    print("   📂 backend/tests/openrouter/  - OpenRouter API tests")
    print("   📂 backend/tests/integration/ - Integration tests")
    print("   📂 backend/tests/legacy/      - Legacy HuggingFace tests")
    print("   📂 backend/tests/utils/       - Utility tests")
    print("   📂 backend/tests/results/     - Test result files")
    print("=" * 60)
    
    runner = TestRunner()
    
    # Run main test suite
    success = runner.run_all_tests()
    
    # Show legacy tests info
    runner.run_legacy_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("🚀 Your OpenRouter integration is working perfectly!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 