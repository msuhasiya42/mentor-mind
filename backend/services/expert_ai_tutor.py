"""
Expert AI Tutor Service - Multi-provider LLM-based resource curation
Supports Gemini, OpenAI, and OpenRouter APIs with automatic fallback
"""
import asyncio
import aiohttp
import logging
import json
import time
import sys
import os
import re
from typing import List, Dict, Any, Optional, Union
from google import genai

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from constants import (
    OPENAI_API_BASE, FALLBACK_MODELS, get_model_provider
)

from .learning_path_generator import Resource
from .resource_curator import ResourceCurator
from .ai_response_parser import AIResponseParser

logger = logging.getLogger(__name__)


class ExpertAITutor:
    """Expert AI Tutor that provides curated learning resources via LLM"""
    
    def __init__(self, model: str = None):
        # Initialize logger first
        logger.info("🤖 INITIALIZING EXPERT AI TUTOR")
        
        # Configuration
        self.rate_limit_delay = 2  # seconds between API calls
        self.max_consecutive_failures = 3
        self.consecutive_failures = 0
        self.last_api_call = 0
        self.session = None
        self.last_response_source = None
        self.last_provider = None
        self.provider = get_model_provider(model)
        
        # Model configuration
        self.model = model or settings.DEFAULT_MODEL
        
        # Initialize services
        self.resource_curator = ResourceCurator()
        self.response_parser = AIResponseParser()
        
        # Initialize Google Generative AI client if API key is available
        self.gemini_client = None
        if settings.GEMINI_API_KEY:
            try:
                self.gemini_client = genai.Client()
                logger.info("✅ Google Generative AI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Generative AI client: {str(e)}")
        
        # Log initialization
        logger.info("✅ Expert AI Tutor initialized")
        logger.info(f"   Provider: {self.provider.upper()}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Available providers: {', '.join(settings.get_available_providers())}")
    
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
        if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY:
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
    
    async def _call_llm_api(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        """Call the appropriate LLM API based on the provider"""
        model = model or self.model
        provider = get_model_provider(model)
        
        # Update instance state
        self.model = model
        self.provider = provider
        self.last_provider = provider
        
        # Select the appropriate API handler
        if provider == 'gemini':
            return await self._call_gemini_api(messages, model)
        elif provider == 'openai':
            return await self._call_openai_api(messages, model)
    
    async def _call_gemini_api(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """Call Google's Gemini API using the official client"""
        if not self.gemini_client:
            raise ValueError("Google Generative AI client not initialized. Check your API key configuration.")
        
        # Convert messages to the format expected by the Gemini client
        contents = []
        for msg in messages:
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append({"role": role, "parts": [{"text": msg['content']}]})
        
        try:
            # Call the Gemini API using the official client
            response = self.gemini_client.models.generate_content(
                model=model,
                contents=contents,
                config={
                    "temperature": 0.2,
                    "max_output_tokens": 2000
                }
            )
            
            # Extract the response text
            if response and hasattr(response, 'text'):
                return {
                    "choices": [{
                        "message": {
                            "content": response.text,
                            "role": "assistant"
                        }
                    }]
                }
            else:
                raise ValueError("Invalid response format from Gemini API")
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
        
        return await self._make_api_request(api_url, payload, headers={"Content-Type": "application/json"})
    
    async def _call_openai_api(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """Call OpenAI's API"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
            
        api_url = f"{OPENAI_API_BASE}{self.model_info['endpoint']}"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2000,
        }
        
        return await self._make_api_request(api_url, payload, settings.openai_headers)

    async def _make_api_request(self, url: str, payload: Dict, headers: Dict) -> Dict[str, Any]:
        """Make an HTTP request to the LLM API"""
        session = await self._get_session()
        self.last_api_call = time.time()
        
        try:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90)
            ) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    error_msg = f"API request failed with status {response.status}: {response_text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                return json.loads(response_text)
                
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise
    
    async def _get_ai_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get AI-curated resources with automatic fallback between providers"""
        logger.info(f"🚀 Starting AI API call with provider: {self.provider}")
        
        # Create system and user messages
        system_message = {
            "role": "system",
            "content": """You are an expert AI tutor with 15+ years of experience in technology education. 
You specialize in recommending the BEST and most FAMOUS learning resources.

IMPORTANT: Respond ONLY with valid JSON in the exact format requested. 
Do not include any other text, explanations, or markdown formatting.
Provide REAL, SPECIFIC resources that are well-known in the developer community."""
        }
        
        user_message = {
            "role": "user",
            "content": self._create_json_prompt(topic)
        }
        
        messages = [system_message, user_message]
        
        # Try the current model first, then fallback models
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        
        last_error = None
        
        for model in models_to_try:
            try:
                # Skip if we don't have the required API key
                provider = get_model_provider(model)
                if (provider == 'gemini' and not settings.GEMINI_API_KEY) or \
                   (provider == 'openai' and not settings.OPENAI_API_KEY) or \
                   (provider == 'openrouter' and not settings.OPENROUTER_API_KEY):
                    logger.warning(f"Skipping {model} - missing API key for {provider}")
                    continue
                
                logger.info(f"🔍 Trying model: {model} ({provider})")
                
                # Make the API call
                response = await self._call_llm_api(messages, model)
                
                # Process the response based on the provider
                if provider == 'gemini':
                    # Gemini responses are already converted to OpenAI format in _call_gemini_api
                    if 'choices' in response and response['choices'] and 'message' in response['choices'][0]:
                        content = response['choices'][0]['message']['content']
                        logger.info(f"Extracted Gemini (converted) content: {content[:200]}...")
                    else:
                        logger.warning("Unexpected Gemini response format after conversion")
                        content = str(response)
                elif 'choices' in response and response['choices'] and 'message' in response['choices'][0]:
                    # Handle OpenAI/OpenRouter response format
                    content = response['choices'][0]['message']['content']
                    logger.info(f"Extracted {provider} content: {content[:200]}...")
                else:
                    logger.warning("Unrecognized response structure")
                    content = str(response)
                    
                # Clean the content by removing markdown code blocks if present
                def clean_json_content(text):
                    # Remove ```json and ``` markers
                    text = re.sub(r'^\s*```(?:json\s*)?', '', text, flags=re.IGNORECASE)
                    text = re.sub(r'```\s*$', '', text, flags=re.IGNORECASE)
                    return text.strip()
                
                # Parse the JSON response
                try:
                    cleaned_content = clean_json_content(content)
                    resources_data = json.loads(cleaned_content)
                    
                    # Convert to Resource objects
                    resources = {}
                    for resource_type, items in resources_data.items():
                        resources[resource_type] = [
                            Resource(
                                title=item.get('title', ''),
                                url=item.get('url', ''),
                                description=item.get('description', ''),
                                platform=item.get('platform', ''),
                                price=item.get('price', '')
                            )
                            for item in items
                            if item.get('title') and item.get('url')
                        ]
                    
                    # Log success
                    total_resources = sum(len(r) for r in resources.values())
                    logger.info(f"✅ Successfully parsed {total_resources} resources from {provider} ({model})")
                    
                    # Reset failure count on success
                    self.consecutive_failures = 0
                    return resources
                    
                except json.JSONDecodeError as je:
                    logger.warning(f"❌ Failed to parse {provider} response as JSON, trying next model...")
                    logger.debug(f"   Error: {str(je)}")
                    logger.debug(f"   Response content: {content[:500]}...")
                    last_error = je
                    continue
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {provider} response: {str(e)}")
                    last_error = e
                    continue
                    
            except Exception as e:
                logger.error(f"❌ API call to {provider} failed: {str(e)}")
                last_error = e
                continue
        
        # If we get here, all models failed
        self.consecutive_failures += 1
        logger.error(f"❌ All model attempts failed. Last error: {str(last_error)}" if last_error else "❌ All model attempts failed")
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
  ]
}}

Requirements:
- Provide 3-5 resources per category
- Use REAL, SPECIFIC resources that are well-known
- Include actual URLs when possible
- Focus on high-quality, popular resources
- Ensure all prices are accurately marked as "Free" or with specific amounts

Topic: {topic}"""

        prompt = prompt.strip()
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