import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class Resource:
    """Represents a learning resource with metadata"""
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""

    def __post_init__(self):
        """Validate and clean resource data"""
        self.title = self.title.strip() if self.title else ""
        self.url = self.url.strip() if self.url else ""
        self.description = self.description.strip() if self.description else ""
        self.platform = self.platform.strip() if self.platform else ""
        self.price = self.price.strip() if self.price else ""


@dataclass
class LearningPath:
    """Represents a complete learning path with categorized resources"""
    blogs: List[Resource]
    docs: List[Resource] 
    youtube: List[Resource]
    free_courses: List[Resource]
    paid_courses: List[Resource]


@dataclass
class SearchResult:
    """Represents a search result from any search engine"""
    title: str
    url: str
    description: str = ""
    
    def to_resource(self, platform: str = "", price: str = "") -> Resource:
        """Convert search result to a Resource object"""
        return Resource(
            title=self.title,
            url=self.url,
            description=self.description,
            platform=platform,
            price=price
        )

class LearningPathGenerator:
    def __init__(self):
        # Import here to avoid circular imports
        from .expert_ai_tutor import ExpertAITutor
        
        self.expert_tutor = ExpertAITutor()
        logger.info("LearningPathGenerator initialized with Expert AI Tutor")
    
    async def generate_path(self, topic: str) -> LearningPath:
        """Generate a comprehensive learning path using a single AI expert call"""
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Starting expert AI learning path generation for: {topic}")
            
            # Validate and clean the topic
            cleaned_topic = self._clean_topic(topic)
            
            # Get curated resources from expert AI tutor in a single call
            categorized_resources = await self.expert_tutor.get_curated_resources(cleaned_topic)
            
            # Extract categorized resources
            docs = categorized_resources.get('docs', [])
            blogs = categorized_resources.get('blogs', [])
            youtube = categorized_resources.get('youtube', [])
            free_courses = categorized_resources.get('free_courses', [])
            paid_courses = categorized_resources.get('paid_courses', [])
            
            learning_path = LearningPath(
                docs=docs[:5],  # Limit to top 5
                blogs=blogs[:5],
                youtube=youtube[:5],
                free_courses=free_courses[:5],
                paid_courses=paid_courses[:5]
            )
            
            total_time = time.time() - start_time
            total_resources = len(docs) + len(blogs) + len(youtube) + len(free_courses) + len(paid_courses)
            logger.info(f"Successfully generated expert learning path for: {topic} with {total_resources} resources in {total_time:.2f} seconds")
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
            # Import fallback provider
            from .fallback_data import FallbackDataProvider
            fallback_provider = FallbackDataProvider()
            
            # Get basic fallback resources
            docs = fallback_provider.get_documentation_sources().get('general', [])[:3]
            blogs = fallback_provider.get_fallback_blogs(topic)[:3]
            youtube = fallback_provider.get_fallback_youtube(topic)[:3]
            free_courses = fallback_provider.get_fallback_courses(topic, "free")[:3]
            paid_courses = fallback_provider.get_fallback_courses(topic, "paid")[:3]
            
            return LearningPath(
                docs=docs,
                blogs=blogs, 
                youtube=youtube,
                free_courses=free_courses,
                paid_courses=paid_courses
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
            # Close expert tutor
            if hasattr(self.expert_tutor, 'close'):
                await self.expert_tutor.close()
                
            logger.info("LearningPathGenerator resources cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up LearningPathGenerator: {str(e)}") 