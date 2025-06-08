#!/usr/bin/env python3
"""
Test script for the new LLM-Only Search Engine
Demonstrates persona-based learning resource generation
"""

import asyncio
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.search_engines import LLMSearchEngine


async def test_llm_search():
    """Test the LLM-based search engine with different topics"""
    
    search_engine = LLMSearchEngine()
    
    test_topics = [
        "React Hooks",
        "Python Machine Learning",
        "Docker Containers",
        "JavaScript Async/Await",
        "System Design"
    ]
    
    print("🔍 Testing LLM-Only Search Engine")
    print("=" * 50)
    
    for topic in test_topics:
        print(f"\n🎯 Topic: {topic}")
        print("-" * 30)
        
        try:
            resources = await search_engine.search(topic)
            
            print(f"📊 Generated {len(resources)} resources")
            
            # Group by persona source
            persona_groups = {}
            for resource in resources:
                persona = resource.get('persona_source', 'unknown')
                if persona not in persona_groups:
                    persona_groups[persona] = []
                persona_groups[persona].append(resource)
            
            # Display results by persona
            for persona, persona_resources in persona_groups.items():
                print(f"\n🎭 {persona.title().replace('_', ' ')}: {len(persona_resources)} resources")
                
                for resource in persona_resources[:3]:  # Show first 3 resources
                    print(f"  📌 {resource['title']}")
                    print(f"     Platform: {resource['platform']} | Difficulty: {resource['difficulty']} | Price: {resource['price']}")
                    print(f"     Type: {resource['type']} | URL: {resource['url'][:50]}...")
                    print()
            
        except Exception as e:
            print(f"❌ Error testing {topic}: {str(e)}")
        
        print("-" * 50)
    
    await search_engine.close()
    print("\n✅ Test completed!")


async def demonstrate_personas():
    """Demonstrate how different personas generate different types of resources"""
    
    print("\n🎭 Persona Demonstration")
    print("=" * 50)
    
    search_engine = LLMSearchEngine()
    topic = "JavaScript Frameworks"
    
    # Test each persona individually
    for persona_name, persona_config in search_engine.personas.items():
        print(f"\n🎯 Persona: {persona_name.title().replace('_', ' ')}")
        print(f"Role: {persona_config['role']}")
        print(f"Style: {persona_config['style']}")
        print("-" * 30)
        
        try:
            resources = await search_engine._generate_resources_with_persona(
                topic, persona_name, persona_config
            )
            
            print(f"Generated {len(resources)} resources:")
            for resource in resources[:3]:
                print(f"  • {resource['title']} ({resource['type']})")
                
        except Exception as e:
            print(f"Error with {persona_name}: {str(e)}")
    
    await search_engine.close()


def show_example_output():
    """Show example of what the LLM search engine outputs"""
    
    print("\n📝 Example Output Structure")
    print("=" * 50)
    
    example_resource = {
        'title': 'React Hooks Complete Guide',
        'url': 'https://www.youtube.com/results?search_query=React+Hooks+Complete+Guide',
        'description': 'Comprehensive tutorial covering all React Hooks with practical examples',
        'platform': 'YouTube',
        'difficulty': 'Intermediate',
        'price': 'Free',
        'type': 'video',
        'persona_source': 'technical_mentor'
    }
    
    print("Resource Structure:")
    print(json.dumps(example_resource, indent=2))
    
    print("\n🏷️ Resource Types:")
    resource_types = ['documentation', 'course', 'video', 'blog', 'repository', 'book', 'tutorial']
    for rtype in resource_types:
        print(f"  • {rtype}")
    
    print("\n🎭 Persona Sources:")
    personas = ['technical_mentor', 'academic_educator', 'industry_expert', 'content_curator']
    for persona in personas:
        print(f"  • {persona.replace('_', ' ').title()}")


if __name__ == "__main__":
    print("🚀 MentorMind LLM-Only Search Engine Demo")
    print("=" * 60)
    
    # Show example output structure
    show_example_output()
    
    # Run the tests
    try:
        asyncio.run(test_llm_search())
        asyncio.run(demonstrate_personas())
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("💡 Make sure you have configured your Hugging Face API token in the environment") 