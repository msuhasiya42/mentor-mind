# 🚀 OpenRouter Integration Setup Instructions

## Step 1: Add Your OpenRouter API Key

1. **Get your API key**:
   - Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
   - Sign up for a free account if you haven't already
   - Copy your API key

2. **Update the .env file**:
   ```bash
   # Edit the .env file (it already exists)
   nano .env
   # Or use any text editor you prefer
   ```

3. **Replace the placeholder**:
   ```bash
   # Change this line:
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # To your actual key:
   OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
   ```

## Step 2: Run Tests to Verify Integration

### Option A: Run All Tests (Recommended)
```bash
python run_all_tests.py
```
This will run a comprehensive test suite and provide a detailed report.

### Option B: Run Individual Tests
```bash
# Basic OpenRouter API verification
python test_openrouter_setup.py

# Complete learning path generator test  
python test_learning_path_openrouter.py

# FastAPI integration test
python test_api_openrouter.py
```

## Step 3: Start Your Application

Once tests pass:

```bash
# 1. Start the backend server
cd backend
python main.py

# 2. In a new terminal, start the frontend
cd frontend  
npm run dev

# 3. Visit your application
open http://localhost:5173
```

## 🎯 What Each Test Does

- **test_openrouter_setup.py**: Verifies basic OpenRouter API connection and model availability
- **test_learning_path_openrouter.py**: Tests the complete learning path generation with AI features
- **test_api_openrouter.py**: Tests the FastAPI server endpoints and integration
- **run_all_tests.py**: Runs all tests and provides comprehensive reporting

## 💡 Tips

- **Free Tier**: You get 50 requests per day for free
- **Higher Limits**: Add $10 credit for 1,000 requests per day
- **Best Model**: DeepSeek is excellent for coding-related topics
- **Fallbacks**: The system automatically tries multiple models if one fails

## 🔧 Troubleshooting

If tests fail:
1. Verify your API key is correct
2. Check your internet connection
3. Ensure all dependencies are installed: `pip install -r backend/requirements.txt`
4. Check the OpenRouter dashboard for any account issues

## 📊 Test Results

Test results are saved to:
- `openrouter_test_results.json` - Basic setup test results
- `api_test_results.json` - API integration test results  
- `comprehensive_test_report.json` - Complete test suite results

Your OpenRouter integration is ready! 🎉 