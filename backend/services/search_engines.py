"""
Search engine implementations for various web search services
"""
import asyncio
import aiohttp
import logging
import random
from typing import List, Dict
from urllib.parse import quote
from requests_html import AsyncHTMLSession
from fake_useragent import UserAgent
from .fallback_data import FallbackDataProvider

logger = logging.getLogger(__name__)


class SearchEngineManager:
    """Manages different search engines and provides unified search interface"""
    
    def __init__(self):
        self.fallback_provider = FallbackDataProvider()
    
    async def search(self, query: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Search using multiple engines with fallback"""
        try:
            # Try reliable search engines in order of preference
            search_methods = [
                self._search_api_sources,
                self._search_startpage,
            ]
            
            for search_method in search_methods:
                try:
                    results = await search_method(query, session)
                    if results:
                        logger.info(f"Search successful with {search_method.__name__} for: {query}")
                        return results
                except Exception as e:
                    logger.warning(f"Search method {search_method.__name__} failed: {str(e)}")
                    continue
            
            # If all search engines fail, return curated results
            logger.info(f"All search engines failed, using curated results for: {query}")
            return self.fallback_provider.get_curated_search_results(query)
            
        except Exception as e:
            logger.error(f"Error in search manager: {str(e)}")
            return self.fallback_provider.get_curated_search_results(query)
    
    async def _search_api_sources(self, query: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Search using API-based sources (most reliable)"""
        try:
            # Try Stack Overflow API for programming queries
            if any(keyword in query.lower() for keyword in ['programming', 'scala', 'python', 'java', 'react', 'javascript']):
                stackoverflow_results = await self._search_stackoverflow_api(query)
                if stackoverflow_results:
                    return stackoverflow_results
            
            # Try GitHub API for code-related queries
            github_results = await self._search_github_api(query)
            if github_results:
                return github_results
            
            return []
                    
        except Exception as e:
            logger.error(f"Error in API search: {str(e)}")
            return []
    
    async def _search_stackoverflow_api(self, query: str) -> List[Dict]:
        """Search Stack Overflow using their API"""
        try:
            import requests
            
            url = "https://api.stackexchange.com/2.3/search"
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': query,
                'site': 'stackoverflow',
                'pagesize': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'description': f"Stack Overflow - Score: {item.get('score', 0)}, Answers: {item.get('answer_count', 0)}"
                    })
                
                if results:
                    logger.info(f"Stack Overflow API search successful with {len(results)} results")
                    return results
            
            return []
                    
        except Exception as e:
            logger.error(f"Error in Stack Overflow API search: {str(e)}")
            return []
    
    async def _search_github_api(self, query: str) -> List[Dict]:
        """Search GitHub repositories using their API"""
        try:
            import requests
            
            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            }
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Mozilla/5.0 (compatible; MentorMind/1.0)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    results.append({
                        'title': item.get('full_name', ''),
                        'url': item.get('html_url', ''),
                        'description': f"GitHub Repository - Stars: {item.get('stargazers_count', 0)} - {item.get('description', '')[:100]}"
                    })
                
                if results:
                    logger.info(f"GitHub API search successful with {len(results)} results")
                    return results
            
            return []
                    
        except Exception as e:
            logger.error(f"Error in GitHub API search: {str(e)}")
            return []
    
    async def _search_startpage(self, query: str, session: aiohttp.ClientSession = None) -> List[Dict]:
        """Search using Startpage (Google results without tracking)"""
        try:
            ua = UserAgent()
            session = AsyncHTMLSession()
            
            # Random delay to appear more human-like
            await asyncio.sleep(random.uniform(1, 2))
            
            url = "https://www.startpage.com/sp/search"
            params = {
                'query': query,
                'language': 'english',
                'cat': 'web'
            }
            
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            r = await session.get(url, params=params, headers=headers)
            
            results = []
            
            # Parse Startpage results
            result_selectors = [
                '.w-gl__result',
                '.result',
                '[data-testid="result"]'
            ]
            
            for selector in result_selectors:
                elements = r.html.find(selector)
                if elements:
                    break
            
            for element in elements[:5]:
                try:
                    # Find title and URL
                    title_elem = element.find('h3 a', first=True)
                    if not title_elem:
                        title_elem = element.find('a[data-testid="result-title-link"]', first=True)
                    if not title_elem:
                        title_elem = element.find('a', first=True)
                    
                    if title_elem:
                        title = title_elem.text.strip()
                        url = title_elem.attrs.get('href', '')
                        
                        # Find description
                        desc_elem = element.find('.w-gl__description', first=True)
                        if not desc_elem:
                            desc_elem = element.find('[data-testid="result-description"]', first=True)
                        if not desc_elem:
                            desc_elem = element.find('p', first=True)
                        
                        description = desc_elem.text.strip() if desc_elem else ''
                        
                        if title and url:
                            results.append({
                                'title': title,
                                'url': url,
                                'description': description
                            })
                except Exception as e:
                    logger.debug(f"Error parsing Startpage result: {str(e)}")
                    continue
            
            await session.close()
            return results
                    
        except Exception as e:
            logger.error(f"Error in Startpage search: {str(e)}")
            return [] 