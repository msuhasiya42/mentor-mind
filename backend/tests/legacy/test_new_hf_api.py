#!/usr/bin/env python3
"""
Test script for the new HuggingFace Inference Providers API
"""
import os
import requests
from huggingface_hub import InferenceClient

# Set the token
os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

def test_inference_client():
    """Test using the new InferenceClient with chat completions"""
    print("🧪 Testing New InferenceClient with Chat Completions")
    print("=" * 60)
    
    try:
        client = InferenceClient(token=os.environ["HUGGINGFACE_API_TOKEN"])
        
        # Try chat completion with a simple model
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            model="microsoft/DialoGPT-medium",
            max_tokens=50
        )
        
        print("✅ SUCCESS with InferenceClient!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ InferenceClient failed: {e}")
        return False

def test_text_generation():
    """Test text generation with InferenceClient"""
    print("\n🧪 Testing Text Generation")
    print("=" * 60)
    
    try:
        client = InferenceClient(token=os.environ["HUGGINGFACE_API_TOKEN"])
        
        response = client.text_generation(
            "Generate a learning plan for Python:",
            model="gpt2",
            max_new_tokens=100
        )
        
        print("✅ SUCCESS with text generation!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        return False

def test_serverless_inference():
    """Test the serverless inference endpoint"""
    print("\n🧪 Testing Serverless Inference")
    print("=" * 60)
    
    try:
        client = InferenceClient(token=os.environ["HUGGINGFACE_API_TOKEN"])
        
        # Try a simple task without specifying model
        response = client.text_generation(
            "Hello world",
            max_new_tokens=20
        )
        
        print("✅ SUCCESS with serverless inference!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Serverless inference failed: {e}")
        return False

def test_feature_extraction():
    """Test feature extraction"""
    print("\n🧪 Testing Feature Extraction")
    print("=" * 60)
    
    try:
        client = InferenceClient(token=os.environ["HUGGINGFACE_API_TOKEN"])
        
        # Try feature extraction
        response = client.feature_extraction("Hello world")
        
        print("✅ SUCCESS with feature extraction!")
        print(f"Response type: {type(response)}")
        return True
        
    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        return False

def test_simple_generation():
    """Test simple text generation without model specification"""
    print("\n🧪 Testing Simple Generation (Auto Model Selection)")
    print("=" * 60)
    
    try:
        client = InferenceClient(token=os.environ["HUGGINGFACE_API_TOKEN"])
        
        # Try without specifying a model
        response = client.text_generation("Hello, I am")
        
        print("✅ SUCCESS with simple generation!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Simple generation failed: {e}")
        return False

def main():
    print("🔧 Testing New HuggingFace Inference Providers API")
    print("=" * 70)
    
    # Test different approaches
    results = {}
    
    results['inference_client'] = test_inference_client()
    results['text_generation'] = test_text_generation()  
    results['serverless'] = test_serverless_inference()
    results['feature_extraction'] = test_feature_extraction()
    results['simple_generation'] = test_simple_generation()
    
    print("\n📋 SUMMARY")
    print("=" * 70)
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    if any(results.values()):
        print("\n🎉 Some API endpoints are working!")
        print("We can update the application to use the working endpoints.")
    else:
        print("\n⚠️  All tests failed.")
        print("This might indicate:")
        print("   • Need to upgrade huggingface_hub library")
        print("   • API token permission issues")
        print("   • Complete migration to paid services")

if __name__ == "__main__":
    main() 