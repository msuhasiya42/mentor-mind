"""
Expert AI Tutor Service - Simplified LLM-based resource curation
"""
import asyncio
import aiohttp
import logging
import json
import time
import sys
import os
from typing import List, Dict

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from .learning_path_generator import Resource
from .resource_curator import ResourceCurator
from .ai_response_parser import AIResponseParser

logger = logging.getLogger(__name__)


class ExpertAITutor:
    """Expert AI Tutor that provides curated learning resources via LLM"""
    
    def __init__(self):
        self.session = None
        self.last_api_call = 0
        self.rate_limit_delay = 2  # Minimum seconds between API calls
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.resource_curator = ResourceCurator()
        self.response_parser = AIResponseParser()
        logger.info("Expert AI Tutor initialized")
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=90)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def get_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get curated learning resources from expert AI tutor"""
        try:
            logger.info(f"Getting curated resources for: {topic}")
            
            # Check if we should skip AI due to consecutive failures
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.info(f"Skipping AI call due to {self.consecutive_failures} consecutive failures, using manual curation")
                return self.resource_curator.get_curated_resources(topic)
            
            # Try AI-powered resource curation first
            if settings.OPENROUTER_API_KEY:
                await self._enforce_rate_limit()
                
                ai_resources = await self._get_ai_curated_resources(topic)
                if ai_resources:
                    self.consecutive_failures = 0  # Reset failure counter on success
                    logger.info(f"AI tutor provided {sum(len(resources) for resources in ai_resources.values())} curated resources")
                    return ai_resources
                else:
                    self.consecutive_failures += 1
                    logger.warning(f"AI call failed, consecutive failures: {self.consecutive_failures}")
            
            # Fallback to manual curation
            logger.info("Using manual curation")
            return self.resource_curator.get_curated_resources(topic)
            
        except Exception as e:
            logger.error(f"Error getting curated resources: {str(e)}")
            self.consecutive_failures += 1
            return self.resource_curator.get_basic_fallback_resources(topic)
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        time_since_last_call = time.time() - self.last_api_call
        if time_since_last_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_call
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s before API call")
            await asyncio.sleep(wait_time)
    
    async def _get_ai_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get AI-curated resources using simplified JSON format request"""
        try:
            session = await self._get_session()
            self.last_api_call = time.time()
            
            # Create simplified prompt that requests JSON format directly
            prompt = self._create_json_prompt(topic)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert AI tutor with 15+ years of experience in technology education. 
You specialize in recommending the BEST and most FAMOUS learning resources.

IMPORTANT: Respond ONLY with valid JSON in the exact format requested. 
Do not include any other text, explanations, or markdown formatting.
Provide REAL, SPECIFIC resources that are well-known in the developer community."""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            payload = {
                "model": settings.DEFAULT_MODEL,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.2,
                "stream": False
            }
            
            api_url = f"{settings.OPENROUTER_API_BASE}/chat/completions"
            
            async with session.post(
                api_url,
                headers=settings.openrouter_headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        generated_text = result['choices'][0]['message']['content']
                        return self.response_parser.parse_json_response(generated_text, topic)
                elif response.status == 429:
                    logger.warning("Rate limit exceeded for OpenRouter")
                    self.rate_limit_delay = min(self.rate_limit_delay * 1.5, 10)
                    logger.info(f"Increased rate limit delay to {self.rate_limit_delay:.1f}s")
                else:
                    logger.warning(f"OpenRouter API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting AI curated resources: {str(e)}")
        
        return {}
    
    def _create_json_prompt(self, topic: str) -> str:
        """Create simplified prompt that requests resources in JSON format"""
        return f"""Please provide the BEST learning resources for "{topic}" in the following JSON format:

{{
  "docs": [
    {{"title": "Resource Title", "url": "https://example.com", "description": "Brief description", "platform": "Platform Name", "price": "Free"}}
  ],
  "blogs": [
    {{"title": "Blog Title", "url": "https://example.com", "description": "Brief description", "platform": "Platform Name", "price": "Free"}}
  ],
  "youtube": [
    {{"title": "Video Title", "url": "https://youtube.com/watch?v=...", "description": "Brief description", "platform": "YouTube", "price": "Free"}}
  ],
  "free_courses": [
    {{"title": "Course Title", "url": "https://example.com", "description": "Brief description", "platform": "Platform Name", "price": "Free"}}
  ],
  "paid_courses": [
    {{"title": "Course Title", "url": "https://example.com", "description": "Brief description", "platform": "Platform Name", "price": "$XX.XX"}}
  ]
}}

Requirements:
- Provide 3-5 resources per category
- Use REAL, SPECIFIC resources that are well-known
- Include actual URLs when possible
- Focus on high-quality, popular resources
- Ensure all prices are accurately marked as "Free" or with specific amounts

Topic: {topic}"""

    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Expert AI Tutor resources cleaned up") 