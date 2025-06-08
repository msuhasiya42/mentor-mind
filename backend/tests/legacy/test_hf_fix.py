#!/usr/bin/env python3
"""
Test script for Hugging Face API fix using the recommended approach
"""
import os
import asyncio
import requests
from huggingface_hub import InferenceClient

# Set your HF token
os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

def test_with_inference_client():
    """Test using the recommended InferenceClient approach"""
    print("🧪 Testing with InferenceClient (Recommended Approach)")
    print("=" * 60)
    
    try:
        # Correct way to initialize InferenceClient
        client = InferenceClient(token=os.getenv("HUGGINGFACE_API_TOKEN"))
        
        # Test with a working model using the correct method
        response = client.text_generation(
            "Generate 3 search queries for learning Python programming:",
            model="tiiuae/falcon-7b-instruct",
            max_new_tokens=128,
            temperature=0.7
        )
        
        print("✅ SUCCESS with InferenceClient!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ InferenceClient failed: {e}")
        return False

def test_with_requests():
    """Test using direct requests as shown in the instructions"""
    print("\n🧪 Testing with Direct Requests")
    print("=" * 60)
    
    API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": "Generate 3 search queries for learning Python programming:",
        "parameters": {"max_new_tokens": 128, "temperature": 0.7}
    }
    
    try:
        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("✅ SUCCESS with Direct Requests!")
        print(f"Response: {result}")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {resp.text}")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_fallback_models():
    """Test multiple models to find working ones"""
    print("\n🧪 Testing Multiple Models for Best Results")
    print("=" * 60)
    
    models_to_test = [
        "tiiuae/falcon-7b-instruct",
        "microsoft/DialoGPT-medium", 
        "google/flan-t5-base",
        "gpt2"
    ]
    
    headers = {
        "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    working_models = []
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...")
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            payload = {
                "inputs": "Hello, how are you?",
                "parameters": {"max_new_tokens": 50}
            }
            
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=10)
            
            if resp.status_code == 200:
                result = resp.json()
                print(f"✅ {model} - WORKING!")
                working_models.append(model)
            elif resp.status_code == 404:
                print(f"❌ {model} - 404 Not Found")
            else:
                print(f"❌ {model} - Error {resp.status_code}")
                
        except Exception as e:
            print(f"❌ {model} - Exception: {e}")
    
    print(f"\n📊 Working Models: {len(working_models)}")
    for model in working_models:
        print(f"  ✅ {model}")
    
    return working_models

async def test_ai_processor():
    """Test our updated AI processor"""
    print("\n🧪 Testing Updated AI Processor")
    print("=" * 60)
    
    import sys
    from pathlib import Path
    
    # Add backend to path
    backend_dir = Path(__file__).parent / 'backend'
    sys.path.insert(0, str(backend_dir))
    
    try:
        from services.ai_processor import AIProcessor
        
        processor = AIProcessor()
        queries = await processor.generate_search_queries("Python programming")
        
        print(f"✅ AI Processor generated {len(queries)} queries:")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
            
        await processor.close()
        return True
        
    except Exception as e:
        print(f"❌ AI Processor failed: {e}")
        return False

def main():
    print("🔧 HUGGING FACE API FIX VERIFICATION")
    print("=" * 70)
    print("Testing the recommended fixes from the instructions\n")
    
    # Test 1: InferenceClient (recommended)
    client_success = test_with_inference_client()
    
    # Test 2: Direct requests
    requests_success = test_with_requests()
    
    # Test 3: Find working models
    working_models = test_fallback_models()
    
    # Test 4: Our updated AI processor
    processor_success = asyncio.run(test_ai_processor())
    
    print("\n📋 SUMMARY")
    print("=" * 70)
    print(f"InferenceClient: {'✅ PASS' if client_success else '❌ FAIL'}")
    print(f"Direct Requests: {'✅ PASS' if requests_success else '❌ FAIL'}")
    print(f"Working Models: {len(working_models)} found")
    print(f"AI Processor: {'✅ PASS' if processor_success else '❌ FAIL'}")
    
    if client_success or requests_success or working_models:
        print("\n🎉 HuggingFace API is working! The fixes have been applied.")
    else:
        print("\n⚠️  All tests failed. May need to check token or wait for HF service.")

if __name__ == "__main__":
    main() 