#!/usr/bin/env python3
"""
Detailed test for AI topic search - shows comprehensive resource breakdown
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add backend to path - get the correct backend path
import os
current_dir = os.getcwd()
if current_dir.endswith('backend'):
    # Already in backend directory
    sys.path.insert(0, current_dir)
else:
    # Add backend directory to path
    backend_path = Path(__file__).parent.parent.parent / "backend"
    sys.path.insert(0, str(backend_path))

from services.search_engines import LLMSearchEngine

def categorize_resources(resources):
    """Categorize resources by type and other attributes"""
    categories = {
        'documentation': [],
        'courses': [],
        'videos': [],
        'blogs': [],
        'repositories': [],
        'books': [],
        'tutorials': []
    }
    
    free_resources = []
    paid_resources = []
    personas = {}
    platforms = {}
    difficulties = {'Beginner': [], 'Intermediate': [], 'Advanced': [], 'All Levels': []}
    
    for resource in resources:
        # Categorize by type
        resource_type = resource.get('type', 'tutorial')
        if resource_type == 'course':
            categories['courses'].append(resource)
        elif resource_type == 'video':
            categories['videos'].append(resource)
        elif resource_type == 'documentation':
            categories['documentation'].append(resource)
        elif resource_type == 'blog':
            categories['blogs'].append(resource)
        elif resource_type == 'repository':
            categories['repositories'].append(resource)
        elif resource_type == 'book':
            categories['books'].append(resource)
        else:
            categories['tutorials'].append(resource)
        
        # Categorize by price
        if resource.get('price', '').lower() == 'free':
            free_resources.append(resource)
        else:
            paid_resources.append(resource)
        
        # Group by persona
        persona = resource.get('persona_source', 'unknown')
        if persona not in personas:
            personas[persona] = []
        personas[persona].append(resource)
        
        # Group by platform
        platform = resource.get('platform', 'Unknown')
        if platform not in platforms:
            platforms[platform] = []
        platforms[platform].append(resource)
        
        # Group by difficulty
        difficulty = resource.get('difficulty', 'All Levels')
        if difficulty in difficulties:
            difficulties[difficulty].append(resource)
    
    return categories, free_resources, paid_resources, personas, platforms, difficulties

def print_detailed_results(resources):
    """Print comprehensive breakdown of AI learning resources"""
    if not resources:
        print("❌ No resources generated")
        return
    
    categories, free_resources, paid_resources, personas, platforms, difficulties = categorize_resources(resources)
    
    print(f"\n🎯 COMPREHENSIVE AI LEARNING RESOURCES ({len(resources)} total)")
    print("=" * 70)
    
    # Overview
    print(f"\n📊 OVERVIEW:")
    print(f"   Total Resources: {len(resources)}")
    print(f"   Free Resources: {len(free_resources)}")
    print(f"   Paid Resources: {len(paid_resources)}")
    print(f"   Unique Platforms: {len(platforms)}")
    
    # Resources by category
    print(f"\n📚 RESOURCES BY CATEGORY:")
    for category, items in categories.items():
        if items:
            print(f"\n   {category.upper()} ({len(items)} resources):")
            for item in items:
                price_indicator = "🆓" if item.get('price', '').lower() == 'free' else "💰"
                difficulty = item.get('difficulty', 'All Levels')
                print(f"     {price_indicator} {item['title']}")
                print(f"        Platform: {item['platform']} | Difficulty: {difficulty}")
                print(f"        URL: {item['url']}")
                print(f"        Description: {item['description']}")
                print()
    
    # Free vs Paid breakdown
    print(f"\n💰 PRICING BREAKDOWN:")
    print(f"\n   🆓 FREE RESOURCES ({len(free_resources)}):")
    for resource in free_resources[:5]:  # Show first 5
        print(f"     • {resource['title']} ({resource['platform']})")
    
    if paid_resources:
        print(f"\n   💰 PAID RESOURCES ({len(paid_resources)}):")
        for resource in paid_resources[:5]:  # Show first 5
            print(f"     • {resource['title']} ({resource['platform']})")
    
    # Platform distribution
    print(f"\n🌐 PLATFORM DISTRIBUTION:")
    for platform, items in sorted(platforms.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {platform}: {len(items)} resources")
    
    # Difficulty levels
    print(f"\n📈 DIFFICULTY LEVELS:")
    for level, items in difficulties.items():
        if items:
            print(f"   {level}: {len(items)} resources")
    
    # Persona breakdown
    print(f"\n🎭 PERSONA CONTRIBUTIONS:")
    for persona, items in personas.items():
        persona_name = persona.replace('_', ' ').title()
        print(f"   {persona_name}: {len(items)} resources")

async def test_ai_search_comprehensive():
    """Comprehensive test of AI topic search"""
    print("🤖 AI LEARNING RESOURCES - COMPREHENSIVE TEST")
    print("=" * 70)
    
    search_engine = LLMSearchEngine()
    
    try:
        print("\n🔍 Searching for 'AI' learning resources...")
        print("   Using 4 different AI personas for diverse perspectives...")
        
        resources = await search_engine.search("AI")
        
        if resources:
            print(f"✅ Successfully generated {len(resources)} resources")
            print_detailed_results(resources)
        else:
            print("⚠️  No resources from LLM, testing fallback generation...")
            fallback_resources = search_engine._generate_fallback_resources("AI")
            print(f"✅ Generated {len(fallback_resources)} fallback resources")
            print_detailed_results(fallback_resources)
        
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        print("\n🔄 Testing fallback generation...")
        fallback_resources = search_engine._generate_fallback_resources("AI")
        print(f"✅ Generated {len(fallback_resources)} fallback resources")
        print_detailed_results(fallback_resources)
    
    finally:
        await search_engine.close()

async def test_specific_ai_subtopics():
    """Test specific AI subtopics"""
    print("\n\n🎯 TESTING SPECIFIC AI SUBTOPICS")
    print("=" * 70)
    
    subtopics = [
        "Machine Learning",
        "Deep Learning", 
        "Natural Language Processing",
        "Computer Vision",
        "AI Ethics"
    ]
    
    search_engine = LLMSearchEngine()
    
    for topic in subtopics:
        print(f"\n🔍 Topic: {topic}")
        print("-" * 50)
        
        try:
            resources = await search_engine.search(topic)
            if not resources:
                resources = search_engine._generate_fallback_resources(topic)
            
            # Show quick summary
            categories, free_resources, paid_resources, personas, platforms, difficulties = categorize_resources(resources)
            
            print(f"   📊 Generated {len(resources)} resources")
            print(f"   🆓 Free: {len(free_resources)} | 💰 Paid: {len(paid_resources)}")
            print(f"   📚 Categories: {', '.join([cat for cat, items in categories.items() if items])}")
            print(f"   🌐 Top Platforms: {', '.join(list(platforms.keys())[:3])}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    await search_engine.close()

def show_example_ai_resources():
    """Show what comprehensive AI resources would look like"""
    print("\n\n📝 EXAMPLE: WHAT COMPREHENSIVE AI RESOURCES LOOK LIKE")
    print("=" * 70)
    
    example_resources = [
        {
            'title': 'MIT Introduction to Machine Learning',
            'url': 'https://ocw.mit.edu/courses/machine-learning',
            'description': 'Comprehensive university-level course covering ML fundamentals',
            'platform': 'MIT OpenCourseWare',
            'difficulty': 'Intermediate',
            'price': 'Free',
            'type': 'course',
            'persona_source': 'academic_educator'
        },
        {
            'title': 'Andrew Ng Machine Learning Course',
            'url': 'https://www.coursera.org/learn/machine-learning',
            'description': 'Industry-standard ML course by Stanford professor',
            'platform': 'Coursera',
            'difficulty': 'Beginner',
            'price': 'Free',
            'type': 'course',
            'persona_source': 'industry_expert'
        },
        {
            'title': 'Python Machine Learning Hands-On Tutorial',
            'url': 'https://www.youtube.com/watch?v=example',
            'description': 'Practical coding tutorial with real projects',
            'platform': 'YouTube',
            'difficulty': 'Intermediate',
            'price': 'Free',
            'type': 'video',
            'persona_source': 'technical_mentor'
        },
        {
            'title': 'Awesome Machine Learning GitHub Repository',
            'url': 'https://github.com/josephmisiti/awesome-machine-learning',
            'description': 'Curated list of ML frameworks, libraries and software',
            'platform': 'GitHub',
            'difficulty': 'All Levels',
            'price': 'Free',
            'type': 'repository',
            'persona_source': 'content_curator'
        },
        {
            'title': 'Hands-On Machine Learning Book',
            'url': 'https://www.amazon.com/hands-on-machine-learning',
            'description': 'Practical guide to ML with TensorFlow and Scikit-Learn',
            'platform': 'Amazon',
            'difficulty': 'Intermediate',
            'price': 'Paid',
            'type': 'book',
            'persona_source': 'academic_educator'
        }
    ]
    
    print_detailed_results(example_resources)

if __name__ == "__main__":
    asyncio.run(test_ai_search_comprehensive())
    asyncio.run(test_specific_ai_subtopics())
    show_example_ai_resources() 