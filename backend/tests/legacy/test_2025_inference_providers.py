#!/usr/bin/env python3
"""
Test script for the NEW 2025 Hugging Face Inference Providers API
Based on the official documentation: https://huggingface.co/docs/inference-providers/en/index
"""
import os
import requests
import time
from huggingface_hub import InferenceClient
import json

# Set the token
API_TOKEN = 'your_huggingface_token_here'
os.environ['HF_TOKEN'] = API_TOKEN

def test_with_new_inference_client(provider, model, test_message="Hello, how are you?"):
    """Test using the new 2025 InferenceClient with chat completions"""
    try:
        print(f"Testing {model} via {provider} with new InferenceClient...")
        
        client = InferenceClient(
            provider=provider,
            api_key=API_TOKEN,
        )
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": test_message
                }
            ],
            max_tokens=100
        )
        
        response_text = completion.choices[0].message.content
        print(f"✅ SUCCESS: {model} via {provider}")
        print(f"Response: {response_text[:100]}...")
        return True, response_text
        
    except Exception as e:
        print(f"❌ FAILED: {model} via {provider} - {str(e)}")
        return False, str(e)

def test_with_raw_new_api(provider, model, test_message="Hello, how are you?"):
    """Test using raw HTTP requests to the new router API"""
    try:
        print(f"Testing {model} via {provider} with raw API...")
        
        # New 2025 API endpoint structure
        url = f"https://router.huggingface.co/{provider}/v3/openai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": test_message
                }
            ],
            "model": model,
            "max_tokens": 100
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            print(f"✅ SUCCESS (Raw): {model} via {provider}")
            print(f"Response: {response_text[:100]}...")
            return True, response_text
        else:
            print(f"❌ FAILED (Raw): {model} via {provider} - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False, f"Status: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        print(f"❌ FAILED (Raw): {model} via {provider} - {str(e)}")
        return False, str(e)

def test_model_combinations():
    """Test various provider + model combinations based on 2025 documentation"""
    print("🧪 Testing 2025 Hugging Face Inference Providers")
    print("=" * 80)
    
    # Based on the documentation, these providers support chat completion
    # Let's test with models that are likely to work
    test_combinations = [
        # Provider, Model
        ("cerebras", "meta-llama/Llama-3.1-8B-Instruct"),
        ("cerebras", "meta-llama/Llama-3.1-70B-Instruct"),
        
        ("cohere", "cohere/command-r-plus-08-2024"),
        ("cohere", "cohere/command-r7b-12-2024"),
        
        ("fireworks-ai", "meta-llama/Llama-3.1-8B-Instruct"),
        ("fireworks-ai", "meta-llama/Llama-3.1-70B-Instruct"),
        
        ("hf-inference", "meta-llama/Llama-3.1-8B-Instruct"),
        ("hf-inference", "microsoft/DialoGPT-medium"),
        ("hf-inference", "gpt2"),
        
        ("hyperbolic", "meta-llama/Llama-3.1-8B-Instruct"),
        ("hyperbolic", "meta-llama/Llama-3.1-70B-Instruct"),
        
        ("novita", "deepseek-ai/DeepSeek-V3-0324"),
        ("novita", "meta-llama/Llama-3.1-8B-Instruct"),
        
        ("replicate", "meta/meta-llama-3-8b-instruct"),
        ("replicate", "meta/meta-llama-3-70b-instruct"),
        
        ("sambanova", "meta-llama/Llama-3.1-8B-Instruct"),
        ("sambanova", "meta-llama/Llama-3.1-405B-Instruct"),
        
        ("together", "meta-llama/Llama-3.1-8B-Instruct"),
        ("together", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
        ("together", "Qwen/Qwen2.5-7B-Instruct"),
    ]
    
    working_combinations = []
    failed_combinations = []
    
    for provider, model in test_combinations:
        print(f"\n{'='*60}")
        print(f"Testing: {model} via {provider}")
        print(f"{'='*60}")
        
        # Test with the new InferenceClient first
        success1, result1 = test_with_new_inference_client(provider, model)
        
        if success1:
            working_combinations.append((provider, model, "InferenceClient", result1))
        else:
            # Try with raw API if InferenceClient fails
            success2, result2 = test_with_raw_new_api(provider, model)
            
            if success2:
                working_combinations.append((provider, model, "RawAPI", result2))
            else:
                failed_combinations.append((provider, model, result1, result2))
        
        # Small delay to avoid rate limits
        time.sleep(3)
    
    # Summary
    print(f"\n{'='*80}")
    print("FINAL RESULTS - 2025 Inference Providers")
    print(f"{'='*80}")
    
    print(f"\n✅ WORKING COMBINATIONS ({len(working_combinations)}):")
    for provider, model, method, response in working_combinations:
        print(f"  - {model} via {provider} (method: {method})")
        print(f"    Response preview: {str(response)[:80]}...")
    
    print(f"\n❌ FAILED COMBINATIONS ({len(failed_combinations)}):")
    for provider, model, error1, error2 in failed_combinations:
        print(f"  - {model} via {provider}")
        print(f"    Errors: InferenceClient={error1[:50]}..., RawAPI={error2[:50]}...")
    
    print(f"\n📊 SUCCESS RATE: {len(working_combinations)}/{len(test_combinations)} ({len(working_combinations)/len(test_combinations)*100:.1f}%)")
    
    # Save results
    results = {
        "working_combinations": [
            {
                "provider": provider,
                "model": model, 
                "method": method,
                "response_preview": str(response)[:200]
            }
            for provider, model, method, response in working_combinations
        ],
        "failed_combinations": [
            {
                "provider": provider,
                "model": model,
                "inference_client_error": error1,
                "raw_api_error": error2
            }
            for provider, model, error1, error2 in failed_combinations
        ],
        "timestamp": time.time(),
        "api_version": "2025_inference_providers"
    }
    
    with open("inference_providers_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to inference_providers_test_results.json")
    
    if working_combinations:
        print(f"\n🎉 SUCCESS! Found {len(working_combinations)} working combinations!")
        print("You can now update your application to use these working provider/model combinations.")
    else:
        print(f"\n😞 No working combinations found. Check your API token and try again.")

if __name__ == "__main__":
    test_model_combinations() 