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
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Starting learning path generation for: {topic}")
            
            # Validate and clean the topic
            cleaned_topic = self._clean_topic(topic)
            
            # Use AI to enhance topic understanding and generate search queries
            query_start = time.time()
            enhanced_queries = await self.ai_processor.generate_search_queries(cleaned_topic)
            query_time = time.time() - query_start
            logger.info(f"Query generation took {query_time:.2f} seconds")
            
            # Get comprehensive resources using the LLM search engine
            aggregation_start = time.time()
            all_resources = await self.content_aggregator.get_all_resources(cleaned_topic, enhanced_queries)
            aggregation_time = time.time() - aggregation_start
            logger.info(f"LLM-based resource aggregation took {aggregation_time:.2f} seconds")
            
            # Extract categorized resources
            docs = all_resources.get('docs', [])
            blogs = all_resources.get('blogs', [])
            youtube = all_resources.get('youtube', [])
            free_courses = all_resources.get('free_courses', [])
            paid_courses = all_resources.get('paid_courses', [])
            
            # Use AI to rank and filter resources in parallel (if we have resources)
            if any([docs, blogs, youtube, free_courses, paid_courses]):
                ranking_start = time.time()
                ranking_tasks = [
                    self.ai_processor.rank_resources(docs, cleaned_topic),
                    self.ai_processor.rank_resources(blogs, cleaned_topic),
                    self.ai_processor.rank_resources(youtube, cleaned_topic),
                    self.ai_processor.rank_resources(free_courses, cleaned_topic),
                    self.ai_processor.rank_resources(paid_courses, cleaned_topic)
                ]
                
                ranked_results = await asyncio.gather(*ranking_tasks)
                docs, blogs, youtube, free_courses, paid_courses = ranked_results
                ranking_time = time.time() - ranking_start
                logger.info(f"Parallel resource ranking took {ranking_time:.2f} seconds")
            
            learning_path = LearningPath(
                docs=docs[:5],  # Limit to top 5
                blogs=blogs[:5],
                youtube=youtube[:5],
                free_courses=free_courses[:5],
                paid_courses=paid_courses[:5]
            )
            
            total_time = time.time() - start_time
            total_resources = len(docs) + len(blogs) + len(youtube) + len(free_courses) + len(paid_courses)
            logger.info(f"Successfully generated learning path for: {topic} with {total_resources} resources in {total_time:.2f} seconds")
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
            # Simple fallback - get basic resources in parallel without AI processing
            fallback_tasks = [
                self.content_aggregator.get_documentation(topic, []),
                self.content_aggregator.get_blogs(topic, []),
                self.content_aggregator.get_youtube_videos(topic, [])
            ]
            
            results = await asyncio.gather(*fallback_tasks, return_exceptions=True)
            
            # Handle results safely
            docs = results[0] if isinstance(results[0], list) else []
            blogs = results[1] if isinstance(results[1], list) else []
            youtube = results[2] if isinstance(results[2], list) else []
            
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