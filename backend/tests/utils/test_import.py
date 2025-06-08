#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

os.environ['HUGGINGFACE_API_TOKEN'] = 'your_huggingface_token_here'

from backend.services.content_aggregator import ContentAggregator

def test_import():
    print("Testing ContentAggregator import...")
    aggregator = ContentAggregator()
    
    print(f"Has get_all_resources: {hasattr(aggregator, 'get_all_resources')}")
    print(f"Has llm_search: {hasattr(aggregator, 'llm_search')}")
    
    if hasattr(aggregator, 'llm_search'):
        print(f"LLM search type: {type(aggregator.llm_search)}")
    
    # Check methods
    methods = [method for method in dir(aggregator) if not method.startswith('_')]
    print(f"Available methods: {methods}")

if __name__ == "__main__":
    test_import() 