#!/usr/bin/env python3
"""
Test script using the EXACT syntax from the official 2025 HF Inference Providers documentation
Based on: https://huggingface.co/docs/inference-providers/en/index
"""
import os
import requests
import time
from huggingface_hub import InferenceClient
import json

# Set the token
API_TOKEN = 'your_huggingface_token_here'
os.environ['HF_TOKEN'] = API_TOKEN

def test_with_exact_documentation_syntax():
    """Test using the EXACT syntax from the documentation"""
    print("🧪 Testing with EXACT Documentation Syntax")
    print("=" * 80)
    
    try:
        print("Testing the exact example from the documentation...")
        
        # This is the EXACT example from the documentation
        client = InferenceClient(
            provider="novita",
            api_key=os.environ["HF_TOKEN"],
        )

        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3-0324",
            messages=[
                {
                    "role": "user",
                    "content": "How many 'G's in 'huggingface'?"
                }
            ],
        )

        print("✅ SUCCESS with exact documentation syntax!")
        print(f"Response: {completion.choices[0].message}")
        return True, completion.choices[0].message.content
        
    except Exception as e:
        print(f"❌ FAILED with exact documentation syntax - {str(e)}")
        return False, str(e)

def test_with_curl_equivalent():
    """Test using the cURL equivalent from documentation"""
    print("\n🧪 Testing with cURL equivalent")
    print("=" * 80)
    
    try:
        print("Testing the cURL equivalent from the documentation...")
        
        # This is the cURL equivalent from the documentation
        response = requests.post(
            "https://router.huggingface.co/novita/v3/openai/chat/completions",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": "How many G in huggingface?"
                    }
                ],
                "model": "deepseek/deepseek-v3-0324",
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print("✅ SUCCESS with cURL equivalent!")
            print(f"Response: {message}")
            return True, message
        else:
            print(f"❌ FAILED with cURL equivalent - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False, f"Status: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        print(f"❌ FAILED with cURL equivalent - {str(e)}")
        return False, str(e)

def test_traditional_inference_client():
    """Test with the traditional InferenceClient without provider parameter"""
    print("\n🧪 Testing with Traditional InferenceClient")
    print("=" * 80)
    
    try:
        print("Testing with traditional InferenceClient (no provider parameter)...")
        
        client = InferenceClient(token=API_TOKEN)
        
        # Try text generation with simple models
        response = client.text_generation(
            "Hello, how are you?",
            model="gpt2",
            max_new_tokens=50
        )
        
        print("✅ SUCCESS with traditional InferenceClient!")
        print(f"Response: {response[:100]}...")
        return True, response
        
    except Exception as e:
        print(f"❌ FAILED with traditional InferenceClient - {str(e)}")
        return False, str(e)

def test_auto_provider():
    """Test with provider='auto' as mentioned in documentation"""
    print("\n🧪 Testing with provider='auto'")
    print("=" * 80)
    
    try:
        print("Testing with provider='auto'...")
        
        client = InferenceClient(api_key=API_TOKEN)
        
        # Try with provider="auto" which is mentioned in docs
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ],
            provider="auto"
        )

        print("✅ SUCCESS with provider='auto'!")
        print(f"Response: {completion.choices[0].message.content}")
        return True, completion.choices[0].message.content
        
    except Exception as e:
        print(f"❌ FAILED with provider='auto' - {str(e)}")
        return False, str(e)

def test_simple_models():
    """Test with simple models that might still work"""
    print("\n🧪 Testing Simple Models")
    print("=" * 80)
    
    simple_models = [
        "gpt2",
        "distilgpt2",
        "microsoft/DialoGPT-small",
        "google/flan-t5-small"
    ]
    
    working_models = []
    
    for model in simple_models:
        try:
            print(f"Testing {model}...")
            
            client = InferenceClient(token=API_TOKEN)
            
            response = client.text_generation(
                "Hello",
                model=model,
                max_new_tokens=20
            )
            
            print(f"✅ SUCCESS: {model}")
            print(f"Response: {response[:50]}...")
            working_models.append((model, response))
            
        except Exception as e:
            print(f"❌ FAILED: {model} - {str(e)}")
            
        time.sleep(1)
    
    return working_models

def main():
    """Run all tests"""
    print("🚀 COMPREHENSIVE 2025 HF API TEST")
    print("=" * 80)
    
    results = {
        "exact_documentation_syntax": None,
        "curl_equivalent": None,
        "traditional_inference_client": None,
        "auto_provider": None,
        "working_simple_models": [],
        "timestamp": time.time()
    }
    
    # Test 1: Exact documentation syntax
    success1, result1 = test_with_exact_documentation_syntax()
    results["exact_documentation_syntax"] = {"success": success1, "result": str(result1)[:200]}
    
    # Test 2: cURL equivalent
    success2, result2 = test_with_curl_equivalent()
    results["curl_equivalent"] = {"success": success2, "result": str(result2)[:200]}
    
    # Test 3: Traditional InferenceClient
    success3, result3 = test_traditional_inference_client()
    results["traditional_inference_client"] = {"success": success3, "result": str(result3)[:200]}
    
    # Test 4: Auto provider
    success4, result4 = test_auto_provider()
    results["auto_provider"] = {"success": success4, "result": str(result4)[:200]}
    
    # Test 5: Simple models
    working_models = test_simple_models()
    results["working_simple_models"] = [
        {"model": model, "response_preview": str(response)[:100]}
        for model, response in working_models
    ]
    
    # Summary
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print(f"{'='*80}")
    
    print(f"✅ Exact Documentation Syntax: {'SUCCESS' if success1 else 'FAILED'}")
    print(f"✅ cURL Equivalent: {'SUCCESS' if success2 else 'FAILED'}")
    print(f"✅ Traditional InferenceClient: {'SUCCESS' if success3 else 'FAILED'}")
    print(f"✅ Auto Provider: {'SUCCESS' if success4 else 'FAILED'}")
    print(f"✅ Working Simple Models: {len(working_models)} found")
    
    if working_models:
        print("\n🎉 Working Models Found:")
        for model, response in working_models:
            print(f"  - {model}: {str(response)[:50]}...")
    
    # Save results
    with open("comprehensive_api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to comprehensive_api_test_results.json")
    
    # Provide recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    if any([success1, success2, success3, success4]) or working_models:
        print("✅ Good news! At least one method works.")
        if working_models:
            print(f"✅ You can use these {len(working_models)} working models for your application.")
        if success3:
            print("✅ Traditional InferenceClient works - update your code to use this approach.")
    else:
        print("❌ No methods worked. This might be due to:")
        print("   - API token permissions")
        print("   - Account subscription level")
        print("   - Temporary service issues")
        print("   - Regional restrictions")

if __name__ == "__main__":
    main() 