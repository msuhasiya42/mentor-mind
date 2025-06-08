"""
Content aggregator service for gathering learning resources from various sources
"""
import asyncio
import aiohttp
import logging
from typing import List
from .models import Resource
from .search_engines import SearchEngineManager
from .fallback_data import FallbackDataProvider

logger = logging.getLogger(__name__)


class ContentAggregator:
    """Main content aggregation service that coordinates resource gathering"""
    
    def __init__(self):
        self.session = None
        self.search_manager = SearchEngineManager()
        self.fallback_provider = FallbackDataProvider()
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def get_documentation(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get official documentation and guides"""
        try:
            resources = []
            session = await self._get_session()
            
            # Check predefined documentation sources first
            doc_sources = self.fallback_provider.get_documentation_sources()
            topic_lower = topic.lower()
            
            for key, docs in doc_sources.items():
                if key in topic_lower or topic_lower in key:
                    resources.extend(docs)
                    break
            
            # If no predefined docs, search for official documentation
            if not resources:
                search_queries = [
                    f"{topic} official documentation",
                    f"{topic} docs reference guide"
                ]
                
                resources = await self._execute_search_queries(
                    search_queries[:2], session, "Documentation"
                )
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting documentation: {str(e)}")
            return []
    
    async def get_blogs(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get blog posts and articles"""
        try:
            session = await self._get_session()
            
            search_queries = [
                f"best {topic} tutorial blog",
                f"{topic} guide article",
                f"learn {topic} blog post"
            ]
            
            # Add enhanced queries if available
            if enhanced_queries:
                search_queries.extend(enhanced_queries[:2])
            
            resources = await self._execute_search_queries(
                search_queries[:3], session, "Blog"
            )
            
            # Use fallback if no results
            if not resources:
                resources = self.fallback_provider.get_fallback_blogs(topic)
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting blogs: {str(e)}")
            return self.fallback_provider.get_fallback_blogs(topic)
    
    async def get_youtube_videos(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get YouTube tutorial videos"""
        try:
            session = await self._get_session()
            
            search_queries = [
                f"{topic} tutorial youtube",
                f"learn {topic} video site:youtube.com"
            ]
            
            resources = await self._execute_search_queries(
                search_queries, session, "YouTube", filter_youtube=True
            )
            
            # Use fallback if no results
            if not resources:
                resources = self.fallback_provider.get_fallback_youtube(topic)
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting YouTube videos: {str(e)}")
            return self.fallback_provider.get_fallback_youtube(topic)
    
    async def get_free_courses(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get free online courses"""
        try:
            session = await self._get_session()
            
            search_queries = [
                f"free {topic} course coursera edx",
                f"{topic} free course freeCodeCamp",
                f"free {topic} tutorial course"
            ]
            
            resources = await self._execute_search_queries(
                search_queries[:3], session, "Free Course"
            )
            
            # Use fallback if no results
            if not resources:
                resources = self.fallback_provider.get_fallback_courses(topic, "free")
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting free courses: {str(e)}")
            return self.fallback_provider.get_fallback_courses(topic, "free")
    
    async def get_paid_courses(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get paid courses with pricing"""
        try:
            session = await self._get_session()
            
            search_queries = [
                f"{topic} course udemy pluralsight",
                f"{topic} paid course linkedin learning"
            ]
            
            resources = await self._execute_search_queries(
                search_queries[:2], session, "Paid Course", price="$10-50"
            )
            
            # Use fallback if no results
            if not resources:
                resources = self.fallback_provider.get_fallback_courses(topic, "paid")
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting paid courses: {str(e)}")
            return self.fallback_provider.get_fallback_courses(topic, "paid")
    
    async def _execute_search_queries(
        self, 
        queries: List[str], 
        session: aiohttp.ClientSession, 
        platform: str,
        price: str = "",
        filter_youtube: bool = False
    ) -> List[Resource]:
        """Execute multiple search queries in parallel and return resources"""
        try:
            # Execute search queries in parallel
            search_tasks = [
                self.search_manager.search(query, session) 
                for query in queries
            ]
            
            search_results_list = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            resources = []
            for search_results in search_results_list:
                if isinstance(search_results, list):  # Valid results
                    for result in search_results[:2]:  # Limit results per query
                        # Filter YouTube results if requested
                        if filter_youtube and 'youtube.com' not in result.get('url', ''):
                            continue
                        
                        resources.append(Resource(
                            title=result.get('title', ''),
                            url=result.get('url', ''),
                            description=result.get('description', ''),
                            platform=platform,
                            price=price
                        ))
            
            return resources
            
        except Exception as e:
            logger.error(f"Error executing search queries: {str(e)}")
            return [] 