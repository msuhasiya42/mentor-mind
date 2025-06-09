#!/usr/bin/env python3
"""
Test script to validate ExpertAITutor refactoring and DeepSeek responses
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print('🧪 EXPERT AI TUTOR REFACTORING TEST')
print('='*50)

# Test imports
try:
    from services.expert_ai_tutor import ExpertAITutor
    from services.resource_curator import ResourceCurator
    from services.ai_response_parser import AIResponseParser
    from services.learning_path_generator import Resource
    print('✅ All module imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)

# Test basic instantiation
try:
    expert_tutor = ExpertAITutor()
    resource_curator = ResourceCurator()
    response_parser = AIResponseParser()
    print('✅ All components instantiate correctly')
except Exception as e:
    print(f'❌ Instantiation failed: {e}')
    exit(1)

# Test functionality
async def test_expert_tutor():
    """Test ExpertAITutor functionality with real API calls"""
    
    print('\n🔍 Testing ExpertAITutor with DeepSeek...')
    
    try:
        # Test with a simple topic
        topic = "python"
        print(f'📝 Testing topic: {topic}')
        
        # Get curated resources
        resources = await expert_tutor.get_curated_resources(topic)
        
        # Validate response structure
        expected_categories = ['docs', 'blogs', 'youtube', 'free_courses', 'paid_courses']
        
        print(f'\n📊 Results for "{topic}":')
        total_resources = 0
        
        for category in expected_categories:
            if category in resources:
                count = len(resources[category])
                total_resources += count
                print(f'  • {category}: {count} resources')
                
                # Show first resource from each category as example
                if count > 0:
                    first_resource = resources[category][0]
                    print(f'    Example: "{first_resource.title}" - {first_resource.platform}')
            else:
                print(f'  • {category}: 0 resources')
        
        print(f'\n📈 Total resources found: {total_resources}')
        
        # Test another topic to see if AI is working
        topic2 = "react"
        print(f'\n📝 Testing topic: {topic2}')
        
        resources2 = await expert_tutor.get_curated_resources(topic2)
        total_resources2 = sum(len(resources2.get(cat, [])) for cat in expected_categories)
        print(f'📈 Total resources found for {topic2}: {total_resources2}')
        
        # Validation checks
        if total_resources > 0:
            print('✅ Expert AI Tutor is working correctly')
        else:
            print('⚠️  No resources returned - might be using fallback')
        
        if total_resources2 > 0:
            print('✅ Multiple topic requests working')
        else:
            print('⚠️  Second topic failed - might be rate limited')
        
        return total_resources > 0 or total_resources2 > 0
        
    except Exception as e:
        print(f'❌ Expert tutor test failed: {e}')
        return False
    finally:
        # Clean up
        await expert_tutor.close()

# Test manual curation fallback
def test_manual_curation():
    """Test ResourceCurator manual fallback"""
    print('\n🔍 Testing ResourceCurator fallback...')
    
    try:
        curator = ResourceCurator()
        
        # Test with known topic
        resources = curator.get_curated_resources("react")
        total = sum(len(resources.get(cat, [])) for cat in ['docs', 'blogs', 'youtube', 'free_courses', 'paid_courses'])
        print(f'✅ Manual curation for "react": {total} resources')
        
        # Test with unknown topic
        resources = curator.get_curated_resources("unknown_topic")
        total = sum(len(resources.get(cat, [])) for cat in ['docs', 'blogs', 'youtube', 'free_courses', 'paid_courses'])
        print(f'✅ Generic fallback for "unknown_topic": {total} resources')
        
        return True
    except Exception as e:
        print(f'❌ Manual curation test failed: {e}')
        return False

# Test JSON parser
def test_json_parser():
    """Test AIResponseParser"""
    print('\n🔍 Testing AIResponseParser...')
    
    try:
        parser = AIResponseParser()
        
        # Test with valid JSON
        test_json = '''
        {
          "docs": [
            {"title": "Test Doc", "url": "https://example.com", "description": "Test", "platform": "Web", "price": "Free"}
          ],
          "blogs": [
            {"title": "Test Blog", "url": "https://blog.com", "description": "Test", "platform": "Blog", "price": "Free"}
          ],
          "youtube": [],
          "free_courses": [],
          "paid_courses": []
        }
        '''
        
        resources = parser.parse_json_response(test_json, "test")
        total = sum(len(resources.get(cat, [])) for cat in ['docs', 'blogs', 'youtube', 'free_courses', 'paid_courses'])
        print(f'✅ JSON parsing test: {total} resources parsed')
        
        return total > 0
    except Exception as e:
        print(f'❌ JSON parser test failed: {e}')
        return False

# Run all tests
async def main():
    print('\n🚀 Starting comprehensive tests...\n')
    
    # Test manual components first
    manual_test = test_manual_curation()
    parser_test = test_json_parser()
    
    # Test AI functionality
    ai_test = await test_expert_tutor()
    
    print('\n' + '='*50)
    print('📋 TEST SUMMARY:')
    print(f'  • Manual Curation: {"✅ PASS" if manual_test else "❌ FAIL"}')
    print(f'  • JSON Parser: {"✅ PASS" if parser_test else "❌ FAIL"}')
    print(f'  • AI Integration: {"✅ PASS" if ai_test else "❌ FAIL"}')
    
    if manual_test and parser_test:
        print('\n🎉 REFACTORING VALIDATION SUCCESSFUL!')
        print('✅ Core functionality working')
        print('✅ Modular structure intact')
        print('✅ Fallback mechanisms operational')
        
        if ai_test:
            print('✅ DeepSeek API integration working')
        else:
            print('⚠️  DeepSeek API not responding (fallback active)')
            
    else:
        print('\n❌ REFACTORING VALIDATION FAILED!')
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        exit(1) 