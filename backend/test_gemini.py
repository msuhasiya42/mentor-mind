import asyncio
import logging
import json
from config import settings
from services.expert_ai_tutor import ExpertAITutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_gemini():
    print("\n=== Testing Gemini API Integration ===")
    print(f"Using model: {settings.DEFAULT_MODEL}")
    print(f"Available providers: {settings.get_available_providers()}")
    
    tutor = ExpertAITutor()
    print(f"\nInitialized tutor with model: {tutor.model} (provider: {tutor.provider})")
    
    try:
        print("\nTesting with query: 'Python programming'")
        resources = await tutor._get_ai_curated_resources("Python programming")
        
        if resources:
            print("\n✅ Success! Received resources:")
            for resource_type, items in resources.items():
                print(f"\n{resource_type.upper()} ({len(items)}):")
                for item in items[:3]:  # Show first 3 items of each type
                    print(f"- {getattr(item, 'title', 'No title')}")
                    if hasattr(item, 'url'):
                        print(f"  URL: {item.url}")
                    if hasattr(item, 'description'):
                        print(f"  Description: {item.description[:100]}...")
                    print()
                if len(items) > 3:
                    print(f"... and {len(items)-3} more")
        else:
            print("❌ No resources returned")
            
    except Exception as e:
        print(f"\n❌ Error during API call: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting test...")
    asyncio.run(test_gemini())
