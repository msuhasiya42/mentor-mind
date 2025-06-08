#!/usr/bin/env python3
"""
Test script to verify that the updated models work with HuggingFace Inference API
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def test_working_models():
    """Test the models that are verified to work with HF Inference API"""
    print("🧪 Testing Updated Working Models")
    print("=" * 60)
    
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not api_token:
        print("❌ No HUGGINGFACE_API_TOKEN found in environment")
        print("Please create a .env file with your token:")
        print("HUGGINGFACE_API_TOKEN=hf_your_token_here")
        return False
    
    # Test the updated models
    models_to_test = [
        "gpt2",  # Default model
        "tiiuae/falcon-7b-instruct",  # Text generation model
        "microsoft/DialoGPT-medium",  # Fallback
        "google/flan-t5-base"  # Another fallback
    ]
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    working_models = []
    failed_models = []
    
    for model in models_to_test:
        try:
            print(f"Testing {model}...")
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            payload = {
                "inputs": "Generate a simple tutorial outline for learning Python:",
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    print(f"✅ {model} - SUCCESS!")
                    print(f"   Generated: {generated_text[:100]}...")
                    working_models.append(model)
                else:
                    print(f"⚠️  {model} - Unexpected response format")
                    failed_models.append(model)
            elif response.status_code == 404:
                print(f"❌ {model} - 404 Not Found (model not hosted)")
                failed_models.append(model)
            elif response.status_code == 503:
                print(f"⏳ {model} - 503 Model Loading (try again later)")
                failed_models.append(model)
            else:
                print(f"❌ {model} - Error {response.status_code}: {response.text}")
                failed_models.append(model)
                
        except requests.exceptions.Timeout:
            print(f"⏳ {model} - Timeout (model may be loading)")
            failed_models.append(model)
        except Exception as e:
            print(f"❌ {model} - Exception: {e}")
            failed_models.append(model)
    
    print(f"\n📊 RESULTS")
    print("=" * 60)
    print(f"✅ Working Models ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model}")
    
    if failed_models:
        print(f"\n❌ Failed Models ({len(failed_models)}):")
        for model in failed_models:
            print(f"   • {model}")
    
    if working_models:
        print(f"\n🎉 SUCCESS! {len(working_models)} models are working with your configuration.")
        print("Your application should now work with the Hugging Face Inference API.")
    else:
        print(f"\n⚠️  No models are working. This could be due to:")
        print("   • Invalid API token")
        print("   • Models currently loading (try again in a few minutes)")
        print("   • Network issues")
    
    return len(working_models) > 0

if __name__ == "__main__":
    print("🔧 TESTING UPDATED MODEL CONFIGURATION")
    print("=" * 70)
    success = test_working_models()
    exit(0 if success else 1) 