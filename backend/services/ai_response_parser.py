"""
AI Response Parser - Simplified JSON parsing for LLM responses
"""
import json
import logging
from typing import Dict, List
from .learning_path_generator import Resource

logger = logging.getLogger(__name__)


class AIResponseParser:
    """Handles parsing of AI responses in JSON format"""
    
    def __init__(self):
        logger.info("AI Response Parser initialized")
    
    def parse_json_response(self, generated_text: str, topic: str) -> Dict[str, List[Resource]]:
        """Parse JSON response from LLM into categorized Resource objects"""
        try:
            # Clean the response text - remove any markdown or extra formatting
            cleaned_text = self._clean_response_text(generated_text)
            
            # Try to parse as JSON
            data = json.loads(cleaned_text)
            
            # Convert to Resource objects
            return self._convert_to_resources(data, topic)
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            # Try to extract JSON from text if it's embedded
            return self._extract_json_from_text(generated_text, topic)
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return {}
    
    def _clean_response_text(self, text: str) -> str:
        """Clean response text to extract pure JSON"""
        text = text.strip()
        
        # Remove common markdown formatting
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        # Find JSON boundaries
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            text = text[json_start:json_end + 1]
        
        return text.strip()
    
    def _convert_to_resources(self, data: Dict, topic: str) -> Dict[str, List[Resource]]:
        """Convert parsed JSON data to Resource objects"""
        categories = {
            'docs': [],
            'blogs': [],
            'youtube': [],
            'free_courses': [],
            'paid_courses': []
        }
        
        for category, resources in data.items():
            if category in categories and isinstance(resources, list):
                for resource_data in resources:
                    if isinstance(resource_data, dict):
                        resource = self._create_resource_from_dict(resource_data, topic)
                        if resource:
                            categories[category].append(resource)
        
        # Log the results
        total_resources = sum(len(resources) for resources in categories.values())
        logger.info(f"Successfully parsed {total_resources} resources from AI response")
        
        return categories
    
    def _create_resource_from_dict(self, resource_dict: Dict, topic: str) -> Resource:
        """Create Resource object from dictionary"""
        try:
            title = resource_dict.get('title', '').strip()
            if not title:
                return None
            
            url = resource_dict.get('url', '').strip()
            if not url:
                url = f"https://www.google.com/search?q={title.replace(' ', '+')}"
            
            description = resource_dict.get('description', '').strip()
            if not description:
                description = f"Learn {topic} with {title}"
            
            platform = resource_dict.get('platform', '').strip()
            if not platform:
                platform = "Web"
            
            price = resource_dict.get('price', '').strip()
            if not price:
                price = "Free"
            
            return Resource(
                title=title,
                url=url,
                description=description,
                platform=platform,
                price=price
            )
        except Exception as e:
            logger.error(f"Error creating resource from dict: {str(e)}")
            return None
    
    def _extract_json_from_text(self, text: str, topic: str) -> Dict[str, List[Resource]]:
        """Fallback: try to extract JSON from malformed text"""
        try:
            # Look for JSON-like patterns in the text
            import re
            
            # Find JSON object boundaries
            json_pattern = r'\{.*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    result = self._convert_to_resources(data, topic)
                    if result and any(result.values()):
                        logger.info("Successfully extracted JSON from malformed text")
                        return result
                except json.JSONDecodeError:
                    continue
            
            logger.warning("Could not extract valid JSON from response")
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting JSON from text: {str(e)}")
            return {} 