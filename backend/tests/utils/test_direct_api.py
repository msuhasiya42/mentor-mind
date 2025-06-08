#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

from backend.services.content_aggregator import ContentAggregator

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