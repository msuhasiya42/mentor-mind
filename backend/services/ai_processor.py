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

# For now, we'll create a simple AI processor without heavy dependencies
# In production, you would use transformers and sentence-transformers
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
        self.api_url = "https://api-inference.huggingface.co/models/"
        self.session = None
        
        # Initialize without heavy ML models for now
        # In production, you would load sentence transformers here
        logger.info("AIProcessor initialized with Hugging Face integration")
        
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
    
    async def generate_search_queries(self, topic: str) -> List[str]:
        """Generate enhanced search queries using Hugging Face API"""
        try:
            # Validate Hugging Face token
            if not settings.HUGGINGFACE_API_TOKEN:
                logger.warning("Hugging Face token not found, using fallback method")
                return self._generate_fallback_queries(topic)
            
            session = await self._get_session()
            
            # Create a prompt for generating search queries
            prompt = f"""Generate 5 specific search queries for learning about "{topic}". 
Focus on different learning resources like:
1. Beginner tutorials
2. Official documentation  
3. Video courses
4. Practical examples
5. Advanced guides

Topic: {topic}
Search queries:
1."""
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9,
                    "return_full_text": False
                }
            }
            
            try:
                async with session.post(
                    f"{self.api_url}{settings.TEXT_GENERATION_MODEL}",
                    headers=settings.huggingface_headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                            queries = self._extract_queries_from_text(generated_text, topic)
                            if queries:
                                logger.info(f"Generated {len(queries)} queries using Hugging Face API")
                                return queries
                    else:
                        logger.warning(f"Hugging Face API error: {response.status}")
                        error_text = await response.text()
                        logger.warning(f"Error details: {error_text}")
                        
            except asyncio.TimeoutError:
                logger.warning("Hugging Face API timeout, using fallback")
            except Exception as api_error:
                logger.warning(f"Hugging Face API error: {str(api_error)}")
                
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
                    enhanced_queries.append(f"learn {topic} {keyword}")
        
        # Add general enhanced queries
        base_queries = [
            f"{topic} tutorial",
            f"{topic} documentation", 
            f"{topic} course",
            f"learn {topic}",
            f"{topic} examples",
            f"best {topic} resources",
            f"{topic} beginner guide",
            f"advanced {topic} tutorial",
            f"{topic} best practices"
        ]
        
        enhanced_queries.extend(base_queries)
        
        # Remove duplicates and return top 5
        return list(set(enhanced_queries))[:5]
    
    async def rank_resources(self, resources: List[Resource], topic: str) -> List[Resource]:
        """Rank resources based on relevance to the topic"""
        try:
            if not resources:
                return []
            
            # Simple ranking based on keyword matching and platform priority
            scored_resources = []
            
            for resource in resources:
                score = self._calculate_relevance_score(resource, topic)
                scored_resources.append((score, resource))
            
            # Sort by score (descending)
            scored_resources.sort(key=lambda x: x[0], reverse=True)
            
            # Return sorted resources
            return [resource for score, resource in scored_resources]
            
        except Exception as e:
            logger.error(f"Error ranking resources: {str(e)}")
            return resources  # Return original list if ranking fails
    
    def _calculate_relevance_score(self, resource: Resource, topic: str) -> float:
        """Calculate relevance score for a resource"""
        score = 0.0
        topic_lower = topic.lower()
        
        # Title relevance (highest weight)
        title_lower = resource.title.lower()
        if topic_lower in title_lower:
            score += 3.0
        
        # Count topic words in title
        topic_words = topic_lower.split()
        for word in topic_words:
            if len(word) > 2 and word in title_lower:
                score += 1.0
        
        # Description relevance
        if resource.description:
            desc_lower = resource.description.lower()
            if topic_lower in desc_lower:
                score += 1.5
            
            for word in topic_words:
                if len(word) > 2 and word in desc_lower:
                    score += 0.5
        
        # Platform priority (official sources get higher scores)
        platform_scores = {
            'documentation': 2.0,
            'official': 2.0,
            'github': 1.5,
            'youtube': 1.2,
            'coursera': 1.3,
            'edx': 1.3,
            'udemy': 1.1,
            'blog': 1.0
        }
        
        platform_lower = resource.platform.lower()
        for platform, platform_score in platform_scores.items():
            if platform in platform_lower:
                score += platform_score
                break
        
        # URL quality indicators
        url_lower = resource.url.lower()
        quality_indicators = [
            ('docs.', 1.5),
            ('official', 1.5),
            ('tutorial', 1.0),
            ('guide', 1.0),
            ('learn', 1.0)
        ]
        
        for indicator, indicator_score in quality_indicators:
            if indicator in url_lower:
                score += indicator_score
        
        return score
    
    async def summarize_content(self, content: str, max_length: int = 150) -> str:
        """Summarize content (simplified version)"""
        try:
            if len(content) <= max_length:
                return content
            
            # Simple extractive summarization - take first sentences up to max_length
            sentences = content.split('. ')
            summary = ""
            
            for sentence in sentences:
                if len(summary + sentence) <= max_length:
                    summary += sentence + ". "
                else:
                    break
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing content: {str(e)}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    async def classify_resource_type(self, resource: Resource) -> str:
        """Classify the type of resource"""
        try:
            title_lower = resource.title.lower()
            url_lower = resource.url.lower()
            
            # Classification based on keywords
            if any(keyword in title_lower or keyword in url_lower for keyword in ['course', 'class', 'training']):
                return 'course'
            elif any(keyword in title_lower or keyword in url_lower for keyword in ['tutorial', 'guide', 'how-to']):
                return 'tutorial'
            elif any(keyword in title_lower or keyword in url_lower for keyword in ['docs', 'documentation', 'reference']):
                return 'documentation'
            elif any(keyword in title_lower or keyword in url_lower for keyword in ['blog', 'article', 'post']):
                return 'article'
            elif 'youtube.com' in url_lower or 'video' in title_lower:
                return 'video'
            else:
                return 'general'
                
        except Exception as e:
            logger.error(f"Error classifying resource: {str(e)}")
            return 'general'
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None 