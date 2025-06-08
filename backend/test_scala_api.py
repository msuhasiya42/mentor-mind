#!/usr/bin/env python3
"""
Test script to test the Scala learning path generation API via HTTP request
"""
import requests
import json
import sys
from pathlib import Path

def test_scala_learning_path_api():
    """Test Scala learning path generation via API call"""
    print("🚀 Testing Scala Learning Path API")
    print("=" * 50)
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/generate-learning-path"
    
    # Request payload
    payload = {
        "topic": "Scala programming"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Making API call for Scala learning path...")
        print(f"URL: {endpoint}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Make the API call
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Generated learning path for: {data['topic']}")
            
            learning_path = data['learning_path']
            
            print(f"\n📚 Results Summary:")
            print(f"   📖 Docs: {len(learning_path.get('docs', []))} resources")
            print(f"   📝 Blogs: {len(learning_path.get('blogs', []))} resources")
            print(f"   🎥 YouTube: {len(learning_path.get('youtube', []))} resources")
            print(f"   🆓 Free Courses: {len(learning_path.get('free_courses', []))} resources")
            print(f"   💰 Paid Courses: {len(learning_path.get('paid_courses', []))} resources")
            
            # Show sample resources
            if learning_path.get('docs'):
                print(f"\n📖 Sample Documentation:")
                for i, doc in enumerate(learning_path['docs'][:3], 1):
                    print(f"   {i}. {doc['title']}")
                    if doc.get('url'):
                        print(f"      URL: {doc['url']}")
                    if doc.get('description'):
                        print(f"      Description: {doc['description'][:100]}...")
            
            if learning_path.get('blogs'):
                print(f"\n📝 Sample Blogs:")
                for i, blog in enumerate(learning_path['blogs'][:3], 1):
                    print(f"   {i}. {blog['title']}")
                    if blog.get('url'):
                        print(f"      URL: {blog['url']}")
                    if blog.get('description'):
                        print(f"      Description: {blog['description'][:100]}...")
            
            if learning_path.get('youtube'):
                print(f"\n🎥 Sample YouTube Videos:")
                for i, video in enumerate(learning_path['youtube'][:3], 1):
                    print(f"   {i}. {video['title']}")
                    if video.get('url'):
                        print(f"      URL: {video['url']}")
            
            if learning_path.get('free_courses'):
                print(f"\n🆓 Sample Free Courses:")
                for i, course in enumerate(learning_path['free_courses'][:3], 1):
                    print(f"   {i}. {course['title']}")
                    if course.get('platform'):
                        print(f"      Platform: {course['platform']}")
                    if course.get('url'):
                        print(f"      URL: {course['url']}")
            
            print(f"\n📄 Full Response (JSON):")
            print(json.dumps(data, indent=2))
            
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the API server running?")
        print("💡 Try running: python start_server.py")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: API call took too long")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health Check Endpoint")
    print("=" * 30)
    
    try:
        health_url = "http://localhost:8000/health"
        response = requests.get(health_url, timeout=10)
        
        print(f"Health Check Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is healthy")
            print(f"Status: {health_data.get('status')}")
            print(f"HuggingFace API: {health_data.get('huggingface_api')}")
            print(f"Version: {health_data.get('version')}")
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

if __name__ == "__main__":
    # First test health endpoint
    test_health_endpoint()
    
    # Then test Scala learning path
    test_scala_learning_path_api() 