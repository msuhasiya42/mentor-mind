"""
OpenRouter-based search engine for generating comprehensive learning resources
"""
import asyncio
import aiohttp
import logging
import json
from typing import List, Dict
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

logger = logging.getLogger(__name__)


class LLMSearchEngine:
    """OpenRouter-based search engine that generates comprehensive learning resources using persona-based prompting"""
    
    def __init__(self):
        self.session = None
        
        # Learning resource personas for different types of content
        self.personas = {
            "technical_mentor": {
                "role": "You are an experienced software engineering mentor with 15+ years of experience",
                "expertise": "You specialize in helping beginners learn programming languages, frameworks, and development practices",
                "style": "You provide clear, structured learning paths with practical examples and real-world applications"
            },
            "academic_educator": {
                "role": "You are a computer science professor at a top university",
                "expertise": "You excel at explaining complex theoretical concepts and providing comprehensive educational resources",
                "style": "You focus on foundational knowledge, official documentation, and authoritative sources"
            },
            "industry_expert": {
                "role": "You are a senior tech lead working at major tech companies",
                "expertise": "You know the most current industry practices, tools, and real-world applications",
                "style": "You recommend practical courses, certifications, and resources that are valued in the industry"
            },
            "content_curator": {
                "role": "You are a learning content curator who has reviewed thousands of educational resources",
                "expertise": "You know the best YouTube channels, blogs, free courses, and learning platforms for any topic",
                "style": "You provide diverse, high-quality resources categorized by learning style and difficulty level"
            }
        }
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def search(self, query: str, session: aiohttp.ClientSession = None) -> List[Dict]:
        """Generate comprehensive learning resources using enhanced fallback with optional OpenRouter enhancement"""
        try:
            logger.info(f"Generating comprehensive learning resources for: {query}")
            
            # Start with enhanced fallback resources (always reliable)
            fallback_resources = self._generate_fallback_resources(query)
            logger.info(f"Generated {len(fallback_resources)} enhanced fallback resources")
            
            # Only attempt OpenRouter enhancement if API token is available
            if settings.OPENROUTER_API_KEY and len(fallback_resources) < 20:
                try:
                    logger.info("Attempting OpenRouter AI enhancement...")
                    
                    # Try to get additional resources from OpenRouter personas
                    llm_resources = []
                    for persona_name, persona_config in self.personas.items():
                        try:
                            resources = await self._generate_resources_with_persona(query, persona_name, persona_config)
                            if resources:
                                llm_resources.extend(resources)
                                logger.info(f"OpenRouter {persona_name} generated {len(resources)} additional resources")
                        except Exception as e:
                            logger.warning(f"OpenRouter {persona_name} failed: {str(e)}")
                            continue
                    
                    # Combine and deduplicate if we got LLM resources
                    if llm_resources:
                        all_resources = fallback_resources + llm_resources
                        unique_resources = self._deduplicate_resources(all_resources)
                        logger.info(f"Combined total: {len(unique_resources)} unique resources (fallback + OpenRouter)")
                        return unique_resources[:25]
                        
                except Exception as e:
                    logger.warning(f"OpenRouter enhancement failed: {str(e)}")
            
            # Return enhanced fallback resources (always available)
            logger.info(f"Returning {len(fallback_resources)} enhanced fallback resources")
            return fallback_resources[:25]
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            # Emergency fallback - basic resources
            return [
                {
                    'title': f'{query} Getting Started Guide',
                    'url': f'https://www.google.com/search?q={query}+tutorial+getting+started',
                    'description': f'Getting started with {query}',
                    'platform': 'Web Search',
                    'difficulty': 'Beginner',
                    'price': 'Free',
                    'type': 'tutorial',
                    'persona_source': 'emergency_fallback'
                }
            ]
    
    async def _generate_resources_with_persona(self, query: str, persona_name: str, persona_config: Dict) -> List[Dict]:
        """Generate resources using a specific persona via OpenRouter"""
        try:
            if not settings.OPENROUTER_API_KEY:
                logger.warning("OpenRouter API key not found, using fallback")
                return self._generate_fallback_resources(query)
            
            session = await self._get_session()
            
            # Create comprehensive prompt with persona
            prompt = self._create_persona_prompt(query, persona_config)
            
            # Use OpenAI-compatible chat format for OpenRouter
            messages = [
                {
                    "role": "system",
                    "content": f"{persona_config['role']}. {persona_config['expertise']}. {persona_config['style']}"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            payload = {
                "model": settings.DEFAULT_MODEL,
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7,
                "stream": False
            }
            
            api_url = f"{settings.OPENROUTER_API_BASE}/chat/completions"
            
            async with session.post(
                api_url,
                headers=settings.openrouter_headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        generated_text = result['choices'][0]['message']['content']
                        resources = self._parse_generated_resources(generated_text, persona_name)
                        return resources
                elif response.status == 429:
                    logger.warning("Rate limit exceeded for OpenRouter")
                else:
                    logger.warning(f"OpenRouter API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error generating resources with persona {persona_name}: {str(e)}")
        
        return []
    
    def _create_persona_prompt(self, query: str, persona_config: Dict) -> str:
        """Create a comprehensive prompt with persona details"""
        return f"""A student wants to learn about "{query}". Please provide a comprehensive list of learning resources including:

1. **Documentation & Official Resources**
   - Official documentation links
   - API references
   - Getting started guides

2. **Interactive Learning**
   - Online courses (both free and paid)
   - Interactive tutorials
   - Coding bootcamps

3. **Video Content**
   - YouTube channels
   - Video course platforms
   - Conference talks

4. **Written Content**
   - Technical blogs
   - Articles and tutorials
   - Books and ebooks

5. **Practical Resources**
   - GitHub repositories
   - Code examples
   - Practice platforms

For each resource, provide:
- Title
- Platform/Source
- Description (why it's valuable)
- Difficulty level (Beginner/Intermediate/Advanced)
- Whether it's free or paid

Format your response as a structured list with clear categories. Be specific about actual resource names, popular platforms, and well-known creators in the field.

Topic: {query}

Resources:"""
    
    def _parse_generated_resources(self, generated_text: str, persona_name: str) -> List[Dict]:
        """Parse the generated text into structured resources"""
        resources = []
        lines = generated_text.split('\n')
        
        current_resource = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for resource indicators
            if any(indicator in line.lower() for indicator in ['tutorial', 'course', 'documentation', 'guide', 'channel', 'platform', 'book', 'article', 'repository']):
                
                # Extract title and create resource
                title = self._extract_title(line)
                if title and len(title) > 3:
                    
                    # Determine resource type and create appropriate URLs
                    resource_type, platform = self._determine_resource_type(line)
                    
                    resource = {
                        'title': title,
                        'url': self._generate_resource_url(title, resource_type),
                        'description': self._extract_description(line, lines),
                        'platform': platform,
                        'difficulty': self._extract_difficulty(line),
                        'price': self._extract_price_info(line),
                        'type': resource_type,
                        'persona_source': persona_name
                    }
                    
                    resources.append(resource)
        
        # If structured parsing didn't work well, use fallback parsing
        if len(resources) < 3:
            resources.extend(self._fallback_parse_resources(generated_text, persona_name))
        
        return resources[:8]  # Limit resources per persona
    
    def _extract_title(self, line: str) -> str:
        """Extract title from a line"""
        # Remove common prefixes and clean up
        line = line.strip()
        
        # Remove bullet points, numbers, etc.
        import re
        line = re.sub(r'^[-•*\d+\.\)]+\s*', '', line)
        
        # Extract text before description separators
        separators = [' - ', ' – ', ' (', ' |', ': ']
        for sep in separators:
            if sep in line:
                line = line.split(sep)[0]
                break
        
        return line.strip()
    
    def _determine_resource_type(self, line: str) -> tuple:
        """Determine resource type and platform from line content"""
        line_lower = line.lower()
        
        if any(keyword in line_lower for keyword in ['youtube', 'video', 'channel']):
            return 'video', 'YouTube'
        elif any(keyword in line_lower for keyword in ['course', 'udemy', 'coursera', 'edx']):
            return 'course', 'Online Course Platform'
        elif any(keyword in line_lower for keyword in ['documentation', 'docs', 'official']):
            return 'documentation', 'Official Documentation'
        elif any(keyword in line_lower for keyword in ['blog', 'article', 'medium']):
            return 'blog', 'Technical Blog'
        elif any(keyword in line_lower for keyword in ['github', 'repository', 'repo']):
            return 'repository', 'GitHub'
        elif any(keyword in line_lower for keyword in ['book', 'ebook']):
            return 'book', 'Book'
        else:
            return 'tutorial', 'Web Resource'
    
    def _generate_resource_url(self, title: str, resource_type: str) -> str:
        """Generate appropriate URL based on resource type and title"""
        # Create search URLs for different platforms
        search_query = title.replace(' ', '+')
        
        url_templates = {
            'video': f"https://www.youtube.com/results?search_query={search_query}",
            'course': f"https://www.coursera.org/search?query={search_query}",
            'documentation': f"https://www.google.com/search?q={search_query}+official+documentation",
            'blog': f"https://www.google.com/search?q={search_query}+tutorial+blog",
            'repository': f"https://github.com/search?q={search_query}",
            'book': f"https://www.google.com/search?q={search_query}+book+pdf",
            'tutorial': f"https://www.google.com/search?q={search_query}+tutorial"
        }
        
        return url_templates.get(resource_type, f"https://www.google.com/search?q={search_query}")
    
    def _extract_description(self, line: str, all_lines: List[str]) -> str:
        """Extract description from line or surrounding context"""
        # Look for description after separators
        separators = [' - ', ' – ', ' (', ': ']
        for sep in separators:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) > 1:
                    return parts[1].strip().rstrip(')')
        
        # If no description in current line, create a generic one
        return f"Learn more about this resource for comprehensive understanding."
    
    def _extract_difficulty(self, line: str) -> str:
        """Extract difficulty level from line"""
        line_lower = line.lower()
        if 'beginner' in line_lower or 'basic' in line_lower:
            return 'Beginner'
        elif 'advanced' in line_lower:
            return 'Advanced'
        elif 'intermediate' in line_lower:
            return 'Intermediate'
        else:
            return 'All Levels'
    
    def _extract_price_info(self, line: str) -> str:
        """Extract price information from line"""
        line_lower = line.lower()
        if 'free' in line_lower:
            return 'Free'
        elif any(keyword in line_lower for keyword in ['paid', 'premium', '$', 'subscription']):
            return 'Paid'
        else:
            return 'Free'
    
    def _fallback_parse_resources(self, text: str, persona_name: str) -> List[Dict]:
        """Fallback parsing when structured parsing fails"""
        resources = []
        
        # Common learning resource names and platforms
        common_resources = [
            {'title': 'Official Documentation', 'type': 'documentation', 'platform': 'Official'},
            {'title': 'Codecademy Interactive Course', 'type': 'course', 'platform': 'Codecademy'},
            {'title': 'freeCodeCamp Tutorial', 'type': 'video', 'platform': 'YouTube'},
            {'title': 'MDN Web Docs', 'type': 'documentation', 'platform': 'Mozilla'},
            {'title': 'Coursera Specialization', 'type': 'course', 'platform': 'Coursera'},
            {'title': 'Udemy Complete Course', 'type': 'course', 'platform': 'Udemy'},
            {'title': 'GitHub Awesome List', 'type': 'repository', 'platform': 'GitHub'},
            {'title': 'Stack Overflow Discussions', 'type': 'blog', 'platform': 'Stack Overflow'}
        ]
        
        for resource_template in common_resources:
            resources.append({
                'title': resource_template['title'],
                'url': self._generate_resource_url(resource_template['title'], resource_template['type']),
                'description': f"High-quality {resource_template['type']} resource for comprehensive learning",
                'platform': resource_template['platform'],
                'difficulty': 'All Levels',
                'price': 'Free' if resource_template['platform'] in ['YouTube', 'GitHub', 'Mozilla'] else 'Mixed',
                'type': resource_template['type'],
                'persona_source': persona_name
            })
        
        return resources
    
    def _deduplicate_resources(self, resources: List[Dict]) -> List[Dict]:
        """Remove duplicate resources while preserving diversity"""
        seen_titles = set()
        unique_resources = []
        
        # Sort by persona diversity to ensure we get different perspectives
        resources.sort(key=lambda x: x.get('persona_source', ''))
        
        for resource in resources:
            title_lower = resource['title'].lower()
            # Simple deduplication based on title similarity
            if not any(title_lower in seen_title or seen_title in title_lower for seen_title in seen_titles):
                seen_titles.add(title_lower)
                unique_resources.append(resource)
        
        return unique_resources
    
    def _generate_fallback_resources(self, query: str) -> List[Dict]:
        """Generate fallback resources when OpenRouter fails"""
        logger.info(f"Using enhanced fallback resource generation for: {query}")
        
        # Enhanced fallback with comprehensive resources for each persona
        query_lower = query.lower()
        
        fallback_resources = []
        
        # Technical Mentor Persona Resources
        fallback_resources.extend([
            {
                'title': f'{query} Hands-On Tutorial',
                'url': f'https://www.youtube.com/results?search_query={query}+tutorial+hands+on',
                'description': 'Step-by-step practical tutorial with real-world examples',
                'platform': 'YouTube',
                'difficulty': 'Beginner',
                'price': 'Free',
                'type': 'video',
                'persona_source': 'technical_mentor'
            },
            {
                'title': f'Build Your First {query} Project',
                'url': f'https://github.com/search?q={query}+project+beginner',
                'description': 'Complete project guide with source code and explanations',
                'platform': 'GitHub',
                'difficulty': 'Intermediate',
                'price': 'Free',
                'type': 'repository',
                'persona_source': 'technical_mentor'
            }
        ])
        
        # Academic Educator Persona Resources
        fallback_resources.extend([
            {
                'title': f'{query} Official Documentation',
                'url': f'https://www.google.com/search?q={query}+official+documentation',
                'description': 'Comprehensive official documentation and API reference',
                'platform': 'Official Documentation',
                'difficulty': 'All Levels',
                'price': 'Free',
                'type': 'documentation',
                'persona_source': 'academic_educator'
            },
            {
                'title': f'University Course: Introduction to {query}',
                'url': f'https://www.coursera.org/search?query={query}',
                'description': 'Structured academic course covering theoretical foundations',
                'platform': 'Coursera',
                'difficulty': 'Intermediate',
                'price': 'Free',
                'type': 'course',
                'persona_source': 'academic_educator'
            }
        ])
        
        # Industry Expert Persona Resources
        fallback_resources.extend([
            {
                'title': f'Professional {query} Certification',
                'url': f'https://www.udemy.com/courses/search/?q={query}+certification',
                'description': 'Industry-recognized certification program',
                'platform': 'Udemy',
                'difficulty': 'Advanced',
                'price': 'Paid',
                'type': 'course',
                'persona_source': 'industry_expert'
            },
            {
                'title': f'{query} Best Practices Guide',
                'url': f'https://medium.com/search?q={query}+best+practices',
                'description': 'Industry expert insights and best practices',
                'platform': 'Medium',
                'difficulty': 'Intermediate',
                'price': 'Free',
                'type': 'blog',
                'persona_source': 'industry_expert'
            }
        ])
        
        # Content Curator Persona Resources
        fallback_resources.extend([
            {
                'title': f'Awesome {query} Resources',
                'url': f'https://github.com/search?q=awesome+{query}',
                'description': 'Curated list of the best tools, libraries, and resources',
                'platform': 'GitHub',
                'difficulty': 'All Levels',
                'price': 'Free',
                'type': 'repository',
                'persona_source': 'content_curator'
            },
            {
                'title': f'{query} Complete Video Course',
                'url': f'https://www.youtube.com/results?search_query={query}+complete+course',
                'description': 'Comprehensive video course series',
                'platform': 'YouTube',
                'difficulty': 'Beginner',
                'price': 'Free',
                'type': 'video',
                'persona_source': 'content_curator'
            },
            {
                'title': f'Learn {query} - Interactive Course',
                'url': f'https://www.codecademy.com/search?query={query}',
                'description': 'Interactive lessons with hands-on coding exercises',
                'platform': 'Codecademy',
                'difficulty': 'Beginner',
                'price': 'Mixed',
                'type': 'course',
                'persona_source': 'content_curator'
            }
        ])
        
        # Add topic-specific resources based on common topics
        if any(keyword in query_lower for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            fallback_resources.extend([
                {
                    'title': 'Stanford CS229 Machine Learning Course',
                    'url': 'https://cs229.stanford.edu/',
                    'description': 'World-renowned Stanford course on machine learning',
                    'platform': 'Stanford Online',
                    'difficulty': 'Advanced',
                    'price': 'Free',
                    'type': 'course',
                    'persona_source': 'academic_educator'
                },
                {
                    'title': 'Fast.ai Practical Deep Learning',
                    'url': 'https://course.fast.ai/',
                    'description': 'Top-rated practical course for deep learning',
                    'platform': 'Fast.ai',
                    'difficulty': 'Intermediate',
                    'price': 'Free',
                    'type': 'course',
                    'persona_source': 'content_curator'
                },
                {
                    'title': '3Blue1Brown Neural Networks Series',
                    'url': 'https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi',
                    'description': 'Beautiful visual explanations of neural networks',
                    'platform': 'YouTube',
                    'difficulty': 'Intermediate',
                    'price': 'Free',
                    'type': 'video',
                    'persona_source': 'content_curator'
                }
            ])
        
        if any(keyword in query_lower for keyword in ['python', 'programming']):
            fallback_resources.extend([
                {
                    'title': 'Python.org Official Tutorial',
                    'url': 'https://docs.python.org/3/tutorial/',
                    'description': 'Official Python tutorial and documentation',
                    'platform': 'Python.org',
                    'difficulty': 'Beginner',
                    'price': 'Free',
                    'type': 'documentation',
                    'persona_source': 'academic_educator'
                },
                {
                    'title': 'Automate the Boring Stuff with Python',
                    'url': 'https://automatetheboringstuff.com/',
                    'description': 'Practical Python programming for beginners',
                    'platform': 'Online Book',
                    'difficulty': 'Beginner',
                    'price': 'Free',
                    'type': 'book',
                    'persona_source': 'technical_mentor'
                }
            ])
        
        return fallback_resources
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()


class SearchEngineManager:
    """Manages OpenRouter-based search engine (maintains compatibility with existing code)"""
    
    def __init__(self):
        self.llm_engine = LLMSearchEngine()
    
    async def search(self, query: str, session: aiohttp.ClientSession = None) -> List[Dict]:
        """Search using OpenRouter-based approach"""
        return await self.llm_engine.search(query, session)
    
    async def close(self):
        """Clean up resources"""
        if self.llm_engine:
            await self.llm_engine.close()