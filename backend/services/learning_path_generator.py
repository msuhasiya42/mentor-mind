import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import re

from .content_aggregator import ContentAggregator
from .ai_processor import AIProcessor

logger = logging.getLogger(__name__)

@dataclass
class Resource:
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""

@dataclass
class LearningPath:
    blogs: List[Resource]
    docs: List[Resource] 
    youtube: List[Resource]
    free_courses: List[Resource]
    paid_courses: List[Resource]

class LearningPathGenerator:
    def __init__(self):
        self.content_aggregator = ContentAggregator()
        self.ai_processor = AIProcessor()
        logger.info("LearningPathGenerator initialized")
    
    async def generate_path(self, topic: str) -> LearningPath:
        """Generate a comprehensive learning path for the given topic"""
        try:
            logger.info(f"Starting learning path generation for: {topic}")
            
            # Validate and clean the topic
            cleaned_topic = self._clean_topic(topic)
            
            # Use AI to enhance topic understanding and generate search queries
            enhanced_queries = await self.ai_processor.generate_search_queries(cleaned_topic)
            
            # Aggregate content from multiple sources
            tasks = [
                self.content_aggregator.get_documentation(cleaned_topic, enhanced_queries),
                self.content_aggregator.get_blogs(cleaned_topic, enhanced_queries),
                self.content_aggregator.get_youtube_videos(cleaned_topic, enhanced_queries),
                self.content_aggregator.get_free_courses(cleaned_topic, enhanced_queries),
                self.content_aggregator.get_paid_courses(cleaned_topic, enhanced_queries)
            ]
            
            results = await asyncio.gather(*tasks)
            docs, blogs, youtube, free_courses, paid_courses = results
            
            # Use AI to rank and filter resources
            docs = await self.ai_processor.rank_resources(docs, cleaned_topic)
            blogs = await self.ai_processor.rank_resources(blogs, cleaned_topic)
            youtube = await self.ai_processor.rank_resources(youtube, cleaned_topic)
            free_courses = await self.ai_processor.rank_resources(free_courses, cleaned_topic)
            paid_courses = await self.ai_processor.rank_resources(paid_courses, cleaned_topic)
            
            learning_path = LearningPath(
                docs=docs[:5],  # Limit to top 5
                blogs=blogs[:5],
                youtube=youtube[:5],
                free_courses=free_courses[:5],
                paid_courses=paid_courses[:5]
            )
            
            logger.info(f"Successfully generated learning path for: {topic}")
            return learning_path
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            # Return a basic fallback path
            return await self._generate_fallback_path(topic)
    
    def _clean_topic(self, topic: str) -> str:
        """Clean and normalize the topic"""
        # Remove special characters, extra spaces
        cleaned = re.sub(r'[^\w\s-]', '', topic).strip()
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
    
    async def _generate_fallback_path(self, topic: str) -> LearningPath:
        """Generate a basic fallback learning path when main generation fails"""
        logger.info(f"Generating fallback path for: {topic}")
        
        try:
            # Simple fallback - just get basic resources without AI processing
            docs = await self.content_aggregator.get_documentation(topic, [])
            blogs = await self.content_aggregator.get_blogs(topic, [])
            youtube = await self.content_aggregator.get_youtube_videos(topic, [])
            
            return LearningPath(
                docs=docs[:3],
                blogs=blogs[:3], 
                youtube=youtube[:3],
                free_courses=[],
                paid_courses=[]
            )
        except Exception as e:
            logger.error(f"Even fallback generation failed: {str(e)}")
            # Return empty path as last resort
            return LearningPath(
                docs=[],
                blogs=[],
                youtube=[],
                free_courses=[],
                paid_courses=[]
            )
    
    async def close(self):
        """Clean up resources"""
        try:
            # Close content aggregator
            if hasattr(self.content_aggregator, 'close'):
                await self.content_aggregator.close()
            
            # Close AI processor
            if hasattr(self.ai_processor, 'close'):
                await self.ai_processor.close()
                
            logger.info("LearningPathGenerator resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up LearningPathGenerator: {str(e)}") 