"""
Resource Curator - Manual curation of high-quality learning resources
"""
import logging
from typing import Dict, List
from .learning_path_generator import Resource

logger = logging.getLogger(__name__)


class ResourceCurator:
    """Handles manual curation of learning resources for popular topics"""
    
    def __init__(self):
        self.resource_templates = self._initialize_resource_templates()
        logger.info("Resource Curator initialized")
    
    def get_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get manually curated resources for a topic"""
        topic_lower = topic.lower()
        
        # Check if we have specific resources for this topic
        for key, resources in self.resource_templates.items():
            if key in topic_lower:
                logger.info(f"Using curated resources for {key}")
                return resources
        
        # Generic high-quality resources
        return self._get_generic_quality_resources(topic)
    
    def get_basic_fallback_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get basic fallback resources when everything else fails"""
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
    
    def _initialize_resource_templates(self) -> Dict[str, Dict[str, List[Resource]]]:
        """Initialize predefined resource templates for popular topics"""
        return {
            'react': {
                'docs': [
                    Resource("React Official Documentation", "https://react.dev", "Official React documentation with hooks and modern practices", "Official", "Free"),
                    Resource("React Patterns", "https://reactpatterns.com", "Common React patterns and best practices", "Web", "Free")
                ],
                'blogs': [
                    Resource("Overreacted by Dan Abramov", "https://overreacted.io", "Deep insights into React by its core maintainer", "Blog", "Free"),
                    Resource("React Blog on dev.to", "https://dev.to/t/react", "Community articles about React development", "Dev.to", "Free")
                ],
                'youtube': [
                    Resource("React Official Channel", "https://www.youtube.com/@ReactJS", "Official React team videos and conferences", "YouTube", "Free"),
                    Resource("Traversy Media React Playlist", "https://www.youtube.com/playlist?list=PLillGF-RfqbY3c2r0htQyVbDJJoBFE6Rb", "Comprehensive React tutorials", "YouTube", "Free")
                ],
                'free_courses': [
                    Resource("React Course on freeCodeCamp", "https://www.freecodecamp.org/learn/front-end-libraries/react/", "Interactive React curriculum", "freeCodeCamp", "Free"),
                    Resource("React Basics on Codecademy", "https://www.codecademy.com/learn/react-101", "Interactive React fundamentals", "Codecademy", "Free")
                ],
                'paid_courses': [
                    Resource("Complete React Developer Course", "https://www.udemy.com/course/react-redux/", "Comprehensive React and Redux course", "Udemy", "$89.99"),
                    Resource("React Path on Pluralsight", "https://www.pluralsight.com/paths/react", "Professional React skill path", "Pluralsight", "$29/month")
                ]
            }
        }
    
    def _get_generic_quality_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get generic high-quality resources for any topic"""
        return {
            'docs': [
                Resource(f"{topic} Official Documentation", f"https://www.google.com/search?q={topic}+official+documentation", f"Official {topic} documentation and guides", "Official", "Free")
            ],
            'blogs': [
                Resource(f"{topic} on dev.to", f"https://dev.to/t/{topic.replace(' ', '')}", f"Community articles about {topic}", "Dev.to", "Free")
            ],
            'youtube': [
                Resource(f"Traversy Media {topic}", f"https://www.youtube.com/c/TraversyMedia/search?query={topic}", f"Practical {topic} tutorials", "YouTube", "Free")
            ],
            'free_courses': [
                Resource(f"{topic} on freeCodeCamp", f"https://www.freecodecamp.org/learn", f"Interactive {topic} curriculum", "freeCodeCamp", "Free")
            ],
            'paid_courses': [
                Resource(f"Complete {topic} Course on Udemy", f"https://www.udemy.com/courses/search/?q={topic}", f"Comprehensive {topic} training", "Udemy", "$89.99")
            ]
        } 