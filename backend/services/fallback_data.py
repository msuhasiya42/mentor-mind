"""
Fallback and curated data for different topics when search engines fail
"""
from typing import List, Dict
from urllib.parse import quote
from .models import Resource


class FallbackDataProvider:
    """Provides fallback data when search engines are unavailable"""
    
    @staticmethod
    def get_documentation_sources() -> Dict[str, List[Resource]]:
        """Get predefined documentation sources for common topics"""
        return {
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
    
    @staticmethod
    def get_fallback_blogs(topic: str) -> List[Resource]:
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
    
    @staticmethod
    def get_fallback_youtube(topic: str) -> List[Resource]:
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
    
    @staticmethod
    def get_fallback_courses(topic: str, course_type: str = "free") -> List[Resource]:
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
    
    @staticmethod
    def get_curated_search_results(query: str) -> List[Dict]:
        """Return curated search results based on query keywords when all search engines fail"""
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
        
        return curated_results 