#!/usr/bin/env python3
"""
Test script to find models that actually work with the current HF Inference API
"""
import os
import requests

# Set the token directly for testing
os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

def test_model(model_name):
    """Test a specific model with the HF Inference API"""
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {
        "Authorization": f"Bearer {os.environ['HUGGINGFACE_API_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "Hello, how are you?",
        "parameters": {"max_new_tokens": 50}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        print(f"Testing {model_name}...")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {model_name} works!")
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                print(f"Generated: {generated_text[:100]}...")
            return True
        elif response.status_code == 503:
            print(f"⏳ Model loading: {model_name}")
            return False
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False
    finally:
        print("-" * 60)

def main():
    print("🔍 Testing Available Models on HF Inference API")
    print("=" * 60)
    
    # Test various model categories
    models_to_test = [
        # Small instruction models
        "HuggingFaceTB/SmolLM-135M-Instruct",
        "microsoft/DialoGPT-small",
        "microsoft/DialoGPT-medium",
        
        # Base models
        "gpt2",
        "distilgpt2",
        
        # T5 models
        "google/flan-t5-small",
        "google/flan-t5-base",
        
        # Other small models
        "facebook/blenderbot_small-90M",
        "EleutherAI/gpt-neo-125M",
        
        # Test the ones we tried before
        "tiiuae/falcon-7b-instruct"
    ]
    
    working_models = []
    loading_models = []
    failed_models = []
    
    for model in models_to_test:
        if test_model(model):
            working_models.append(model)
        else:
            failed_models.append(model)
    
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    if working_models:
        print(f"✅ Working Models ({len(working_models)}):")
        for model in working_models:
            print(f"   • {model}")
    
    if failed_models:
        print(f"\n❌ Failed Models ({len(failed_models)}):")
        for model in failed_models:
            print(f"   • {model}")
    
    if working_models:
        print(f"\n🎉 Found {len(working_models)} working models!")
        print("We can update the configuration to use these models.")
    else:
        print("\n⚠️  No models are working with the current API.")
        print("This might be due to:")
        print("   • Changes in HF Inference API availability")
        print("   • Need to use the new Inference Providers system")
        print("   • API token issues")

if __name__ == "__main__":
    main() 