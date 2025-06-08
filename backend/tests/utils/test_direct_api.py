#!/usr/bin/env python3
import asyncio
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

os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

from services.content_aggregator import ContentAggregator

async def test_direct():
    print("🧪 Testing Content Aggregator Directly")
    print("=" * 50)
    
    aggregator = ContentAggregator()
    all_resources = await aggregator.get_all_resources('AI', [])
    
    print("Direct test results:")
    for category, resources in all_resources.items():
        count = len(resources)
        sample = resources[0].title if resources else 'No resources'
        print(f'  {category}: {count} resources - Sample: {sample}')
    
    await aggregator.close()

if __name__ == "__main__":
    asyncio.run(test_direct()) 