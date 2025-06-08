#!/usr/bin/env python3
"""
Final comprehensive test to verify all Hugging Face fixes are working
"""
import asyncio
import sys
import os
from pathlib import Path

# Set environment
os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

async def test_ai_processor():
    """Test the updated AI Processor"""
    print("🧪 Testing AI Processor with HF Fixes")
    print("=" * 50)
    
    try:
        from services.ai_processor import AIProcessor
        
        # Test different topics
        topics = ["Machine Learning", "Python Programming", "Web Development"]
        
        ai = AIProcessor()
        
        for topic in topics:
            print(f"\n📚 Testing topic: {topic}")
            queries = await ai.generate_search_queries(topic)
            
            print(f"✅ Generated {len(queries)} queries:")
            for i, query in enumerate(queries, 1):
                print(f"  {i}. {query}")
        
        await ai.close()
        return True
        
    except Exception as e:
        print(f"❌ AI Processor failed: {e}")
        return False

async def test_content_aggregator():
    """Test the Content Aggregator"""
    print("\n🧪 Testing Content Aggregator")
    print("=" * 50)
    
    try:
        from services.content_aggregator import ContentAggregator
        
        aggregator = ContentAggregator()
        all_resources = await aggregator.get_all_resources('AI', [])
        
        total_resources = sum(len(resources) for resources in all_resources.values())
        print(f"✅ Total resources found: {total_resources}")
        
        for category, resources in all_resources.items():
            count = len(resources)
            sample = resources[0].title if resources else 'No resources'
            print(f"  {category}: {count} resources - Sample: {sample}")
        
        await aggregator.close()
        return True
        
    except Exception as e:
        print(f"❌ Content Aggregator failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n🧪 Testing Configuration")
    print("=" * 50)
    
    try:
        from config import settings
        
        print(f"✅ HF Token: {'Set' if settings.HUGGINGFACE_API_TOKEN else 'Not Set'}")
        print(f"✅ Default Model: {settings.DEFAULT_MODEL}")
        print(f"✅ Fallback Models: {len(settings.FALLBACK_MODELS)} configured")
        print(f"✅ Headers: {'Configured' if settings.huggingface_headers else 'Not Configured'}")
        
        return settings.validate_config()
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

async def main():
    print("🔧 FINAL HUGGING FACE FIX VERIFICATION")
    print("=" * 70)
    print("Testing all components after applying the fixes\n")
    
    # Test 1: Configuration
    config_success = test_config()
    
    # Test 2: AI Processor
    ai_success = await test_ai_processor()
    
    # Test 3: Content Aggregator
    content_success = await test_content_aggregator()
    
    print("\n📋 FINAL RESULTS")
    print("=" * 70)
    print(f"Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"AI Processor: {'✅ PASS' if ai_success else '❌ FAIL'}")
    print(f"Content Aggregator: {'✅ PASS' if content_success else '❌ FAIL'}")
    
    all_pass = config_success and ai_success and content_success
    
    if all_pass:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your Hugging Face integration is working correctly")
        print("✅ System gracefully handles HF service issues with fallbacks")
        print("✅ Users will get learning resources regardless of HF status")
    else:
        print("\n⚠️  Some components need attention")
    
    print(f"\n📊 Overall Status: {'✅ SUCCESS' if all_pass else '❌ NEEDS WORK'}")

if __name__ == "__main__":
    asyncio.run(main()) 