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
        logger.info("📚 INITIALIZING RESOURCE CURATOR")
        
        self.resource_templates = self._initialize_resource_templates()
        
        logger.info("   Manual curation templates loaded:")
        logger.info(f"     - Available topics: {len(self.resource_templates)}")
        for topic in self.resource_templates.keys():
            logger.info(f"       * {topic}")
        
        logger.info("✅ Resource Curator initialized successfully")
    
    def get_curated_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get manually curated resources for a topic"""
        logger.info("📋 MANUAL CURATION: Searching for curated resources")
        logger.info(f"   Topic: '{topic}'")
        
        topic_lower = topic.lower()
        logger.debug(f"   Normalized topic: '{topic_lower}'")
        
        # Check if we have specific resources for this topic
        matched_key = None
        for key, resources in self.resource_templates.items():
            if key in topic_lower:
                matched_key = key
                logger.info(f"✅ MANUAL CURATION MATCH FOUND")
                logger.info(f"   Matched template: '{key}'")
                logger.info(f"   Original topic: '{topic}'")
                
                # Log detailed breakdown
                total_curated = sum(len(res_list) for res_list in resources.values())
                logger.info(f"   Curated resources summary:")
                for category, res_list in resources.items():
                    logger.info(f"     - {category}: {len(res_list)} resources")
                logger.info(f"   Total curated resources: {total_curated}")
                
                return resources
        
        # Generic high-quality resources
        logger.info("❌ NO SPECIFIC CURATION FOUND")
        logger.info(f"   No template found for topic: '{topic}'")
        logger.info("   🔄 Using generic quality resources")
        
        generic_resources = self._get_generic_quality_resources(topic)
        total_generic = sum(len(res_list) for res_list in generic_resources.values())
        
        logger.info("✅ Generic quality resources generated")
        logger.info(f"   Total generic resources: {total_generic}")
        
        return generic_resources
    
    def get_basic_fallback_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get basic fallback resources when everything else fails"""
        logger.warning("🆘 BASIC FALLBACK: Generating emergency resources")
        logger.warning(f"   Topic: '{topic}'")
        logger.warning("   This is the last resort fallback method")
        
        basic_resources = {
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
        
        total_basic = sum(len(res_list) for res_list in basic_resources.values())
        logger.warning(f"✅ Basic fallback resources generated: {total_basic} resources")
        logger.warning("   These are generic search links, not curated content")
        
        return basic_resources
    
    def _initialize_resource_templates(self) -> Dict[str, Dict[str, List[Resource]]]:
        """Initialize predefined resource templates for popular topics"""
        logger.info("🔧 Initializing manual curation templates")
        
        templates = {
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
        
        logger.info(f"   Loaded {len(templates)} manual curation templates")
        for topic, resources in templates.items():
            total_resources = sum(len(res_list) for res_list in resources.values())
            logger.info(f"     - {topic}: {total_resources} resources across {len(resources)} categories")
        
        return templates
    
    def _get_generic_quality_resources(self, topic: str) -> Dict[str, List[Resource]]:
        """Get generic high-quality resources for any topic"""
        logger.info("🌐 GENERATING GENERIC QUALITY RESOURCES")
        logger.info(f"   Topic: '{topic}'")
        logger.info("   Using high-quality generic platforms")
        
        generic_resources = {
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
        
        total_generic = sum(len(res_list) for res_list in generic_resources.values())
        logger.info(f"✅ Generic quality resources generated: {total_generic} resources")
        logger.info("   These are high-quality generic platforms with topic-specific searches")
        
        return generic_resources 