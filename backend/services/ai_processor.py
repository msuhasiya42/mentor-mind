import asyncio
import logging
import aiohttp
import json
from typing import List, Dict, Any
from dataclasses import dataclass
import re
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

logger = logging.getLogger(__name__)

@dataclass
class Resource:
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""

class AIProcessor:
    def __init__(self):
        self.session = None
        self.request_count = 0  # Track requests for rate limiting
        
        logger.info("AIProcessor initialized with OpenRouter integration")
        
        # Common technology keywords for better search query generation
        self.tech_keywords = {
            'react': ['jsx', 'hooks', 'components', 'state management', 'redux'],
            'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy', 'machine learning'],
            'javascript': ['es6', 'nodejs', 'typescript', 'async', 'promises'],
            'machine learning': ['tensorflow', 'pytorch', 'scikit-learn', 'neural networks'],
            'web development': ['html', 'css', 'javascript', 'responsive design'],
            'data science': ['python', 'r', 'pandas', 'matplotlib', 'jupyter'],
            'backend': ['api', 'database', 'server', 'microservices'],
            'frontend': ['ui', 'ux', 'responsive', 'css', 'javascript']
        }
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def _call_openrouter_api(self, messages: List[Dict], model: str = None, max_tokens: int = 150) -> str:
        """
        Call OpenRouter API with OpenAI-compatible format
        """
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OpenRouter API key not found, using fallback")
            return None
            
        if model is None:
            model = settings.DEFAULT_MODEL
            
        try:
            session = await self._get_session()
            
            # Check rate limiting
            self.request_count += 1
            if self.request_count >= settings.RATE_LIMIT_WARNING_THRESHOLD:
                logger.warning(f"Approaching rate limit: {self.request_count} requests made")
            
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False
            }
            
            api_url = f"{settings.OPENROUTER_API_BASE}/chat/completions"
            
            async with session.post(
                api_url,
                headers=settings.openrouter_headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        logger.info(f"Successfully got response from {model}")
                        return content
                elif response.status == 429:
                    logger.warning("Rate limit exceeded for OpenRouter")
                    error_text = await response.text()
                    logger.warning(f"Rate limit details: {error_text}")
                else:
                    logger.warning(f"OpenRouter API error {response.status}")
                    error_text = await response.text()
                    logger.warning(f"Error details: {error_text}")
                    
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}")
            
        return None
    
    async def _try_multiple_models(self, messages: List[Dict], max_tokens: int = 150) -> str:
        """
        Try multiple OpenRouter models as fallback
        """
        for model in settings.FALLBACK_MODELS:
            try:
                result = await self._call_openrouter_api(messages, model, max_tokens)
                if result:
                    logger.info(f"Successfully used fallback model: {model}")
                    return result
            except Exception as e:
                logger.warning(f"Model {model} failed: {str(e)}")
                continue
                
        return None

    async def generate_search_queries(self, topic: str) -> List[str]:
        """Generate enhanced search queries using OpenRouter free models"""
        try:
            # Validate OpenRouter configuration
            if not settings.OPENROUTER_API_KEY:
                logger.warning("OpenRouter API key not found, using fallback method")
                return self._generate_fallback_queries(topic)
            
            # Create messages for OpenAI-compatible format
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates specific search queries for learning resources. Focus on creating diverse, actionable search queries that will find different types of learning materials."
                },
                {
                    "role": "user", 
                    "content": f"""Generate 5 specific search queries for learning about "{topic}". 
Create queries that would find different types of resources:
1. Beginner tutorials
2. Official documentation  
3. Video courses
4. Practical examples/projects
5. Advanced guides

Format your response as a simple numbered list:
1. [query 1]
2. [query 2]
3. [query 3]
4. [query 4]
5. [query 5]

Topic: {topic}"""
                }
            ]
            
            # Try to get response from OpenRouter
            response = await self._try_multiple_models(messages, max_tokens=200)
            
            if response:
                queries = self._extract_queries_from_text(response, topic)
                if queries:
                    logger.info(f"Generated {len(queries)} queries using OpenRouter")
                    return queries
                    
        except Exception as e:
            logger.error(f"Error in generate_search_queries: {str(e)}")
        
        # Fallback to manual query generation
        return self._generate_fallback_queries(topic)
    
    def _extract_queries_from_text(self, text: str, topic: str) -> List[str]:
        """Extract queries from generated text"""
        queries = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove numbering and clean up
            line = re.sub(r'^\d+\.?\s*', '', line)
            line = line.strip('"\'')
            
            if line and len(line) > 5 and len(line) < 100:
                # Ensure the query contains the topic or is relevant
                if topic.lower() in line.lower() or any(word in line.lower() for word in ['tutorial', 'guide', 'course', 'learn']):
                    queries.append(line)
        
        # If we didn't get good queries, try a different extraction method
        if not queries:
            # Look for lines that might be queries
            for line in lines:
                line = line.strip()
                if line and len(line) > 10 and ('?' in line or 'how' in line.lower() or topic.lower() in line.lower()):
                    queries.append(line)
        
        return list(set(queries))[:5]  # Remove duplicates and limit to 5
    
    def _generate_fallback_queries(self, topic: str) -> List[str]:
        """Generate fallback search queries when AI fails"""
        topic_lower = topic.lower()
        enhanced_queries = []
        
        # Add related keywords based on topic
        for key, keywords in self.tech_keywords.items():
            if key in topic_lower or any(keyword in topic_lower for keyword in keywords):
                for keyword in keywords[:2]:  # Limit to 2 keywords
                    enhanced_queries.append(f"{topic} {keyword} tutorial")
        
        # Base queries that work for any topic
        base_queries = [
            f"{topic} tutorial for beginners",
            f"{topic} complete guide",
            f"learn {topic} step by step",
            f"{topic} documentation official",
            f"{topic} video course free",
            f"{topic} examples practical",
            f"best {topic} resources",
            f"{topic} cheat sheet"
        ]
        
        # Combine and deduplicate
        all_queries = enhanced_queries + base_queries
        unique_queries = list(dict.fromkeys(all_queries))  # Preserve order while removing duplicates
        
        return unique_queries[:5]
    
    async def rank_resources(self, resources: List[Resource], topic: str) -> List[Resource]:
        """Rank resources based on relevance to the topic using OpenRouter"""
        if not resources:
            return []
        
        try:
            # Use AI to help with ranking if available
            if settings.OPENROUTER_API_KEY:
                ranked_resources = await self._ai_rank_resources(resources, topic)
                if ranked_resources:
                    return ranked_resources
                    
        except Exception as e:
            logger.warning(f"AI ranking failed, using fallback: {str(e)}")
        
        # Fallback to simple ranking
        scored_resources = []
        for resource in resources:
            score = self._calculate_relevance_score(resource, topic)
            scored_resources.append((resource, score))
        
        # Sort by score (descending)
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        return [resource for resource, score in scored_resources]
    
    async def _ai_rank_resources(self, resources: List[Resource], topic: str) -> List[Resource]:
        """Use AI to rank resources"""
        try:
            # Create a summary of resources for AI analysis
            resource_summaries = []
            for i, resource in enumerate(resources[:10]):  # Limit to avoid token limits
                summary = f"{i+1}. {resource.title} - {resource.description[:100]}... (Platform: {resource.platform})"
                resource_summaries.append(summary)
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are helping rank learning resources for the topic '{topic}'. Rank them by relevance and quality for someone learning this topic."
                },
                {
                    "role": "user",
                    "content": f"""Here are learning resources for '{topic}'. Please rank them from most relevant/useful to least relevant for learning this topic.

Resources:
{chr(10).join(resource_summaries)}

Please respond with just the numbers in order of preference (most relevant first), separated by commas.
Example: 3,1,5,2,4"""
                }
            ]
            
            response = await self._try_multiple_models(messages, max_tokens=100)
            
            if response:
                # Parse the ranking
                ranking_str = response.strip()
                try:
                    rankings = [int(x.strip()) - 1 for x in ranking_str.split(',') if x.strip().isdigit()]
                    
                    # Reorder resources based on AI ranking
                    ranked_resources = []
                    used_indices = set()
                    
                    for rank in rankings:
                        if 0 <= rank < len(resources) and rank not in used_indices:
                            ranked_resources.append(resources[rank])
                            used_indices.add(rank)
                    
                    # Add any remaining resources
                    for i, resource in enumerate(resources):
                        if i not in used_indices:
                            ranked_resources.append(resource)
                    
                    return ranked_resources
                    
                except ValueError:
                    logger.warning("Could not parse AI ranking response")
                    
        except Exception as e:
            logger.warning(f"AI ranking failed: {str(e)}")
            
        return None
    
    def _calculate_relevance_score(self, resource: Resource, topic: str) -> float:
        """Calculate relevance score based on keyword matching"""
        score = 0.0
        topic_lower = topic.lower()
        
        # Title relevance (highest weight)
        if topic_lower in resource.title.lower():
            score += 3.0
        
        # Description relevance
        if topic_lower in resource.description.lower():
            score += 2.0
        
        # Keyword matching from tech_keywords
        for key, keywords in self.tech_keywords.items():
            if key in topic_lower:
                for keyword in keywords:
                    if keyword in resource.title.lower() or keyword in resource.description.lower():
                        score += 0.5
        
        # Platform preferences (you can adjust these)
        platform_scores = {
            'youtube': 0.8,
            'coursera': 1.0,
            'udemy': 0.9,
            'github': 1.2,
            'stackoverflow': 0.7,
            'medium': 0.6,
            'documentation': 1.5
        }
        
        platform_lower = resource.platform.lower()
        for platform, platform_score in platform_scores.items():
            if platform in platform_lower:
                score += platform_score
                break
        
        # Free resources get a slight boost
        if 'free' in resource.price.lower() or resource.price == '':
            score += 0.3
        
        return score

    async def summarize_content(self, content: str, max_length: int = 150) -> str:
        """Summarize content using OpenRouter"""
        try:
            if not settings.OPENROUTER_API_KEY or len(content) < 100:
                # Use simple truncation for short content or if no API key
                return content[:max_length] + "..." if len(content) > max_length else content
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise, informative summaries."
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following content in {max_length} characters or less:\n\n{content[:1000]}"  # Limit input to avoid token issues
                }
            ]
            
            response = await self._try_multiple_models(messages, max_tokens=max_length//3)  # Rough token estimate
            
            if response:
                return response.strip()
                
        except Exception as e:
            logger.warning(f"Content summarization failed: {str(e)}")
        
        # Fallback to simple truncation
        return content[:max_length] + "..." if len(content) > max_length else content

    async def classify_resource_type(self, resource: Resource) -> str:
        """Classify the type of resource"""
        try:
            if settings.OPENROUTER_API_KEY:
                messages = [
                    {
                        "role": "system",
                        "content": "Classify learning resources into one of these categories: tutorial, documentation, course, video, article, tool, or other."
                    },
                    {
                        "role": "user",
                        "content": f"Classify this resource:\nTitle: {resource.title}\nDescription: {resource.description[:200]}\nPlatform: {resource.platform}\n\nRespond with just one word: tutorial, documentation, course, video, article, tool, or other."
                    }
                ]
                
                response = await self._try_multiple_models(messages, max_tokens=20)
                
                if response:
                    classification = response.strip().lower()
                    valid_types = ['tutorial', 'documentation', 'course', 'video', 'article', 'tool', 'other']
                    if classification in valid_types:
                        return classification
                        
        except Exception as e:
            logger.warning(f"Resource classification failed: {str(e)}")
        
        # Fallback classification based on keywords
        title_lower = resource.title.lower()
        description_lower = resource.description.lower()
        platform_lower = resource.platform.lower()
        
        if 'youtube' in platform_lower or 'video' in title_lower:
            return 'video'
        elif 'course' in title_lower or 'coursera' in platform_lower or 'udemy' in platform_lower:
            return 'course'
        elif 'tutorial' in title_lower or 'how to' in title_lower:
            return 'tutorial'
        elif 'docs' in platform_lower or 'documentation' in title_lower:
            return 'documentation'
        elif 'github' in platform_lower or 'tool' in title_lower:
            return 'tool'
        elif 'article' in title_lower or 'blog' in platform_lower:
            return 'article'
        else:
            return 'other'
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None 