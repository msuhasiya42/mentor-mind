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
        
        self.session = None
        self.last_api_call = 0
        self.rate_limit_delay = 2  # Minimum seconds between API calls
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.resource_curator = ResourceCurator()
        self.response_parser = AIResponseParser()
        self.last_response_source = None  # Track the source of the last response
        
        # Log initialization details
        logger.info("   Configuration:")
        logger.info(f"     - Rate limit delay: {self.rate_limit_delay}s")
        logger.info(f"     - Max consecutive failures: {self.max_consecutive_failures}")
        logger.info(f"     - OpenRouter API: {'✅ Available' if settings.OPENROUTER_API_KEY else '❌ Not available'}")
        logger.info(f"     - Default model: {settings.DEFAULT_MODEL}")
        logger.info("   Components:")
        logger.info("     - Resource Curator: ✅ Loaded")
        logger.info("     - AI Response Parser: ✅ Loaded")
        
        logger.info("✅ Expert AI Tutor initialized successfully")
    
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
        """Get curated learning resources from expert AI tutor"""
        logger.info("🎯 EXPERT AI TUTOR: Getting curated resources")
        logger.info(f"   Topic: '{topic}'")
        logger.info(f"   Current failure count: {self.consecutive_failures}/{self.max_consecutive_failures}")
        
        try:
            # Check if we should skip AI due to consecutive failures
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.warning("🚫 SKIPPING AI CALL - Too many consecutive failures")
                logger.warning(f"   Consecutive failures: {self.consecutive_failures}")
                logger.warning(f"   Max allowed: {self.max_consecutive_failures}")
                logger.warning("   🔄 Falling back to manual curation")
                
                manual_resources = self.resource_curator.get_curated_resources(topic)
                self.last_response_source = "📋 MANUAL CURATION (Too many AI failures)"
                logger.info("✅ Manual curation completed successfully")
                logger.info("   📋 RESPONSE SOURCE: MANUAL CURATION (Manual fallback due to AI failures)")
                return manual_resources
            
            # Try AI-powered resource curation first
            if settings.OPENROUTER_API_KEY:
                logger.info("🤖 ATTEMPTING AI-POWERED CURATION")
                logger.info(f"   API Key: {'✅ Available' if settings.OPENROUTER_API_KEY else '❌ Missing'}")
                logger.info(f"   Model: {settings.DEFAULT_MODEL}")
                
                await self._enforce_rate_limit()
                
                ai_resources = await self._get_ai_curated_resources(topic)
                if ai_resources:
                    self.consecutive_failures = 0  # Reset failure counter on success
                    total_ai_resources = sum(len(resources) for resources in ai_resources.values())
                    
                    self.last_response_source = "🤖 AI TUTOR (DeepSeek via OpenRouter)"
                    logger.info("✅ AI CURATION SUCCESSFUL")
                    logger.info(f"   Total AI resources: {total_ai_resources}")
                    logger.info("   🔄 Consecutive failures reset to 0")
                    logger.info("   🤖 RESPONSE SOURCE: AI TUTOR (DeepSeek/OpenRouter API)")
                    
                    # Log detailed breakdown
                    for category, resources in ai_resources.items():
                        logger.info(f"     - {category}: {len(resources)} resources")
                    
                    return ai_resources
                else:
                    self.consecutive_failures += 1
                    logger.warning("❌ AI CURATION FAILED")
                    logger.warning(f"   Consecutive failures incremented to: {self.consecutive_failures}")
                    logger.warning("   🔄 Falling back to manual curation")
            else:
                logger.warning("🚫 NO OPENROUTER API KEY CONFIGURED")
                logger.warning("   Skipping AI curation, using manual curation")
            
            # Fallback to manual curation
            logger.info("📝 USING MANUAL CURATION FALLBACK")
            manual_resources = self.resource_curator.get_curated_resources(topic)
            total_manual_resources = sum(len(resources) for resources in manual_resources.values())
            
            # Determine the specific reason for manual curation
            if not settings.OPENROUTER_API_KEY:
                self.last_response_source = "📋 MANUAL CURATION (No API key)"
            elif self.consecutive_failures > 0:
                self.last_response_source = "📋 MANUAL CURATION (AI partially failing)"
            else:
                self.last_response_source = "📋 MANUAL CURATION (Fallback)"
            
            logger.info("✅ Manual curation fallback completed")
            logger.info(f"   Total manual resources: {total_manual_resources}")
            logger.info("   📋 RESPONSE SOURCE: MANUAL CURATION (Fallback)")
            
            # Log detailed breakdown
            for category, resources in manual_resources.items():
                logger.info(f"     - {category}: {len(resources)} resources")
            
            return manual_resources
            
        except Exception as e:
            self.consecutive_failures += 1
            logger.error("💥 EXPERT AI TUTOR ERROR")
            logger.error(f"   Topic: '{topic}'")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Consecutive failures: {self.consecutive_failures}")
            logger.error("   🆘 Using basic fallback resources")
            
            basic_fallback = self.resource_curator.get_basic_fallback_resources(topic)
            total_fallback_resources = sum(len(resources) for resources in basic_fallback.values())
            
            self.last_response_source = "🔄 BASIC FALLBACK (Emergency fallback)"
            logger.info(f"✅ Basic fallback completed with {total_fallback_resources} resources")
            logger.info("   🔄 RESPONSE SOURCE: BASIC FALLBACK (Emergency fallback)")
            
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
        logger.info("🚀 INITIATING AI API CALL")
        logger.info(f"   Topic: '{topic}'")
        logger.info(f"   Target API: {settings.OPENROUTER_API_BASE}")
        logger.info(f"   Model: {settings.DEFAULT_MODEL}")
        
        api_start_time = time.time()
        
        try:
            session = await self._get_session()
            self.last_api_call = time.time()
            
            # Create simplified prompt that requests JSON format directly
            logger.info("📝 Creating AI prompt")
            prompt = self._create_json_prompt(topic)
            logger.debug(f"   Prompt length: {len(prompt)} characters")
            
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
            
            logger.info("📡 Sending API request")
            logger.info(f"   URL: {api_url}")
            logger.info(f"   Payload size: {len(json.dumps(payload))} bytes")
            
            # Add timing for the actual HTTP request
            request_start_time = time.time()
            logger.info("⏳ Starting HTTP request...")
            
            async with session.post(
                api_url,
                headers=settings.openrouter_headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90)
            ) as response:
                
                request_time = time.time() - request_start_time
                api_time = time.time() - api_start_time
                logger.info(f"📨 HTTP request completed in {request_time:.3f}s")
                logger.info(f"📨 Total API time so far: {api_time:.3f}s")
                logger.info(f"   Status: {response.status}")
                logger.info(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
                logger.info(f"   Content Length: {response.headers.get('content-length', 'Unknown')} bytes")
                
                if response.status == 200:
                    logger.info("✅ AI API CALL SUCCESSFUL")
                    
                    # Add timing for JSON parsing
                    json_start_time = time.time()
                    logger.info("🔍 Starting response JSON parsing...")
                    
                    result = await response.json()
                    
                    json_time = time.time() - json_start_time
                    logger.info(f"✅ JSON parsing completed in {json_time:.3f}s")
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        generated_text = result['choices'][0]['message']['content']
                        logger.info(f"   Response length: {len(generated_text)} characters")
                        logger.info("   🔍 Parsing AI response...")
                        
                        # Add timing for AI response parsing
                        parse_start_time = time.time()
                        
                        parsed_resources = self.response_parser.parse_json_response(generated_text, topic)
                        
                        parse_time = time.time() - parse_start_time
                        logger.info(f"   AI response parsing took {parse_time:.3f}s")
                        
                        if parsed_resources:
                            total_parsed = sum(len(resources) for resources in parsed_resources.values())
                            logger.info(f"✅ AI Response parsed successfully")
                            logger.info(f"   Total resources parsed: {total_parsed}")
                            logger.info("   🤖 CONFIRMED SOURCE: AI TUTOR (DeepSeek via OpenRouter)")
                            return parsed_resources
                        else:
                            logger.warning("❌ AI response parsing failed")
                            logger.warning("   Generated text could not be parsed into resources")
                    else:
                        logger.warning("❌ AI response missing 'choices' or empty")
                        logger.warning(f"   Response keys: {list(result.keys()) if result else 'None'}")
                        
                elif response.status == 429:
                    logger.warning("🚫 RATE LIMIT EXCEEDED")
                    logger.warning(f"   Current delay: {self.rate_limit_delay:.1f}s")
                    self.rate_limit_delay = min(self.rate_limit_delay * 1.5, 10)
                    logger.warning(f"   New delay: {self.rate_limit_delay:.1f}s")
                    
                else:
                    logger.warning(f"❌ AI API ERROR: HTTP {response.status}")
                    error_text = await response.text()
                    logger.warning(f"   Error response: {error_text[:200]}...")
                    
        except asyncio.TimeoutError:
            api_time = time.time() - api_start_time
            logger.error(f"⏰ AI API TIMEOUT after {api_time:.3f}s")
            logger.error("   The AI service took too long to respond")
            
        except Exception as e:
            api_time = time.time() - api_start_time
            logger.error(f"💥 AI API CALL FAILED after {api_time:.3f}s")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
        
        logger.warning("❌ AI curation failed, will use fallback")
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