#!/usr/bin/env python3
"""
Test script to find models that actually work with the current HF API in 2025
Based on web search findings about working models and current API structure
"""
import os
import requests
import time
from huggingface_hub import InferenceClient
import json

# Set the token
API_TOKEN = 'your_huggingface_token_here'
os.environ['HUGGINGFACE_API_TOKEN'] = API_TOKEN

def test_model_with_inference_client(model_name, test_input="Hello, how are you?"):
    """Test a model using the new InferenceClient approach"""
    try:
        print(f"Testing {model_name} with InferenceClient...")
        client = InferenceClient(token=API_TOKEN)
        
        # Try text generation
        response = client.text_generation(
            prompt=test_input,
            model=model_name,
            max_new_tokens=50,
            temperature=0.7
        )
        print(f"✅ SUCCESS: {model_name}")
        print(f"Response: {response[:100]}...")
        return True, response
        
    except Exception as e:
        print(f"❌ FAILED: {model_name} - {str(e)}")
        return False, str(e)

def test_model_with_chat_completion(model_name, test_input="Hello, how are you?"):
    """Test a model using chat completion if supported"""
    try:
        print(f"Testing {model_name} with chat completion...")
        client = InferenceClient(token=API_TOKEN)
        
        response = client.chat_completion(
            messages=[{"role": "user", "content": test_input}],
            model=model_name,
            max_tokens=50
        )
        
        print(f"✅ SUCCESS (Chat): {model_name}")
        print(f"Response: {response.choices[0].message.content[:100]}...")
        return True, response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ FAILED (Chat): {model_name} - {str(e)}")
        return False, str(e)

def test_model_with_raw_api(model_name, test_input="Hello, how are you?"):
    """Test with raw API call to see what happens"""
    try:
        print(f"Testing {model_name} with raw API...")
        
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": test_input,
            "parameters": {"max_new_tokens": 50}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS (Raw API): {model_name}")
            print(f"Response: {str(result)[:100]}...")
            return True, result
        else:
            print(f"❌ FAILED (Raw API): {model_name} - Status: {response.status_code}, Response: {response.text}")
            return False, f"Status: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        print(f"❌ FAILED (Raw API): {model_name} - {str(e)}")
        return False, str(e)

def main():
    """Test various models based on 2025 findings"""
    print("🧪 Testing Current Working Models in 2025")
    print("=" * 80)
    
    # Models based on web search findings - mix of different types
    models_to_test = [
        # From LinkedIn article about top 2025 models
        "microsoft/DialoGPT-medium",
        "microsoft/DialoGPT-small", 
        "microsoft/DialoGPT-large",
        
        # Basic text generation models that might still work
        "gpt2",
        "distilgpt2",
        "openai-gpt",
        
        # Small instruction-following models
        "microsoft/CodeGPT-small-py",
        "EleutherAI/gpt-neo-125m",
        "EleutherAI/gpt-neo-1.3B",
        
        # Text classification models (different API)
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "distilbert-base-uncased-finetuned-sst-2-english",
        
        # Feature extraction models
        "sentence-transformers/all-MiniLM-L6-v2",
        
        # Fill mask models
        "bert-base-uncased",
        "distilbert-base-uncased",
        
        # From HF documentation examples
        "facebook/bart-large-cnn",  # summarization
        "deepset/roberta-base-squad2",  # question answering
        
        # Recent smaller models that might work
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "Qwen/Qwen2-0.5B-Instruct",
        
        # Models mentioned as potentially working
        "google/flan-t5-small",
        "google/flan-t5-base",
        "t5-small",
        "t5-base",
    ]
    
    working_models = []
    failed_models = []
    
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing: {model}")
        print(f"{'='*60}")
        
        # Test with different methods
        methods_tried = []
        
        # Method 1: InferenceClient text_generation
        success1, result1 = test_model_with_inference_client(model)
        methods_tried.append(("InferenceClient", success1, result1))
        
        if not success1:
            # Method 2: Chat completion (for instruction models)
            success2, result2 = test_model_with_chat_completion(model)
            methods_tried.append(("ChatCompletion", success2, result2))
            
            if not success2:
                # Method 3: Raw API call
                success3, result3 = test_model_with_raw_api(model)
                methods_tried.append(("RawAPI", success3, result3))
        
        # Check if any method worked
        if any(success for _, success, _ in methods_tried):
            working_models.append((model, methods_tried))
            print(f"🎉 {model} WORKS!")
        else:
            failed_models.append((model, methods_tried))
            print(f"💀 {model} FAILED")
            
        # Small delay to avoid rate limits
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print(f"{'='*80}")
    
    print(f"\n✅ WORKING MODELS ({len(working_models)}):")
    for model, methods in working_models:
        working_methods = [method for method, success, _ in methods if success]
        print(f"  - {model} (via: {', '.join(working_methods)})")
    
    print(f"\n❌ FAILED MODELS ({len(failed_models)}):")
    for model, methods in failed_models:
        print(f"  - {model}")
    
    print(f"\n📊 SUCCESS RATE: {len(working_models)}/{len(models_to_test)} ({len(working_models)/len(models_to_test)*100:.1f}%)")
    
    # Save results
    results = {
        "working_models": working_models,
        "failed_models": failed_models,
        "timestamp": time.time()
    }
    
    with open("model_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to model_test_results.json")

if __name__ == "__main__":
    main() 