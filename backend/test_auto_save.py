#!/usr/bin/env python3
"""
Test script for auto-save functionality
"""
import requests
import json
import time
import os
from datetime import datetime

def test_auto_save():
    """Test the auto-save functionality"""
    base_url = "http://localhost:8000"
    results_dir = "results"
    
    print("🧪 TESTING AUTO-SAVE FUNCTIONALITY")
    print("=" * 50)
    
    # Test 1: Check health
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   OpenRouter API: {data.get('openrouter_api', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
        return
    
    # Test 2: Check initial file count
    print("\n2️⃣ Checking initial saved files...")
    try:
        if os.path.exists(results_dir):
            initial_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
            initial_count = len(initial_files)
            print(f"   ✅ Initial saved files: {initial_count}")
            print(f"   Existing files: {initial_files[:3]}{'...' if len(initial_files) > 3 else ''}")
        else:
            initial_count = 0
            print(f"   ⚠️ Results directory doesn't exist yet")
    except Exception as e:
        print(f"   ❌ Error checking initial files: {str(e)}")
        initial_count = 0
    
    # Test 3: Generate learning path (should trigger auto-save if AI)
    print("\n3️⃣ Generating learning path for 'React'...")
    test_topic = "React"
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/generate-learning-path",
            json={"topic": test_topic},
            headers={"Content-Type": "application/json"}
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            processing_time = end_time - start_time
            
            print(f"   ✅ Learning path generated successfully")
            print(f"   Processing time: {processing_time:.2f}s")
            print(f"   Topic: {data.get('topic', 'unknown')}")
            
            # Count resources
            learning_path = data.get('learning_path', {})
            total_resources = sum(len(learning_path.get(category, [])) for category in 
                                ['docs', 'blogs', 'youtube', 'free_courses', 'paid_courses'])
            print(f"   Total resources: {total_resources}")
            
        else:
            print(f"   ❌ Learning path generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Learning path generation error: {str(e)}")
        return
    
    # Test 4: Check if file was saved
    print("\n4️⃣ Checking if file was auto-saved...")
    time.sleep(1)  # Give a moment for file operations
    
    try:
        if os.path.exists(results_dir):
            final_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
            final_count = len(final_files)
            
            print(f"   ✅ Final saved files: {final_count}")
            print(f"   Files added: {final_count - initial_count}")
            
            # Check for today's React file
            today_date = datetime.now().strftime("%d_%B").lower()
            expected_filename = f"react_res_{today_date}.json"
            
            if expected_filename in final_files:
                print(f"   🎉 AUTO-SAVE WORKED! Found: {expected_filename}")
                
                # Show file details
                filepath = os.path.join(results_dir, expected_filename)
                file_size = os.path.getsize(filepath)
                print(f"   📁 File size: {file_size} bytes")
                
                # Check file content structure
                try:
                    with open(filepath, 'r') as f:
                        saved_data = json.load(f)
                    
                    if 'topic' in saved_data and 'learning_path' in saved_data:
                        print(f"   ✅ File structure is correct")
                        saved_topic = saved_data.get('topic', '')
                        saved_resources = sum(len(saved_data['learning_path'].get(cat, [])) 
                                            for cat in ['docs', 'blogs', 'youtube', 'free_courses', 'paid_courses'])
                        print(f"   📊 Saved topic: '{saved_topic}'")
                        print(f"   📊 Saved resources: {saved_resources}")
                    else:
                        print(f"   ❌ File structure is incorrect")
                        
                except Exception as e:
                    print(f"   ❌ Error reading saved file: {str(e)}")
                    
            elif final_count > initial_count:
                new_files = [f for f in final_files if f not in initial_files]
                print(f"   ✅ New file(s) saved: {new_files}")
                print(f"   ℹ️ Expected: {expected_filename}")
            else:
                print("   ⚠️ No new files saved")
                print("   💡 This might indicate the response was from fallback/manual curation")
                print("   💡 Check logs for source determination")
            
            # Show most recent files
            if final_files:
                final_files.sort(reverse=True)
                print(f"   📁 Most recent files:")
                for i, filename in enumerate(final_files[:3]):
                    print(f"      {i+1}. {filename}")
                    
        else:
            print(f"   ❌ Results directory still doesn't exist")
            
    except Exception as e:
        print(f"   ❌ Error checking saved files: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 AUTO-SAVE TEST COMPLETED")
    print("\nTo check manually:")
    print("   📁 Look in backend/results/ for new JSON files")
    print("   📋 Check backend/logs/ for detailed logs")
    print("   🔍 Search logs: grep '💾' logs/mentor_mind_*.log")

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_auto_save()
    print(f"🕐 Test ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 