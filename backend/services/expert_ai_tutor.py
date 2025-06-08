"""
Expert AI Tutor Service - Single LLM call for curated learning resources
"""
import asyncio
import aiohttp
import logging
import json
from typing import List, Dict
import re
import sys
import os
import time
from functools import lru_cache

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from .learning_path_generator import Resource

logger = logging.getLogger(__name__)


class ExpertAITutor:
    """Expert AI Tutor that provides curated learning resources in a single call"""
    
    def __init__(self):
        self.session = None
        self.last_api_call = 0
        self.rate_limit_delay = 2  # Minimum seconds between API calls
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        logger.info("Expert AI Tutor initialized with rate limiting optimizations")
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=90)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def get_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get curated learning resources from expert AI tutor in a single call"""
        try:
            logger.info(f"Getting curated resources from expert AI tutor for: {topic}")
            
            # Check if we should skip AI due to consecutive failures
            if self.consecutive_failures >= self.max_consecutive_failures:
                logger.info(f"Skipping AI call due to {self.consecutive_failures} consecutive failures, using manual curation")
                return self._get_enhanced_manual_resources(topic)
            
            # Try AI-powered resource curation first (with rate limiting)
            if settings.OPENROUTER_API_KEY:
                # Implement rate limiting
                time_since_last_call = time.time() - self.last_api_call
                if time_since_last_call < self.rate_limit_delay:
                    wait_time = self.rate_limit_delay - time_since_last_call
                    logger.info(f"Rate limiting: waiting {wait_time:.1f}s before API call")
                    await asyncio.sleep(wait_time)
                
                ai_resources = await self._get_ai_curated_resources(topic)
                if ai_resources:
                    self.consecutive_failures = 0  # Reset failure counter on success
                    logger.info(f"AI tutor provided {sum(len(resources) for resources in ai_resources.values())} curated resources")
                    return ai_resources
                else:
                    self.consecutive_failures += 1
                    logger.warning(f"AI call failed, consecutive failures: {self.consecutive_failures}")
            
            # Fallback to enhanced manual curation
            logger.info("Using enhanced manual curation")
            return self._get_enhanced_manual_resources(topic)
            
        except Exception as e:
            logger.error(f"Error getting curated resources: {str(e)}")
            self.consecutive_failures += 1
            return self._get_basic_fallback_resources(topic)
    
    async def _get_ai_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get AI-curated resources using expert tutor persona with rate limiting"""
        try:
            session = await self._get_session()
            
            # Record API call time for rate limiting
            self.last_api_call = time.time()
            
            # Create expert tutor prompt
            prompt = self._create_expert_tutor_prompt(topic)
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert AI tutor with 15+ years of experience in technology education. You specialize in recommending the BEST and most FAMOUS learning resources that are proven effective for students. 

Your expertise includes:
- Knowing the most popular and well-regarded blogs, documentation, and tutorials
- Identifying the best YouTube channels and playlists for specific topics
- Recommending high-quality free courses from platforms like edX, Coursera, Khan Academy
- Suggesting valuable paid courses from Udemy, Pluralsight, and other platforms
- Providing direct, specific resource links rather than generic searches

You always provide REAL, SPECIFIC resources that are well-known in the developer community."""
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            payload = {
                "model": settings.DEFAULT_MODEL,
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.3,
                "stream": False
            }
            
            api_url = f"{settings.OPENROUTER_API_BASE}/chat/completions"
            
            async with session.post(
                api_url,
                headers=settings.openrouter_headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        generated_text = result['choices'][0]['message']['content']
                        return self._parse_ai_resources(generated_text, topic)
                elif response.status == 429:
                    logger.warning("Rate limit exceeded for OpenRouter - will use manual curation")
                    # Increase delay for future calls
                    self.rate_limit_delay = min(self.rate_limit_delay * 1.5, 10)  # Max 10 seconds
                    logger.info(f"Increased rate limit delay to {self.rate_limit_delay:.1f}s")
                else:
                    logger.warning(f"OpenRouter API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error getting AI curated resources: {str(e)}")
        
        return {}
    
    def _create_expert_tutor_prompt(self, topic: str) -> str:
        """Create comprehensive prompt for expert AI tutor"""
        return f"""As an expert AI tutor, please provide the BEST and most FAMOUS learning resources for "{topic}". Focus on quality over quantity - recommend resources that are well-known and proven effective in the developer community.

Please provide SPECIFIC, REAL resources in the following categories:

## 📚 DOCUMENTATION & OFFICIAL RESOURCES (3-5 resources)
- Official documentation with actual URLs
- API references and getting started guides
- Famous developer guides and references

## 📝 BLOGS & ARTICLES (3-5 resources) 
- Well-known technical blogs (like Medium articles, dev.to posts)
- Famous tutorial series and guides
- Popular developer blog posts about {topic}

## 🎥 YOUTUBE CONTENT (3-5 resources)
- Best YouTube channels for {topic}
- Famous playlists and tutorial series
- Popular conference talks and presentations

## 🆓 FREE COURSES (3-5 resources)
- edX courses
- Coursera free courses
- Khan Academy content
- freeCodeCamp resources
- Other reputable free learning platforms

## 💰 PAID COURSES (3-5 resources)
- Top-rated Udemy courses
- Pluralsight paths
- LinkedIn Learning courses
- Other premium course platforms

For each resource, provide:
- **Title**: Exact title
- **URL**: Direct link (if you know specific URLs, provide them; otherwise indicate the platform)
- **Description**: Why this resource is excellent (1-2 sentences)
- **Platform**: Where to find it
- **Price**: Free/Paid with approximate cost if known

Focus on resources that are:
- Well-established and popular in the community
- Highly rated with good reviews
- Frequently recommended by developers
- Up-to-date and actively maintained

Topic: {topic}"""
    
    def _parse_ai_resources(self, generated_text: str, topic: str) -> Dict[str, List[Resource]]:
        """Parse AI-generated resources into categorized Resource objects"""
        try:
            categories = {
                'docs': [],
                'blogs': [],
                'youtube': [],
                'free_courses': [],
                'paid_courses': []
            }
            
            lines = generated_text.split('\n')
            current_category = None
            current_resource = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect category headers
                if '📚' in line or 'DOCUMENTATION' in line.upper() or 'OFFICIAL' in line.upper():
                    current_category = 'docs'
                    continue
                elif '📝' in line or 'BLOG' in line.upper() or 'ARTICLE' in line.upper():
                    current_category = 'blogs'
                    continue
                elif '🎥' in line or 'YOUTUBE' in line.upper() or 'VIDEO' in line.upper():
                    current_category = 'youtube'
                    continue
                elif '🆓' in line or 'FREE COURSE' in line.upper():
                    current_category = 'free_courses'
                    continue
                elif '💰' in line or 'PAID COURSE' in line.upper():
                    current_category = 'paid_courses'
                    continue
                
                # Parse resource information
                if current_category and line.startswith('-'):
                    resource_text = line[1:].strip()
                    resource = self._extract_resource_from_text(resource_text, topic)
                    if resource:
                        categories[current_category].append(resource)
                
                # Look for structured resource information
                elif '**Title**:' in line:
                    if current_resource and current_category:
                        resource = self._create_resource_from_dict(current_resource, topic)
                        if resource:
                            categories[current_category].append(resource)
                    current_resource = {'title': line.split('**Title**:')[1].strip()}
                elif '**URL**:' in line:
                    current_resource['url'] = line.split('**URL**:')[1].strip()
                elif '**Description**:' in line:
                    current_resource['description'] = line.split('**Description**:')[1].strip()
                elif '**Platform**:' in line:
                    current_resource['platform'] = line.split('**Platform**:')[1].strip()
                elif '**Price**:' in line:
                    current_resource['price'] = line.split('**Price**:')[1].strip()
            
            # Don't forget the last resource
            if current_resource and current_category:
                resource = self._create_resource_from_dict(current_resource, topic)
                if resource:
                    categories[current_category].append(resource)
            
            # Fallback parsing if structured parsing didn't work well
            if sum(len(resources) for resources in categories.values()) < 5:
                return self._fallback_parse_resources(generated_text, topic)
            
            logger.info(f"Parsed AI resources: {sum(len(resources) for resources in categories.values())} total resources")
            return categories
            
        except Exception as e:
            logger.error(f"Error parsing AI resources: {str(e)}")
            return self._fallback_parse_resources(generated_text, topic)
    
    def _extract_resource_from_text(self, text: str, topic: str) -> Resource:
        """Extract resource information from a line of text"""
        try:
            parts = text.split(' - ', 1)
            if len(parts) >= 2:
                title = parts[0].strip()
                description = parts[1].strip()
                url = self._generate_resource_url(title, topic)
                
                return Resource(
                    title=title,
                    url=url,
                    description=description,
                    platform=self._detect_platform(title, description),
                    price=self._detect_price(description)
                )
            else:
                title = text.strip()
                if len(title) > 3:
                    return Resource(
                        title=title,
                        url=self._generate_resource_url(title, topic),
                        description=f"Learn {topic} with {title}",
                        platform=self._detect_platform(title, ""),
                        price="Free"
                    )
        except Exception as e:
            logger.error(f"Error extracting resource from text: {str(e)}")
        
        return None
    
    def _create_resource_from_dict(self, resource_dict: Dict, topic: str) -> Resource:
        """Create Resource object from dictionary of parsed fields"""
        try:
            title = resource_dict.get('title', '').strip()
            if not title:
                return None
            
            url = resource_dict.get('url', '').strip()
            if not url or url.lower() in ['n/a', 'varies', 'see platform']:
                url = self._generate_resource_url(title, topic)
            
            return Resource(
                title=title,
                url=url,
                description=resource_dict.get('description', f"Learn {topic} with {title}"),
                platform=resource_dict.get('platform', self._detect_platform(title, resource_dict.get('description', ''))),
                price=resource_dict.get('price', 'Free')
            )
        except Exception as e:
            logger.error(f"Error creating resource from dict: {str(e)}")
            return None
    
    def _fallback_parse_resources(self, text: str, topic: str) -> Dict[str, List[Resource]]:
        """Fallback parsing method for AI-generated resources"""
        categories = {
            'docs': [],
            'blogs': [],
            'youtube': [],
            'free_courses': [],
            'paid_courses': []
        }
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) < 10:
                continue
            
            if any(keyword in line.lower() for keyword in ['tutorial', 'guide', 'course', 'documentation', 'blog']):
                resource = self._extract_resource_from_text(line, topic)
                if resource:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['official', 'docs', 'documentation', 'api']):
                        categories['docs'].append(resource)
                    elif any(keyword in line_lower for keyword in ['youtube', 'video', 'channel']):
                        categories['youtube'].append(resource)
                    elif any(keyword in line_lower for keyword in ['blog', 'article', 'medium']):
                        categories['blogs'].append(resource)
                    elif any(keyword in line_lower for keyword in ['free', 'edx', 'coursera']):
                        categories['free_courses'].append(resource)
                    elif any(keyword in line_lower for keyword in ['udemy', 'paid', 'premium']):
                        categories['paid_courses'].append(resource)
                    else:
                        categories['free_courses'].append(resource)
        
        return categories
    
    def _generate_resource_url(self, title: str, topic: str) -> str:
        """Generate plausible URLs for resources"""
        title_clean = re.sub(r'[^\w\s]', '', title.lower())
        topic_clean = re.sub(r'[^\w\s]', '', topic.lower())
        
        if 'official' in title.lower() or 'documentation' in title.lower():
            return f"https://docs.{topic_clean.replace(' ', '')}.org"
        elif 'youtube' in title.lower() or 'video' in title.lower():
            return f"https://www.youtube.com/results?search_query={topic_clean.replace(' ', '+')}"
        elif 'udemy' in title.lower():
            return f"https://www.udemy.com/course/{topic_clean.replace(' ', '-')}"
        elif 'coursera' in title.lower():
            return f"https://www.coursera.org/search?query={topic_clean.replace(' ', '%20')}"
        elif 'edx' in title.lower():
            return f"https://www.edx.org/search?q={topic_clean.replace(' ', '+')}"
        else:
            return f"https://www.google.com/search?q={title_clean.replace(' ', '+')}+{topic_clean.replace(' ', '+')}"
    
    def _detect_platform(self, title: str, description: str) -> str:
        """Detect platform from title and description"""
        text = (title + " " + description).lower()
        
        platforms = {
            'YouTube': ['youtube', 'video', 'channel'],
            'Udemy': ['udemy'],
            'Coursera': ['coursera'],
            'edX': ['edx'],
            'Medium': ['medium'],
            'GitHub': ['github', 'repository'],
            'Official': ['official', 'documentation', 'docs'],
            'freeCodeCamp': ['freecodecamp'],
            'Pluralsight': ['pluralsight'],
            'LinkedIn Learning': ['linkedin learning']
        }
        
        for platform, keywords in platforms.items():
            if any(keyword in text for keyword in keywords):
                return platform
        
        return "Web"
    
    def _detect_price(self, text: str) -> str:
        """Detect price information from text"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['free', 'no cost', '$0']):
            return "Free"
        elif any(keyword in text_lower for keyword in ['paid', 'premium', '$', 'subscription']):
            return "Paid"
        else:
            return "Free"
    
    def _get_enhanced_manual_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Enhanced manual resource curation based on topic"""
        topic_lower = topic.lower()
        
        # Define high-quality resource templates for popular topics
        resource_templates = {
            'react': {
                'docs': [
                    Resource("React Official Documentation", "https://react.dev", "Official React documentation with hooks and modern practices", "Official", "Free"),
                    Resource("React Patterns", "https://reactpatterns.com", "Common React patterns and best practices", "Web", "Free"),
                    Resource("Awesome React", "https://github.com/enaqx/awesome-react", "Curated list of React resources", "GitHub", "Free")
                ],
                'blogs': [
                    Resource("Overreacted by Dan Abramov", "https://overreacted.io", "Deep insights into React by its core maintainer", "Blog", "Free"),
                    Resource("React Blog on dev.to", "https://dev.to/t/react", "Community articles about React development", "Dev.to", "Free"),
                    Resource("Kent C. Dodds Blog", "https://kentcdodds.com/blog", "Practical React tips and best practices", "Blog", "Free")
                ],
                'youtube': [
                    Resource("React Official Channel", "https://www.youtube.com/@ReactJS", "Official React team videos and conferences", "YouTube", "Free"),
                    Resource("Traversy Media React Playlist", "https://www.youtube.com/playlist?list=PLillGF-RfqbY3c2r0htQyVbDJJoBFE6Rb", "Comprehensive React tutorials", "YouTube", "Free"),
                    Resource("The Net Ninja React Series", "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gZD-Tvwfod2gaISzfRiP9d", "Step-by-step React learning", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("React Course on freeCodeCamp", "https://www.freecodecamp.org/learn/front-end-libraries/react/", "Interactive React curriculum", "freeCodeCamp", "Free"),
                    Resource("React Basics on Codecademy", "https://www.codecademy.com/learn/react-101", "Interactive React fundamentals", "Codecademy", "Free"),
                    Resource("Introduction to React on edX", "https://www.edx.org/course/introduction-to-react", "University-level React course", "edX", "Free")
                ],
                'paid_courses': [
                    Resource("Complete React Developer Course", "https://www.udemy.com/course/react-redux/", "Comprehensive React and Redux course", "Udemy", "$89.99"),
                    Resource("React Path on Pluralsight", "https://www.pluralsight.com/paths/react", "Professional React skill path", "Pluralsight", "$29/month"),
                    Resource("Epic React by Kent C. Dodds", "https://epicreact.dev", "Advanced React patterns and practices", "Epic React", "$599")
                ]
            },
            'python': {
                'docs': [
                    Resource("Python Official Documentation", "https://docs.python.org/3/", "Official Python 3 documentation", "Official", "Free"),
                    Resource("Real Python", "https://realpython.com", "High-quality Python tutorials and guides", "Real Python", "Free/Paid"),
                    Resource("Python Package Index", "https://pypi.org", "Repository of Python packages", "PyPI", "Free")
                ],
                'blogs': [
                    Resource("Planet Python", "https://planetpython.org", "Aggregated Python blog posts", "Planet Python", "Free"),
                    Resource("Python Tricks by Dan Bader", "https://realpython.com/python-tricks/", "Advanced Python tips and tricks", "Real Python", "Free"),
                    Resource("Talk Python Blog", "https://talkpython.fm/blog", "Python news and tutorials", "Talk Python", "Free")
                ],
                'youtube': [
                    Resource("Corey Schafer Python Tutorials", "https://www.youtube.com/user/schafer5", "Comprehensive Python tutorials", "YouTube", "Free"),
                    Resource("Programming with Mosh Python", "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "Python tutorial for beginners", "YouTube", "Free"),
                    Resource("Python Explained", "https://www.youtube.com/c/PythonExplained", "Clear Python concept explanations", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("Python for Everybody on Coursera", "https://www.coursera.org/specializations/python", "University of Michigan Python course", "Coursera", "Free"),
                    Resource("Introduction to Python on edX", "https://www.edx.org/course/introduction-to-python", "MIT Python introduction", "edX", "Free"),
                    Resource("Python Course on Codecademy", "https://www.codecademy.com/learn/learn-python-3", "Interactive Python learning", "Codecademy", "Free")
                ],
                'paid_courses': [
                    Resource("Complete Python Bootcamp", "https://www.udemy.com/course/complete-python-bootcamp/", "Comprehensive Python course", "Udemy", "$94.99"),
                    Resource("Python Path on Pluralsight", "https://www.pluralsight.com/paths/python", "Professional Python development", "Pluralsight", "$29/month"),
                    Resource("Python Basics on LinkedIn Learning", "https://www.linkedin.com/learning/python-essential-training", "Professional Python training", "LinkedIn Learning", "$29.99/month")
                ]
            },
            'llm': {
                'docs': [
                    Resource("Hugging Face Transformers Documentation", "https://huggingface.co/docs/transformers", "Official documentation for the most popular LLM library", "Hugging Face", "Free"),
                    Resource("OpenAI API Documentation", "https://platform.openai.com/docs", "Official OpenAI API documentation and guides", "OpenAI", "Free"),
                    Resource("LangChain Documentation", "https://python.langchain.com/docs/get_started/introduction", "Framework for developing LLM applications", "LangChain", "Free")
                ],
                'blogs': [
                    Resource("The Batch by Andrew Ng", "https://www.deeplearning.ai/the-batch/", "Weekly newsletter on AI and ML developments", "DeepLearning.AI", "Free"),
                    Resource("Towards Data Science LLM Articles", "https://towardsdatascience.com/tagged/large-language-models", "Community articles on LLMs and AI", "Medium", "Free"),
                    Resource("OpenAI Blog", "https://openai.com/blog/", "Latest developments and research from OpenAI", "OpenAI", "Free")
                ],
                'youtube': [
                    Resource("Andrej Karpathy's Neural Networks Course", "https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ", "Deep learning fundamentals by former OpenAI researcher", "YouTube", "Free"),
                    Resource("3Blue1Brown Neural Networks", "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi", "Visual explanations of neural networks and deep learning", "YouTube", "Free"),
                    Resource("Two Minute Papers AI Videos", "https://www.youtube.com/c/K%C3%A1rolyZsolnai", "Latest AI research explained simply", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("CS224N: Natural Language Processing with Deep Learning", "https://web.stanford.edu/class/cs224n/", "Stanford's comprehensive NLP course", "Stanford", "Free"),
                    Resource("Deep Learning Specialization", "https://www.coursera.org/specializations/deep-learning", "Andrew Ng's deep learning course series", "Coursera", "Free"),
                    Resource("Hugging Face NLP Course", "https://huggingface.co/learn/nlp-course", "Practical NLP with transformers", "Hugging Face", "Free")
                ],
                'paid_courses': [
                    Resource("Complete Guide to LangChain", "https://www.udemy.com/course/langchain/", "Master LLM application development", "Udemy", "$89.99"),
                    Resource("Advanced NLP with Python", "https://www.pluralsight.com/paths/advanced-nlp-with-python", "Professional NLP development", "Pluralsight", "$29/month"),
                    Resource("LLM Engineering Bootcamp", "https://www.linkedin.com/learning/paths/llm-engineering", "Enterprise LLM development", "LinkedIn Learning", "$29.99/month")
                ]
            },
            'ai': {
                'docs': [
                    Resource("Artificial Intelligence: A Modern Approach", "https://aima.cs.berkeley.edu/", "Classic AI textbook resources and updates", "Berkeley", "Free"),
                    Resource("Google AI Education", "https://ai.google/education/", "Comprehensive AI learning resources from Google", "Google AI", "Free"),
                    Resource("MIT Introduction to AI", "https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-034-artificial-intelligence-fall-2010/", "MIT's foundational AI course materials", "MIT OCW", "Free")
                ],
                'blogs': [
                    Resource("Distill.pub", "https://distill.pub/", "Clear explanations of machine learning concepts", "Distill", "Free"),
                    Resource("Google AI Blog", "https://ai.googleblog.com/", "Latest research and developments from Google AI", "Google", "Free"),
                    Resource("OpenAI Research", "https://openai.com/research/", "Cutting-edge AI research and publications", "OpenAI", "Free")
                ],
                'youtube': [
                    Resource("DeepMind Lectures", "https://www.youtube.com/c/DeepMind", "Advanced AI research presentations", "YouTube", "Free"),
                    Resource("MIT 6.034 Artificial Intelligence", "https://www.youtube.com/playlist?list=PLUl4u3cNGP63gFHB6xb-kVBiQHYe_4hSi", "Complete MIT AI course lectures", "YouTube", "Free"),
                    Resource("AI Explained", "https://www.youtube.com/c/aiexplained-official", "Latest AI developments explained clearly", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("Introduction to Artificial Intelligence", "https://www.edx.org/course/introduction-to-artificial-intelligence", "Columbia University's AI fundamentals", "edX", "Free"),
                    Resource("CS50's Introduction to AI with Python", "https://cs50.harvard.edu/ai/2020/", "Harvard's practical AI programming course", "Harvard", "Free"),
                    Resource("AI for Everyone", "https://www.coursera.org/learn/ai-for-everyone", "Non-technical introduction to AI by Andrew Ng", "Coursera", "Free")
                ],
                'paid_courses': [
                    Resource("Machine Learning Engineering for Production", "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops", "MLOps specialization by Andrew Ng", "Coursera", "$49/month"),
                    Resource("AI Product Manager Nanodegree", "https://www.udacity.com/course/ai-product-manager-nanodegree--nd088", "Managing AI products and teams", "Udacity", "$399/month"),
                    Resource("Applied AI Professional Certificate", "https://www.ibm.com/training/badge/applied-ai-professional-certificate", "IBM's comprehensive AI program", "IBM", "$39/month")
                ]
            },
            'javascript': {
                'docs': [
                    Resource("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "The most comprehensive JavaScript documentation", "MDN", "Free"),
                    Resource("JavaScript.info", "https://javascript.info/", "Modern JavaScript tutorial with detailed explanations", "JavaScript.info", "Free"),
                    Resource("ECMAScript Specification", "https://tc39.es/ecma262/", "Official JavaScript language specification", "TC39", "Free")
                ],
                'blogs': [
                    Resource("JavaScript Weekly", "https://javascriptweekly.com/", "Weekly JavaScript news and articles", "JavaScript Weekly", "Free"),
                    Resource("2ality by Dr. Axel Rauschmayer", "https://2ality.com/", "Deep dives into JavaScript features", "2ality", "Free"),
                    Resource("JavaScript on dev.to", "https://dev.to/t/javascript", "Community JavaScript articles and tutorials", "Dev.to", "Free")
                ],
                'youtube': [
                    Resource("JavaScript Mastery", "https://www.youtube.com/c/JavaScriptMastery", "Modern JavaScript and React projects", "YouTube", "Free"),
                    Resource("The Net Ninja JavaScript", "https://www.youtube.com/playlist?list=PL4cUxeGkcC9i9Ae2D9Ee1RvylH38dKuET", "Complete JavaScript tutorial series", "YouTube", "Free"),
                    Resource("Traversy Media JavaScript", "https://www.youtube.com/playlist?list=PLillGF-RfqbbnEGy3ROiLWk7JMCuSyQtX", "Practical JavaScript tutorials", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("JavaScript Algorithms and Data Structures", "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "Comprehensive JavaScript curriculum", "freeCodeCamp", "Free"),
                    Resource("Introduction to JavaScript", "https://www.codecademy.com/learn/introduction-to-javascript", "Interactive JavaScript fundamentals", "Codecademy", "Free"),
                    Resource("JavaScript Course", "https://www.khanacademy.org/computing/computer-programming/programming", "Beginner-friendly JavaScript course", "Khan Academy", "Free")
                ],
                'paid_courses': [
                    Resource("The Complete JavaScript Course", "https://www.udemy.com/course/the-complete-javascript-course/", "Most popular JavaScript course on Udemy", "Udemy", "$84.99"),
                    Resource("JavaScript Path", "https://www.pluralsight.com/paths/javascript", "Professional JavaScript development track", "Pluralsight", "$29/month"),
                    Resource("JavaScript Essential Training", "https://www.linkedin.com/learning/javascript-essential-training", "Comprehensive JavaScript fundamentals", "LinkedIn Learning", "$29.99/month")
                ]
            },
            'machine learning': {
                'docs': [
                    Resource("Scikit-learn Documentation", "https://scikit-learn.org/stable/", "Most popular machine learning library for Python", "Scikit-learn", "Free"),
                    Resource("TensorFlow Documentation", "https://www.tensorflow.org/learn", "Google's machine learning framework", "TensorFlow", "Free"),
                    Resource("PyTorch Documentation", "https://pytorch.org/tutorials/", "Facebook's deep learning framework", "PyTorch", "Free")
                ],
                'blogs': [
                    Resource("Towards Data Science", "https://towardsdatascience.com/", "Leading publication for data science and ML", "Medium", "Free"),
                    Resource("Google AI Blog", "https://ai.googleblog.com/", "Latest ML research from Google", "Google", "Free"),
                    Resource("OpenAI Blog", "https://openai.com/blog/", "Cutting-edge AI and ML research", "OpenAI", "Free")
                ],
                'youtube': [
                    Resource("3Blue1Brown Neural Networks", "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi", "Visual explanation of neural networks", "YouTube", "Free"),
                    Resource("StatQuest with Josh Starmer", "https://www.youtube.com/c/joshstarmer", "Statistics and ML concepts explained simply", "YouTube", "Free"),
                    Resource("Two Minute Papers", "https://www.youtube.com/c/K%C3%A1rolyZsolnai", "Latest ML research explained", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("Machine Learning by Andrew Ng", "https://www.coursera.org/learn/machine-learning", "Most popular ML course worldwide", "Coursera", "Free"),
                    Resource("CS229 Machine Learning", "https://cs229.stanford.edu/", "Stanford's comprehensive ML course", "Stanford", "Free"),
                    Resource("Introduction to Machine Learning", "https://www.edx.org/course/introduction-to-machine-learning", "MIT's foundational ML course", "edX", "Free")
                ],
                'paid_courses': [
                    Resource("Machine Learning A-Z", "https://www.udemy.com/course/machinelearning/", "Hands-on machine learning course", "Udemy", "$94.99"),
                    Resource("Machine Learning Path", "https://www.pluralsight.com/paths/machine-learning", "Professional ML development track", "Pluralsight", "$29/month"),
                    Resource("Applied Machine Learning", "https://www.linkedin.com/learning/paths/applied-machine-learning", "Enterprise ML applications", "LinkedIn Learning", "$29.99/month")
                ]
            }
        }
        
        # Check if we have specific resources for this topic (with partial matching)
        for key, resources in resource_templates.items():
            if key in topic_lower or any(word in topic_lower for word in key.split()):
                logger.info(f"Using curated resources for {key}")
                return resources
        
        # Also check for common variations and abbreviations
        topic_mappings = {
            'llm': ['large language model', 'llms', 'language model'],
            'ai': ['artificial intelligence', 'artificial-intelligence'],
            'ml': ['machine learning', 'machine-learning'],
            'js': ['javascript'],
            'py': ['python']
        }
        
        for key, variations in topic_mappings.items():
            if key in resource_templates and (key in topic_lower or any(var in topic_lower for var in variations)):
                logger.info(f"Using curated resources for {key} (matched via variation)")
                return resource_templates[key]
        
        # Generic high-quality resources
        return self._get_generic_quality_resources(topic)
    
    def _get_generic_quality_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get generic high-quality resources for any topic"""
        return {
            'docs': [
                Resource(f"{topic} Official Documentation", f"https://www.google.com/search?q={topic}+official+documentation", f"Official {topic} documentation and guides", "Official", "Free"),
                Resource(f"{topic} on MDN", f"https://developer.mozilla.org/en-US/search?q={topic}", f"Mozilla Developer Network resources for {topic}", "MDN", "Free"),
                Resource(f"{topic} GitHub Awesome List", f"https://github.com/search?q=awesome-{topic.replace(' ', '-')}", f"Curated {topic} resources on GitHub", "GitHub", "Free")
            ],
            'blogs': [
                Resource(f"{topic} on dev.to", f"https://dev.to/t/{topic.replace(' ', '')}", f"Community articles about {topic}", "Dev.to", "Free"),
                Resource(f"{topic} Medium Articles", f"https://medium.com/search?q={topic}", f"Professional {topic} articles on Medium", "Medium", "Free"),
                Resource(f"{topic} CSS-Tricks", f"https://css-tricks.com/?s={topic}", f"Practical {topic} tutorials and tips", "CSS-Tricks", "Free")
            ],
            'youtube': [
                Resource(f"Traversy Media {topic}", f"https://www.youtube.com/c/TraversyMedia/search?query={topic}", f"Practical {topic} tutorials", "YouTube", "Free"),
                Resource(f"The Net Ninja {topic}", f"https://www.youtube.com/c/TheNetNinja/search?query={topic}", f"Step-by-step {topic} learning", "YouTube", "Free"),
                Resource(f"Programming with Mosh {topic}", f"https://www.youtube.com/c/programmingwithmosh/search?query={topic}", f"Professional {topic} tutorials", "YouTube", "Free")
            ],
            'free_courses': [
                Resource(f"{topic} on freeCodeCamp", f"https://www.freecodecamp.org/learn", f"Interactive {topic} curriculum", "freeCodeCamp", "Free"),
                Resource(f"{topic} on Coursera", f"https://www.coursera.org/search?query={topic}", f"University-level {topic} courses", "Coursera", "Free"),
                Resource(f"{topic} on edX", f"https://www.edx.org/search?q={topic}", f"Academic {topic} courses", "edX", "Free")
            ],
            'paid_courses': [
                Resource(f"Complete {topic} Course on Udemy", f"https://www.udemy.com/courses/search/?q={topic}", f"Comprehensive {topic} training", "Udemy", "$89.99"),
                Resource(f"{topic} Path on Pluralsight", f"https://www.pluralsight.com/search?q={topic}", f"Professional {topic} skill path", "Pluralsight", "$29/month"),
                Resource(f"{topic} on LinkedIn Learning", f"https://www.linkedin.com/learning/search?keywords={topic}", f"Professional {topic} training", "LinkedIn Learning", "$29.99/month")
            ]
        }
    
    def _get_basic_fallback_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Basic fallback resources when everything else fails"""
        return {
            'docs': [
                Resource(f"{topic} Documentation", f"https://www.google.com/search?q={topic}+documentation", f"Find {topic} documentation", "Web Search", "Free")
            ],
            'blogs': [
                Resource(f"{topic} Tutorials", f"https://www.google.com/search?q={topic}+tutorial", f"Find {topic} tutorials", "Web Search", "Free")
            ],
            'youtube': [
                Resource(f"{topic} Videos", f"https://www.youtube.com/results?search_query={topic}", f"Find {topic} video tutorials", "YouTube", "Free")
            ],
            'free_courses': [
                Resource(f"{topic} Free Courses", f"https://www.google.com/search?q={topic}+free+course", f"Find free {topic} courses", "Web Search", "Free")
            ],
            'paid_courses': [
                Resource(f"{topic} Paid Courses", f"https://www.udemy.com/courses/search/?q={topic}", f"Find paid {topic} courses", "Udemy", "Varies")
            ]
        }

    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("Expert AI Tutor resources cleaned up") 