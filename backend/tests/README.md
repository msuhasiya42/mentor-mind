# Tests Directory Structure

This directory contains all tests for the mentor-mind backend, organized by category for better maintainability.

## Directory Structure

```
backend/tests/
├── __init__.py                 # Package initialization
├── run_all_tests.py           # Master test runner
├── README.md                  # This file
├── openrouter/                # OpenRouter API tests
│   ├── __init__.py
│   ├── test_openrouter_setup.py         # Basic API setup tests
│   ├── test_api_openrouter.py           # FastAPI integration tests
│   ├── test_learning_path_openrouter.py # Learning path generation tests
│   └── test_deepseek_r1_openrouter.py   # DeepSeek R1 model tests
├── integration/               # Integration tests
│   ├── __init__.py
│   ├── test_ai_detailed.py              # AI processing integration
│   ├── test_app.py                      # Application integration
│   └── test_llm_search.py               # LLM search integration
├── legacy/                    # Legacy HuggingFace tests (archived)
│   ├── __init__.py
│   ├── test_hf_fix.py                   # HuggingFace fix attempts
│   ├── test_new_hf_api.py               # New HF API tests
│   ├── test_2025_inference_providers.py # 2025 inference provider tests
│   ├── test_current_working_models.py   # Working model tests
│   ├── test_correct_2025_api.py         # Correct 2025 API tests
│   ├── test_available_models.py         # Available model tests
│   └── test_working_models.py           # Working model validation
├── utils/                     # Utility and helper tests
│   ├── __init__.py
│   ├── test_direct_api.py               # Direct API testing utilities
│   ├── test_import.py                   # Import testing utilities
│   ├── final_test.py                    # Final validation tests
│   ├── debug_search.py                  # Search debugging utilities
│   └── direct_ai_test.py                # Direct AI testing utilities
└── results/                   # Test result files
    ├── __init__.py
    ├── deepseek_r1_test_results.json
    ├── comprehensive_api_test_results.json
    ├── inference_providers_test_results.json
    └── ai_results.json
```

## Running Tests

### Run All Tests
From the project root:
```bash
python run_tests.py
```

### Run Specific Test Categories

#### OpenRouter Tests
```bash
cd backend/tests/openrouter
python test_openrouter_setup.py          # Basic setup
python test_deepseek_r1_openrouter.py    # DeepSeek R1 model
python test_learning_path_openrouter.py  # Learning path generation
python test_api_openrouter.py            # FastAPI integration
```

#### Integration Tests
```bash
cd backend/tests/integration
python test_ai_detailed.py               # AI processing
python test_app.py                       # Application integration
```

#### Utility Tests
```bash
cd backend/tests/utils
python test_direct_api.py                # Direct API testing
python test_import.py                    # Import validation
```

### Run Legacy Tests (for reference)
```bash
cd backend/tests/legacy
# Note: These may not work due to HuggingFace API changes
python test_hf_fix.py
python test_new_hf_api.py
```

## Test Categories Explained

### 🔌 OpenRouter Tests (`openrouter/`)
Tests specifically for OpenRouter API integration:
- **Basic Setup**: API key validation, connection testing
- **DeepSeek R1**: Advanced model testing with reasoning capabilities
- **Learning Path**: End-to-end learning path generation
- **FastAPI Integration**: Server API endpoint testing

### 🎯 Integration Tests (`integration/`)
Tests for system integration and end-to-end functionality:
- **AI Processing**: AI service integration testing
- **Application**: Full application workflow testing
- **LLM Search**: Search functionality with LLM integration

### 🏛️ Legacy Tests (`legacy/`)
Archived tests from the HuggingFace era (kept for reference):
- Historical test files from the HuggingFace integration
- May not work due to API changes
- Useful for understanding migration path

### 🔧 Utility Tests (`utils/`)
Helper tests and debugging utilities:
- Direct API testing tools
- Import validation
- Debug utilities for development

### 📊 Results (`results/`)
Test result files and reports:
- JSON files with test results
- Performance benchmarks
- Historical test data

## Prerequisites

Before running tests, ensure:

1. **Environment Setup**:
   ```bash
   # Install dependencies
   pip install -r backend/requirements.txt
   
   # Set up environment variables
   cp .env.template .env
   # Edit .env with your OpenRouter API key
   ```

2. **OpenRouter API Key**:
   - Sign up at https://openrouter.ai
   - Get your API key
   - Add to `.env`: `OPENROUTER_API_KEY=your_key_here`

3. **Project Structure**:
   - Ensure you're in the project root when running tests
   - Backend server should be available (for integration tests)

## Test Development Guidelines

### Adding New Tests

1. **Choose the Right Category**:
   - OpenRouter-specific → `openrouter/`
   - Integration/E2E → `integration/`
   - Utilities/Helpers → `utils/`

2. **Follow Naming Convention**:
   - `test_*.py` for test files
   - Descriptive names: `test_feature_functionality.py`

3. **Update Test Runner**:
   - Add new tests to `run_all_tests.py`
   - Categorize appropriately

### Test Structure Template

```python
#!/usr/bin/env python3
"""
Test description
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

def test_feature():
    """Test specific feature"""
    # Test implementation
    pass

def main():
    """Main test runner"""
    print("🧪 Testing [Feature Name]")
    
    try:
        test_feature()
        print("✅ All tests passed!")
        return True
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure you're running from project root
   - Check Python path configuration

2. **API Key Issues**:
   - Verify `.env` file exists and contains valid key
   - Check OpenRouter account status

3. **Network Issues**:
   - Ensure internet connection
   - Check firewall settings

4. **Dependency Issues**:
   - Run `pip install -r backend/requirements.txt`
   - Check Python version compatibility

### Getting Help

- Check individual test file documentation
- Review error messages in test output
- Consult the main project README.md
- Check OpenRouter API documentation 