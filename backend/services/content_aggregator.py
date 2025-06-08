import asyncio
import aiohttp
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
from fake_useragent import UserAgent
import random
import json

logger = logging.getLogger(__name__)

@dataclass
class Resource:
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""

class ContentAggregator:
    def __init__(self):
        self.session = None
        
    async def _get_session(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
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
            
            # Predefined documentation sources for common topics
            doc_sources = {
                'react': [
                    Resource("React Official Documentation", "https://react.dev/", "The official React documentation", "React"),
                    Resource("React Tutorial", "https://react.dev/learn", "Interactive React tutorial", "React"),
                ],
                'python': [
                    Resource("Python Official Documentation", "https://docs.python.org/3/", "Official Python 3 documentation", "Python"),
                    Resource("Python Tutorial", "https://docs.python.org/3/tutorial/", "Official Python tutorial", "Python"),
                ],
                'javascript': [
                    Resource("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "Comprehensive JavaScript guide", "MDN"),
                    Resource("JavaScript.info", "https://javascript.info/", "Modern JavaScript tutorial", "JavaScript.info"),
                ],
                'fastapi': [
                    Resource("FastAPI Documentation", "https://fastapi.tiangolo.com/", "Official FastAPI documentation", "FastAPI"),
                    Resource("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/", "FastAPI user guide", "FastAPI"),
                ],
                'django': [
                    Resource("Django Documentation", "https://docs.djangoproject.com/", "Official Django documentation", "Django"),
                    Resource("Django Tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "Django getting started tutorial", "Django"),
                ],
                'scala': [
                    Resource("Scala Official Documentation", "https://docs.scala-lang.org/", "Official Scala documentation", "Scala"),
                    Resource("Scala Tour", "https://docs.scala-lang.org/tour/tour-of-scala.html", "Tour of Scala programming language", "Scala"),
                    Resource("Scala Getting Started", "https://docs.scala-lang.org/getting-started/", "Getting started with Scala", "Scala"),
                    Resource("Scala Book", "https://docs.scala-lang.org/scala3/book/introduction.html", "Scala 3 Book - comprehensive guide", "Scala"),
                ]
            }
            
            # Check if we have predefined docs for this topic
            topic_lower = topic.lower()
            for key, docs in doc_sources.items():
                if key in topic_lower or topic_lower in key:
                    resources.extend(docs)
                    break
            
            # If no predefined docs, try to search for official documentation
            if not resources:
                search_queries = [
                    f"{topic} official documentation",
                    f"{topic} docs",
                    f"{topic} reference guide"
                ]
                
                for query in search_queries[:2]:  # Limit to avoid rate limiting
                    search_results = await self._search_duckduckgo(query, session)
                    for result in search_results[:2]:
                        resources.append(Resource(
                            title=result.get('title', ''),
                            url=result.get('url', ''), 
                            description=result.get('description', ''),
                            platform="Documentation"
                        ))
            
            return resources[:5]  # Limit to top 5
            
        except Exception as e:
            logger.error(f"Error getting documentation: {str(e)}")
            return []
    
    async def get_blogs(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get blog posts and articles"""
        try:
            resources = []
            session = await self._get_session()
            
            search_queries = [
                f"best {topic} tutorial blog",
                f"{topic} guide article",
                f"learn {topic} blog post"
            ]
            
            # Add enhanced queries if available
            if enhanced_queries:
                search_queries.extend(enhanced_queries[:2])
            
            for query in search_queries[:3]:  # Limit searches
                search_results = await self._search_duckduckgo(query, session)
                for result in search_results[:2]:
                    resources.append(Resource(
                        title=result.get('title', ''),
                        url=result.get('url', ''),
                        description=result.get('description', ''),
                        platform="Blog"
                    ))
            
            # If no results from search, provide fallback resources for popular topics
            if not resources:
                resources = self._get_fallback_blogs(topic)
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting blogs: {str(e)}")
            return self._get_fallback_blogs(topic)
    
    async def get_youtube_videos(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get YouTube tutorial videos"""
        try:
            resources = []
            session = await self._get_session()
            
            search_queries = [
                f"{topic} tutorial youtube",
                f"learn {topic} video",
                f"{topic} crash course"
            ]
            
            for query in search_queries[:2]:
                search_results = await self._search_duckduckgo(query + " site:youtube.com", session)
                for result in search_results[:3]:
                    if 'youtube.com' in result.get('url', ''):
                        resources.append(Resource(
                            title=result.get('title', ''),
                            url=result.get('url', ''),
                            description=result.get('description', ''),
                            platform="YouTube"
                        ))
            
            # If no results from search, provide fallback resources
            if not resources:
                resources = self._get_fallback_youtube(topic)
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting YouTube videos: {str(e)}")
            return self._get_fallback_youtube(topic)
    
    async def get_free_courses(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get free online courses"""
        try:
            resources = []
            session = await self._get_session()
            
            # Search for free courses on popular platforms
            search_queries = [
                f"free {topic} course coursera",
                f"free {topic} course edx", 
                f"{topic} free course udemy",
                f"free {topic} course freeCodeCamp"
            ]
            
            for query in search_queries[:3]:
                search_results = await self._search_duckduckgo(query, session)
                for result in search_results[:2]:
                    resources.append(Resource(
                        title=result.get('title', ''),
                        url=result.get('url', ''),
                        description=result.get('description', ''),
                        platform="Free Course"
                    ))
            
            # If no results from search, provide fallback resources
            if not resources:
                resources = self._get_fallback_courses(topic, "free")
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting free courses: {str(e)}")
            return self._get_fallback_courses(topic, "free")
    
    async def get_paid_courses(self, topic: str, enhanced_queries: List[str]) -> List[Resource]:
        """Get paid courses with pricing"""
        try:
            resources = []
            session = await self._get_session()
            
            search_queries = [
                f"{topic} course udemy",
                f"{topic} course pluralsight",
                f"{topic} course linkedin learning"
            ]
            
            for query in search_queries[:2]:
                search_results = await self._search_duckduckgo(query, session)
                for result in search_results[:2]:
                    resources.append(Resource(
                        title=result.get('title', ''),
                        url=result.get('url', ''),
                        description=result.get('description', ''),
                        platform="Paid Course",
                        price="$10-50" # Placeholder price range
                    ))
            
            # If no results from search, provide fallback resources
            if not resources:
                resources = self._get_fallback_courses(topic, "paid")
            
            return resources[:5]
            
        except Exception as e:
            logger.error(f"Error getting paid courses: {str(e)}")
            return self._get_fallback_courses(topic, "paid")
    
    async def _search_duckduckgo(self, query: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Search DuckDuckGo for results with fallback search engines"""
        try:
            # Try DuckDuckGo first
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Set a shorter timeout for DuckDuckGo
            timeout = aiohttp.ClientTimeout(total=5)
            try:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        html = await response.text()
                        results = self._parse_duckduckgo_results(html)
                        if results:
                            logger.info(f"DuckDuckGo search successful for: {query}")
                            return results
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                logger.warning(f"DuckDuckGo timeout/error for query '{query}': {str(e)}")
            
            # Fallback to alternative search methods
            logger.info(f"Using fallback search for: {query}")
            fallback_results = await self._search_fallback(query, session)
            return fallback_results
                    
        except Exception as e:
            logger.error(f"Error in search (trying fallback): {str(e)}")
            return await self._search_fallback(query, session)
    
    def _parse_duckduckgo_results(self, html: str) -> List[Dict]:
        """Parse DuckDuckGo search results from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            # Find search result elements
            result_elements = soup.find_all('div', class_='result')
            
            for element in result_elements[:5]:  # Limit to first 5 results
                title_elem = element.find('a', class_='result__a')
                snippet_elem = element.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    description = snippet_elem.get_text().strip() if snippet_elem else ''
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'description': description
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo results: {str(e)}")
            return []
    
    async def _search_fallback(self, query: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Fallback search methods when DuckDuckGo fails"""
        try:
            # Try SearX search first (privacy-focused, bot-friendly)
            searx_results = await self._search_searx(query)
            if searx_results:
                logger.info(f"SearX search successful for: {query}")
                return searx_results
            
            # Try browser-based Bing search with better emulation
            bing_results = await self._search_bing_browser(query)
            if bing_results:
                logger.info(f"Bing browser search successful for: {query}")
                return bing_results
            
            # Try alternative search engines
            startpage_results = await self._search_startpage(query)
            if startpage_results:
                logger.info(f"Startpage search successful for: {query}")
                return startpage_results
            
            # If all search engines fail, return topic-specific curated results
            logger.info(f"All search engines failed, using curated results for: {query}")
            return self._get_curated_search_results(query)
            
        except Exception as e:
            logger.error(f"Error in fallback search: {str(e)}")
            return self._get_curated_search_results(query)
    
    async def _search_searx(self, query: str) -> List[Dict]:
        """Search using SearX metasearch engine (privacy-focused and bot-friendly)"""
        try:
            # Use YouTube search for programming-related queries as a reliable fallback
            if any(keyword in query.lower() for keyword in ['tutorial', 'programming', 'learn', 'course']):
                youtube_results = await self._search_youtube_api(query)
                if youtube_results:
                    return youtube_results
            
            # Simple requests-based approach for SearX
            import requests
            
            # Try reliable SearX instances
            searx_instances = [
                "https://search.bus-hit.me",
                "https://searx.tiekoetter.com"
            ]
            
            for instance in searx_instances[:1]:  # Try just one to avoid delays
                try:
                    url = f"{instance}/search"
                    params = {
                        'q': query,
                        'format': 'json',
                        'engines': 'bing,google',
                        'categories': 'general'
                    }
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                        'Accept': 'application/json'
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        
                        for result in data.get('results', [])[:5]:
                            results.append({
                                'title': result.get('title', ''),
                                'url': result.get('url', ''),
                                'description': result.get('content', '')
                            })
                        
                        if results:
                            logger.info(f"SearX search successful with {len(results)} results from {instance}")
                            return results
                    
                except Exception as e:
                    logger.debug(f"SearX instance {instance} failed: {str(e)}")
                    continue
            
            return []
                    
        except Exception as e:
            logger.error(f"Error in SearX search: {str(e)}")
            return []
    
    async def _search_youtube_api(self, query: str) -> List[Dict]:
        """Search YouTube using the youtube-search-python library"""
        try:
            from youtubesearchpython import VideosSearch
            
            # Search for videos
            videosSearch = VideosSearch(query, limit=5)
            results = videosSearch.result()
            
            search_results = []
            for video in results.get('result', []):
                search_results.append({
                    'title': video.get('title', ''),
                    'url': video.get('link', ''),
                    'description': f"YouTube video - Duration: {video.get('duration', 'N/A')}"
                })
            
            if search_results:
                logger.info(f"YouTube API search successful with {len(search_results)} results")
                return search_results
            
            return []
                    
        except Exception as e:
            logger.error(f"Error in YouTube API search: {str(e)}")
            return []
    
    async def _search_bing_browser(self, query: str) -> List[Dict]:
        """Search using reliable aggregator sites and APIs"""
        try:
            # Use Stack Overflow API for programming queries
            if any(keyword in query.lower() for keyword in ['programming', 'scala', 'python', 'java', 'react', 'javascript']):
                stackoverflow_results = await self._search_stackoverflow_api(query)
                if stackoverflow_results:
                    return stackoverflow_results
            
            # Use GitHub API for code-related queries
            github_results = await self._search_github_api(query)
            if github_results:
                return github_results
            
            return []
                    
        except Exception as e:
            logger.error(f"Error in aggregator search: {str(e)}")
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
    
    async def _search_startpage(self, query: str) -> List[Dict]:
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
    

    
    def _get_curated_search_results(self, query: str) -> List[Dict]:
        """Return curated search results based on query keywords when all search engines fail"""
        try:
            query_lower = query.lower()
            curated_results = []
            
            # Programming languages and frameworks
            if any(keyword in query_lower for keyword in ['scala', 'functional programming']):
                curated_results = [
                    {'title': 'Scala Official Documentation', 'url': 'https://docs.scala-lang.org/', 'description': 'Official Scala documentation and guides'},
                    {'title': 'Scala Exercises', 'url': 'https://www.scala-exercises.org/', 'description': 'Interactive Scala exercises and tutorials'},
                    {'title': 'Rock the JVM', 'url': 'https://rockthejvm.com/', 'description': 'Advanced Scala and functional programming courses'},
                ]
            elif any(keyword in query_lower for keyword in ['python', 'django', 'flask']):
                curated_results = [
                    {'title': 'Python.org', 'url': 'https://www.python.org/', 'description': 'Official Python website with documentation'},
                    {'title': 'Real Python', 'url': 'https://realpython.com/', 'description': 'Practical Python tutorials and articles'},
                    {'title': 'Python Package Index', 'url': 'https://pypi.org/', 'description': 'Find and install Python packages'},
                ]
            elif any(keyword in query_lower for keyword in ['react', 'javascript', 'js', 'frontend']):
                curated_results = [
                    {'title': 'React Documentation', 'url': 'https://react.dev/', 'description': 'Official React documentation'},
                    {'title': 'MDN Web Docs', 'url': 'https://developer.mozilla.org/', 'description': 'Comprehensive web development resources'},
                    {'title': 'JavaScript.info', 'url': 'https://javascript.info/', 'description': 'Modern JavaScript tutorial'},
                ]
            elif any(keyword in query_lower for keyword in ['java', 'spring', 'jvm']):
                curated_results = [
                    {'title': 'Oracle Java Documentation', 'url': 'https://docs.oracle.com/en/java/', 'description': 'Official Oracle Java documentation'},
                    {'title': 'Spring Framework', 'url': 'https://spring.io/', 'description': 'Spring Framework documentation and guides'},
                    {'title': 'Baeldung Java', 'url': 'https://www.baeldung.com/', 'description': 'Java and Spring tutorials'},
                ]
            
            # Learning platforms
            elif any(keyword in query_lower for keyword in ['course', 'tutorial', 'learn']):
                curated_results = [
                    {'title': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/', 'description': 'Free coding courses and certifications'},
                    {'title': 'Coursera', 'url': 'https://www.coursera.org/', 'description': 'Online courses from top universities'},
                    {'title': 'edX', 'url': 'https://www.edx.org/', 'description': 'Free online courses from MIT, Harvard, and more'},
                ]
            
            # YouTube content
            elif 'youtube' in query_lower:
                curated_results = [
                    {'title': 'YouTube Search', 'url': f'https://www.youtube.com/results?search_query={quote(query)}', 'description': 'YouTube search results'},
                ]
            
            # Default fallback
            else:
                curated_results = [
                    {'title': 'Stack Overflow', 'url': f'https://stackoverflow.com/search?q={quote(query)}', 'description': 'Programming Q&A community'},
                    {'title': 'GitHub', 'url': f'https://github.com/search?q={quote(query)}', 'description': 'Code repositories and projects'},
                    {'title': 'Reddit Programming', 'url': f'https://www.reddit.com/search/?q={quote(query)}', 'description': 'Programming discussions and resources'},
                ]
            
            logger.info(f"Using curated results for query: {query}")
            return curated_results
            
        except Exception as e:
            logger.error(f"Error generating curated results: {str(e)}")
            return [
                {'title': 'Stack Overflow', 'url': 'https://stackoverflow.com/', 'description': 'Programming Q&A community'},
                {'title': 'GitHub', 'url': 'https://github.com/', 'description': 'Code repositories and projects'},
            ]
    
    def _get_fallback_blogs(self, topic: str) -> List[Resource]:
        """Get fallback blog resources when search fails"""
        fallback_blogs = {
            'scala': [
                Resource("Scala Official Blog", "https://www.scala-lang.org/blog/", "Official Scala blog with news and tutorials", "Scala Blog"),
                Resource("Rock the JVM Scala Articles", "https://blog.rockthejvm.com/", "High-quality Scala and functional programming articles", "Rock the JVM"),
                Resource("Baeldung Scala", "https://www.baeldung.com/scala/", "Comprehensive Scala tutorials and guides", "Baeldung"),
            ],
            'python': [
                Resource("Real Python", "https://realpython.com/", "Practical Python tutorials and articles", "Real Python"),
                Resource("Python.org Blog", "https://blog.python.org/", "Official Python blog", "Python"),
            ],
            'react': [
                Resource("React Blog", "https://react.dev/blog", "Official React blog", "React"),
                Resource("Dev.to React", "https://dev.to/t/react", "Community React articles", "Dev.to"),
            ]
        }
        
        topic_lower = topic.lower()
        for key, blogs in fallback_blogs.items():
            if key in topic_lower or topic_lower in key:
                return blogs
        
        # Generic fallback
        return [
            Resource(f"{topic.title()} Resources", f"https://github.com/topics/{topic.lower()}", f"GitHub repositories related to {topic}", "GitHub")
        ]
    
    def _get_fallback_youtube(self, topic: str) -> List[Resource]:
        """Get fallback YouTube resources when search fails"""
        fallback_youtube = {
            'scala': [
                Resource("Rock the JVM Scala Course", "https://www.youtube.com/watch?v=DzFt0YkZo8M", "Complete Scala programming course", "Rock the JVM"),
                Resource("Scala Fundamentals", "https://www.youtube.com/results?search_query=scala+programming+tutorial", "Scala programming fundamentals", "YouTube"),
            ],
            'python': [
                Resource("Python Tutorial for Beginners", "https://www.youtube.com/results?search_query=python+tutorial+beginners", "Python programming for beginners", "YouTube"),
            ],
            'react': [
                Resource("React Crash Course", "https://www.youtube.com/results?search_query=react+crash+course", "React.js crash course", "YouTube"),
            ]
        }
        
        topic_lower = topic.lower()
        for key, videos in fallback_youtube.items():
            if key in topic_lower or topic_lower in key:
                return videos
        
        return []
    
    def _get_fallback_courses(self, topic: str, course_type: str = "free") -> List[Resource]:
        """Get fallback course resources when search fails"""
        fallback_courses = {
            'scala': [
                Resource("Coursera Scala Course", "https://www.coursera.org/specializations/scala", "Functional Programming in Scala Specialization", "Coursera", "Free" if course_type == "free" else "$39-79/month"),
                Resource("edX Scala Course", "https://www.edx.org/learn/scala", "Introduction to Scala programming", "edX", "Free" if course_type == "free" else "$50-100"),
            ],
            'python': [
                Resource("freeCodeCamp Python", "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "Scientific Computing with Python", "freeCodeCamp", "Free"),
            ],
            'react': [
                Resource("freeCodeCamp React", "https://www.freecodecamp.org/learn/front-end-development-libraries/", "Front End Development Libraries", "freeCodeCamp", "Free"),
            ]
        }
        
        topic_lower = topic.lower()
        for key, courses in fallback_courses.items():
            if key in topic_lower or topic_lower in key:
                return courses
        
        return [] 