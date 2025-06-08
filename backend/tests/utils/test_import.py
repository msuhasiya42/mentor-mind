#!/usr/bin/env python3
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