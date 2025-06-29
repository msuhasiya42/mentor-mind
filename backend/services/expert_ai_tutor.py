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
from typing import List, Dict, Tuple

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
        logger.info("🤖 INITIALIZING EXPERT AI TUTOR")
        
        # Configuration
        self.rate_limit_delay = 2  # seconds between API calls
        self.max_consecutive_failures = 3
        self.consecutive_failures = 0
        self.last_api_call = 0
        self.session = None
        self.last_response_source = None
        
        # Initialize services
        self.resource_curator = ResourceCurator()
        self.response_parser = AIResponseParser()
        
        logger.info("✅ Expert AI Tutor initialized")
        logger.info(f"   OpenRouter API: {'✅' if settings.OPENROUTER_API_KEY else '❌'}")
        logger.info(f"   Model: {settings.DEFAULT_MODEL}")
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            logger.debug("🔗 Creating new HTTP session")
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=180)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
            logger.debug("✅ HTTP session created")
        return self.session
    
    async def get_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get curated resources for a topic using AI or fallback methods"""
        logger.info("🎯 EXPERT AI TUTOR: Getting curated resources")
        logger.info(f"   Topic: '{topic}'")
        
        start_time = time.time()
        
        # Check if we should attempt AI curation
        if not settings.OPENROUTER_API_KEY:
            logger.warning("❌ No API key available, using manual curation")
            return await self._use_manual_curation(topic)
        
        if self.consecutive_failures >= self.max_consecutive_failures:
            logger.warning(f"❌ Too many failures ({self.consecutive_failures}/{self.max_consecutive_failures}), using manual curation")
            return await self._use_manual_curation(topic)
        
        try:
            # Enforce rate limiting
            await self._enforce_rate_limit()
            
            logger.info("🤖 ATTEMPTING AI-POWERED CURATION")
            
            # Try AI curation
            ai_resources = await self._get_ai_curated_resources(topic)
            
            if ai_resources and any(ai_resources.values()):
                total_ai_resources = sum(len(resources) for resources in ai_resources.values())
                processing_time = time.time() - start_time
                
                # Reset failure count on success
                self.consecutive_failures = 0
                
                self.last_response_source = "🤖 AI TUTOR (DeepSeek/OpenRouter API)"
                logger.info("✅ AI CURATION SUCCESSFUL")
                logger.info(f"   Resources: {total_ai_resources} | Time: {processing_time:.2f}s | Source: AI")
                
                return ai_resources
            else:
                logger.warning("❌ AI curation returned empty results")
                
        except Exception as e:
            logger.error("💥 AI curation failed")
            logger.error(f"   Error: {str(e)}")
        
        # Fallback to manual curation
        logger.info("🔄 Falling back to manual curation")
        return await self._use_manual_curation(topic)
    
    async def _use_manual_curation(self, topic: str) -> Dict[str, List[Resource]]:
        """Use manual curation as fallback"""
        manual_resources = self.resource_curator.get_curated_resources(topic)
        if manual_resources and any(manual_resources.values()):
            total_resources = sum(len(resources) for resources in manual_resources.values())
            self.last_response_source = "📋 MANUAL CURATION (Fallback)"
            logger.info(f"✅ Manual curation: {total_resources} resources")
            return manual_resources
        else:
            # Emergency basic fallback
            self.consecutive_failures += 1
            basic_fallback = self.resource_curator.get_basic_fallback_resources(topic)
            total_resources = sum(len(resources) for resources in basic_fallback.values())
            self.last_response_source = "🔄 BASIC FALLBACK (Emergency)"
            logger.info(f"✅ Basic fallback: {total_resources} resources")
            return basic_fallback

    def get_last_response_source(self) -> str:
        """Get the source of the last response"""
        return self.last_response_source or "No response yet"
    
    def get_source_info(self) -> Dict[str, any]:
        """Get detailed information about the current source state"""
        return {
            "last_source": self.last_response_source,
            "consecutive_failures": self.consecutive_failures,
            "max_failures": self.max_consecutive_failures,
            "has_api_key": bool(settings.OPENROUTER_API_KEY),
            "rate_limit_delay": self.rate_limit_delay,
            "is_ai_available": bool(settings.OPENROUTER_API_KEY) and self.consecutive_failures < self.max_consecutive_failures
        }
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between API calls"""
        time_since_last_call = time.time() - self.last_api_call
        if time_since_last_call < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last_call
            logger.info(f"⏱️ RATE LIMITING: Waiting {wait_time:.1f}s before API call")
            await asyncio.sleep(wait_time)
        else:
            logger.debug(f"✅ Rate limit OK: {time_since_last_call:.1f}s since last call")
    
    async def _get_ai_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get AI-curated resources using simplified JSON format request"""
        logger.info("🚀 Starting AI API call")
        
        api_start_time = time.time()
        
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
                
                request_time = time.time() - api_start_time
                
                if response.status == 200:
                    logger.info(f"📨 API response received ({request_time:.2f}s)")
                    
                    # Fetch response text once and store it
                    response_text = await response.text()
                    
                    # Parse the JSON response
                    json_start_time = time.time()
                    try:
                        result = json.loads(response_text)
                        json_time = time.time() - json_start_time
                        
                        if json_time > 5:  # Only log if JSON parsing is slow
                            logger.warning(f"⚠️ Slow JSON parsing: {json_time:.2f}s")
                        
                        # Log formatted response with appropriate level of detail
                        logger.info("🔄 API Response Summary:")
                        
                        if 'id' in result:
                            logger.info(f"   ID: {result.get('id')}")
                        if 'model' in result:
                            logger.info(f"   Model: {result.get('model')}")
                        if 'usage' in result:
                            usage = result.get('usage', {})
                            logger.info(f"   Tokens: {usage.get('total_tokens', 'N/A')} total "+ 
                                      f"({usage.get('prompt_tokens', 'N/A')} prompt, "+ 
                                      f"{usage.get('completion_tokens', 'N/A')} completion)")
                        
                        # Log choices summary if available
                        if 'choices' in result and len(result['choices']) > 0:
                            choice = result['choices'][0]
                            finish_reason = choice.get('finish_reason', 'unknown')
                            logger.info(f"   Finish reason: {finish_reason}")
                            
                            # For debugging purposes, log full JSON at debug level
                            if settings.DEBUG:
                                formatted_json = json.dumps(result, indent=2)
                                logger.debug(f"Full API Response:\n{formatted_json}")
                            
                            # Process the generated text
                            generated_text = choice['message']['content']
                            parsed_resources = self.response_parser.parse_json_response(generated_text, topic)
                            
                            if parsed_resources:
                                total_parsed = sum(len(resources) for resources in parsed_resources.values())
                                total_time = time.time() - api_start_time
                                logger.info(f"✅ AI parsing complete: {total_parsed} resources ({total_time:.2f}s total)")
                                return parsed_resources
                            else:
                                logger.warning("❌ AI response parsing failed")
                        else:
                            logger.warning("❌ No choices found in API response")
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Failed to parse API response as JSON: {e}")
                        logger.debug(f"Raw response text: {response_text[:500]}...")
                        
                elif response.status == 429:
                    logger.warning("🚫 Rate limit exceeded")
                    self.rate_limit_delay = min(self.rate_limit_delay * 1.5, 10)
                    
                else:
                    logger.warning(f"❌ API error: HTTP {response.status}")
                    try:
                        error_text = await response.text()
                        logger.debug(f"Error response: {error_text[:500]}...")
                    except Exception as e:
                        logger.debug(f"Could not read error response: {e}")
                        
                    
        except asyncio.TimeoutError:
            logger.error(f"⏰ API timeout after {time.time() - api_start_time:.2f}s")
            
        except Exception as e:
            logger.error(f"💥 API call failed: {str(e)}")
        
        return {}
    
    def _create_json_prompt(self, topic: str) -> str:
        """Create simplified prompt that requests resources in JSON format"""
        logger.debug(f"📝 Creating JSON prompt for topic: '{topic}'")
        
        prompt = f"""Please provide the BEST learning resources for "{topic}" in the following JSON format:

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

        logger.debug(f"   Prompt created with {len(prompt)} characters")
        return prompt

    async def close(self):
        """Clean up resources"""
        logger.info("🧹 CLEANING UP EXPERT AI TUTOR")
        
        if self.session:
            logger.info("   Closing HTTP session...")
            await self.session.close()
            self.session = None
            logger.info("   ✅ HTTP session closed")
        
        logger.info("✅ Expert AI Tutor cleanup completed")
        logger.info(f"   Final failure count: {self.consecutive_failures}")
        logger.info(f"   Final rate limit delay: {self.rate_limit_delay:.1f}s")
        logger.info(f"   Last response source: {self.last_response_source}") 