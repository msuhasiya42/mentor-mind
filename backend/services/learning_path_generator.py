import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import re
import time

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
        from .result_saver import ResultSaver
        
        logger.info("🔧 INITIALIZING LEARNING PATH GENERATOR")
        
        # Initialize Expert AI Tutor and Result Saver
        self.expert_ai_tutor = ExpertAITutor()
        self.result_saver = ResultSaver()
        
        logger.info("✅ Learning Path Generator initialized")
        logger.info("   - Expert AI Tutor: Ready")
        logger.info("   - Result Saver: Ready")
    
    async def generate_learning_path(self, topic: str) -> LearningPath:
        """Generate a comprehensive learning path for the given topic"""
        logger.info("🎯 STARTING LEARNING PATH GENERATION")
        logger.info(f"   Topic: '{topic}'")
        
        start_time = time.time()
        
        # Clean and validate topic
        clean_topic = self._clean_topic(topic)
        logger.info(f"   Cleaned topic: '{clean_topic}'")
        
        # Get curated resources from expert AI tutor
        logger.info("🤖 Requesting AI curated resources")
        resources = await self.expert_ai_tutor.get_curated_resources(clean_topic)
        
        # Create learning path
        learning_path = self._create_learning_path(clean_topic, resources)
        
        # Auto-save if from AI source
        source = self.expert_ai_tutor.get_last_response_source()
        
        if self.result_saver.save_ai_generated_result(clean_topic, learning_path, source):
            logger.info("💾 Auto-saved AI result")
        
        processing_time = time.time() - start_time
        total_resources = sum(len(getattr(learning_path, category)) for category in ['docs', 'blogs', 'youtube', 'free_courses'])
        
        logger.info("✅ LEARNING PATH GENERATION COMPLETED")
        logger.info(f"   Resources: {total_resources} | Time: {processing_time:.2f}s | Source: {source.split('(')[0].strip()}")
        
        return learning_path
    
    def _create_learning_path(self, topic: str, resources: Dict[str, List[Resource]]) -> LearningPath:
        """Create learning path from resources, limiting to top 5 per category"""
        return LearningPath(
            docs=resources.get('docs', [])[:5],
            blogs=resources.get('blogs', [])[:5],
            youtube=resources.get('youtube', [])[:5],
            free_courses=resources.get('free_courses', [])[:5]
        )
    
    def _determine_result_source(self) -> str:
        """
        Determine the source of the current result based on expert tutor state
        
        Returns:
            str: Source description for logging and saving decisions
        """
        try:
            # Get the actual source from the expert tutor
            if hasattr(self.expert_ai_tutor, 'get_last_response_source'):
                actual_source = self.expert_ai_tutor.get_last_response_source()
                if actual_source and actual_source != "No response yet":
                    logger.debug(f"   Using expert tutor's tracked source: {actual_source}")
                    return actual_source
            
            # Fallback to inference method if direct tracking is not available
            logger.debug("   Expert tutor source tracking not available, using inference")
            
            # Check expert tutor's consecutive failures and last operation
            consecutive_failures = getattr(self.expert_ai_tutor, 'consecutive_failures', 0)
            max_failures = getattr(self.expert_ai_tutor, 'max_consecutive_failures', 3)
            
            # If too many consecutive failures, it would have used manual curation
            if consecutive_failures >= max_failures:
                return "📋 MANUAL CURATION (Too many AI failures)"
            
            # If we have an OpenRouter API key and low failures, likely AI-generated
            from config import settings
            if settings.OPENROUTER_API_KEY and consecutive_failures == 0:
                return "🤖 AI TUTOR (DeepSeek via OpenRouter)"
            elif settings.OPENROUTER_API_KEY and consecutive_failures > 0:
                return "📋 MANUAL CURATION (AI partially failing)"
            else:
                return "📋 MANUAL CURATION (No API key)"
                
        except Exception as e:
            logger.warning(f"⚠️ Could not determine exact source: {str(e)}")
            return "🔄 UNKNOWN SOURCE"
    
    def get_last_generation_source(self) -> str:
        """Get the source of the last generation"""
        return self.expert_ai_tutor.get_last_response_source() or "No generation yet"
    
    def _clean_topic(self, topic: str) -> str:
        """Clean and normalize the topic"""
        logger.debug(f"🧹 Cleaning topic: '{topic}'")
        
        # Remove special characters, extra spaces
        cleaned = re.sub(r'[^\w\s-]', '', topic).strip()
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        logger.debug(f"   Cleaned result: '{cleaned}'")
        return cleaned
    
    async def _generate_fallback_path(self, topic: str) -> LearningPath:
        """Generate a basic fallback learning path when main generation fails"""
        logger.warning("🆘 GENERATING FALLBACK LEARNING PATH")
        logger.warning(f"   Topic: '{topic}'")
        logger.warning("   Reason: Main AI generation failed")
        
        fallback_start_time = time.time()
        
        try:
            # Import fallback provider
            from .fallback_data import FallbackDataProvider
            logger.info("📦 Loading fallback data provider")
            
            fallback_provider = FallbackDataProvider()
            
            # Get basic fallback resources
            logger.info("🔍 Retrieving fallback resources")
            docs = fallback_provider.get_documentation_sources().get('general', [])[:3]
            blogs = fallback_provider.get_fallback_blogs(topic)[:3]
            youtube = fallback_provider.get_fallback_youtube(topic)[:3]
            free_courses = fallback_provider.get_fallback_courses(topic, "free")[:3]
            
            fallback_path = LearningPath(
                docs=docs,
                blogs=blogs, 
                youtube=youtube,
                free_courses=free_courses
            )
            
            fallback_time = time.time() - fallback_start_time
            total_fallback_resources = (
                len(docs) + len(blogs) + len(youtube) + len(free_courses)
            )
            
            logger.info("✅ FALLBACK PATH GENERATION COMPLETED")
            logger.info(f"   Fallback Resources:")
            logger.info(f"     - Docs: {len(docs)}")
            logger.info(f"     - Blogs: {len(blogs)}")
            logger.info(f"     - YouTube: {len(youtube)}")
            logger.info(f"     - Free Courses: {len(free_courses)}")
            logger.info(f"   Total Fallback Resources: {total_fallback_resources}")
            logger.info(f"   Fallback Generation Time: {fallback_time:.3f} seconds")
            
            return fallback_path
            
        except Exception as e:
            logger.error("💥 FALLBACK GENERATION ALSO FAILED")
            logger.error(f"   Topic: '{topic}'")
            logger.error(f"   Fallback Error: {str(e)}")
            logger.error("   Returning empty learning path as last resort")
            
            # Return empty path as last resort
            empty_path = LearningPath(
                docs=[],
                blogs=[],
                youtube=[],
                free_courses=[]
            )
            
            logger.warning("⚠️ EMPTY LEARNING PATH RETURNED")
            logger.warning("   This indicates a serious system failure")
            logger.warning("   All resource generation methods have failed")
            
            return empty_path
    
    async def close(self):
        """Clean up resources"""
        logger.info("🧹 CLEANING UP LEARNING PATH GENERATOR")
        
        try:
            # Close expert tutor
            if hasattr(self.expert_ai_tutor, 'close'):
                logger.info("   Closing Expert AI Tutor...")
                await self.expert_ai_tutor.close()
                logger.info("   ✅ Expert AI Tutor closed")
            
            # Log final save statistics
            if hasattr(self.result_saver, 'get_save_statistics'):
                stats = self.result_saver.get_save_statistics()
                logger.info(f"   📊 Final save statistics: {stats.get('total_files', 0)} files saved")
                
            logger.info("✅ Learning Path Generator cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up Learning Path Generator: {str(e)}")
            logger.error("   Some resources may not have been properly cleaned up") 