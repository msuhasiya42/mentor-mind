"""
Content aggregator service for gathering learning resources from various sources
"""
import asyncio
import aiohttp
import logging
from typing import List
from .learning_path_generator import Resource
from .search_engines import LLMSearchEngine
from .fallback_data import FallbackDataProvider

logger = logging.getLogger(__name__)


class ContentAggregator:
    """Main content aggregation service that coordinates resource gathering"""
    
    def __init__(self):
        self.session = None
        self.llm_search = LLMSearchEngine()
        self.fallback_provider = FallbackDataProvider()
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close the aiohttp session and LLM search engine"""
        if self.session:
            await self.session.close()
            self.session = None
        if self.llm_search:
            await self.llm_search.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_all_resources(self, topic: str, enhanced_queries: List[str]) -> dict:
        """Get all resources at once using the LLM search engine and categorize them"""
        try:
            logger.info(f"Getting comprehensive resources for topic: {topic}")
            
            # Use the LLM search engine to get comprehensive resources
            session = await self._get_session()
            all_resources = await self.llm_search.search(topic, session)
            
            # Categorize resources by type
            categorized = {
                'docs': [],
                'blogs': [],
                'youtube': [],
                'free_courses': [],
                'paid_courses': []
            }
            
            for resource in all_resources:
                resource_type = resource.get('type', 'tutorial')
                price = resource.get('price', 'Free').lower()
                
                # Convert to our Resource model
                converted_resource = Resource(
                    title=resource.get('title', ''),
                    url=resource.get('url', ''),
                    description=resource.get('description', ''),
                    platform=resource.get('platform', ''),
                    price=resource.get('price', '')
                )
                
                # Categorize based on type and price
                if resource_type == 'documentation':
                    categorized['docs'].append(converted_resource)
                elif resource_type == 'video':
                    categorized['youtube'].append(converted_resource)
                elif resource_type == 'blog':
                    categorized['blogs'].append(converted_resource)
                elif resource_type == 'course':
                    if 'free' in price or price == '':
                        categorized['free_courses'].append(converted_resource)
                    else:
                        categorized['paid_courses'].append(converted_resource)
                elif resource_type == 'repository':
                    categorized['blogs'].append(converted_resource)  # Treat repos as blog-like resources
                else:
                    # Default categorization
                    if 'free' in price or price == '':
                        categorized['free_courses'].append(converted_resource)
                    else:
                        categorized['paid_courses'].append(converted_resource)
            
            logger.info(f"Categorized resources: docs={len(categorized['docs'])}, blogs={len(categorized['blogs'])}, youtube={len(categorized['youtube'])}, free_courses={len(categorized['free_courses'])}, paid_courses={len(categorized['paid_courses'])}")
            
            return categorized
            
        except Exception as e:
            logger.error(f"Error getting comprehensive resources: {str(e)}")
            # Fall back to individual methods if comprehensive search fails
            return await self._get_fallback_categorized_resources(topic, enhanced_queries)
    
    async def get_documentation(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get official documentation and guides"""
        try:
            # Try to get comprehensive resources first
            all_resources = await self.get_all_resources(topic, enhanced_queries)
            docs = all_resources.get('docs', [])
            
            if docs:
                return docs[:5]
            
            # Fallback to traditional search
            return await self._get_documentation_fallback(topic)
            
        except Exception as e:
            logger.error(f"Error getting documentation: {str(e)}")
            return await self._get_documentation_fallback(topic)
    
    async def get_blogs(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get blog posts and articles"""
        try:
            # Try to get comprehensive resources first
            all_resources = await self.get_all_resources(topic, enhanced_queries)
            blogs = all_resources.get('blogs', [])
            
            if blogs:
                return blogs[:5]
            
            # Fallback
            return self.fallback_provider.get_fallback_blogs(topic)
            
        except Exception as e:
            logger.error(f"Error getting blogs: {str(e)}")
            return self.fallback_provider.get_fallback_blogs(topic)
    
    async def get_youtube_videos(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get YouTube tutorial videos"""
        try:
            # Try to get comprehensive resources first
            all_resources = await self.get_all_resources(topic, enhanced_queries)
            youtube = all_resources.get('youtube', [])
            
            if youtube:
                return youtube[:5]
            
            # Fallback
            return self.fallback_provider.get_fallback_youtube(topic)
            
        except Exception as e:
            logger.error(f"Error getting YouTube videos: {str(e)}")
            return self.fallback_provider.get_fallback_youtube(topic)
    
    async def get_free_courses(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get free online courses"""
        try:
            # Try to get comprehensive resources first
            all_resources = await self.get_all_resources(topic, enhanced_queries)
            free_courses = all_resources.get('free_courses', [])
            
            if free_courses:
                return free_courses[:5]
            
            # Fallback
            return self.fallback_provider.get_fallback_courses(topic, "free")
            
        except Exception as e:
            logger.error(f"Error getting free courses: {str(e)}")
            return self.fallback_provider.get_fallback_courses(topic, "free")
    
    async def get_paid_courses(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get paid courses with pricing"""
        try:
            # Try to get comprehensive resources first
            all_resources = await self.get_all_resources(topic, enhanced_queries)
            paid_courses = all_resources.get('paid_courses', [])
            
            if paid_courses:
                return paid_courses[:5]
            
            # Fallback
            return self.fallback_provider.get_fallback_courses(topic, "paid")
            
        except Exception as e:
            logger.error(f"Error getting paid courses: {str(e)}")
            return self.fallback_provider.get_fallback_courses(topic, "paid")
    
    async def _get_fallback_categorized_resources(self, topic: str, enhanced_queries: List[str]) -> dict:
        """Get fallback categorized resources when LLM search fails"""
        logger.info(f"Using fallback categorized resources for: {topic}")
        
        return {
            'docs': self.fallback_provider.get_documentation_sources().get('general', [])[:3],
            'blogs': self.fallback_provider.get_fallback_blogs(topic)[:3],
            'youtube': self.fallback_provider.get_fallback_youtube(topic)[:3],
            'free_courses': self.fallback_provider.get_fallback_courses(topic, "free")[:3],
            'paid_courses': self.fallback_provider.get_fallback_courses(topic, "paid")[:3]
        }
    
    async def _get_documentation_fallback(self, topic: str) -> List[Resource]:
        """Fallback method for getting documentation"""
        doc_sources = self.fallback_provider.get_documentation_sources()
        topic_lower = topic.lower()
        
        # Look for topic-specific documentation
        for key, docs in doc_sources.items():
            if key in topic_lower or topic_lower in key:
                return docs[:3]
        
        # Return general documentation if no specific match
        return doc_sources.get('general', [])[:3] 