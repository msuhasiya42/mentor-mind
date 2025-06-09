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
        logger.info("🔍 INITIALIZING AI RESPONSE PARSER")
        logger.info("✅ AI Response Parser initialized successfully")
    
    def parse_json_response(self, generated_text: str, topic: str) -> Dict[str, List[Resource]]:
        """Parse JSON response from LLM into categorized Resource objects"""
        logger.info("🔬 Parsing AI response")
        
        try:
            # Clean the response text - remove any markdown or extra formatting
            cleaned_text = self._clean_response_text(generated_text)
            
            # Try to parse as JSON
            data = json.loads(cleaned_text)
            
            # Convert to Resource objects
            result = self._convert_to_resources(data, topic)
            
            if result:
                total_resources = sum(len(resources) for resources in result.values())
                logger.info(f"✅ Parsed {total_resources} AI resources")
                return result
            else:
                logger.warning("❌ No resources extracted from parsed data")
                return {}
            
        except json.JSONDecodeError:
            logger.warning("❌ JSON parsing failed, trying fallback extraction")
            fallback_result = self._extract_json_from_text(generated_text, topic)
            if fallback_result:
                total_resources = sum(len(resources) for resources in fallback_result.values())
                logger.info(f"✅ Fallback extraction: {total_resources} resources")
                return fallback_result
            else:
                logger.error("❌ All parsing methods failed")
                return {}
                
        except Exception as e:
            logger.error(f"💥 Parsing error: {str(e)}")
            return {}
    
    def _clean_response_text(self, text: str) -> str:
        """Clean response text to extract pure JSON"""
        logger.debug("🧹 Cleaning response text")
        original_length = len(text)
        text = text.strip()
        
        # Track cleaning operations
        cleaning_operations = []
        
        # Remove common markdown formatting
        if text.startswith('```json'):
            text = text[7:]
            cleaning_operations.append("Removed '```json' prefix")
        if text.startswith('```'):
            text = text[3:]
            cleaning_operations.append("Removed '```' prefix")
        if text.endswith('```'):
            text = text[:-3]
            cleaning_operations.append("Removed '```' suffix")
        
        # Find JSON boundaries
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start != -1 and json_end != -1 and json_end > json_start:
            original_text_length = len(text)
            text = text[json_start:json_end + 1]
            if len(text) != original_text_length:
                cleaning_operations.append(f"Extracted JSON boundaries ({json_start}:{json_end+1})")
        
        cleaned_text = text.strip()
        
        logger.debug(f"   Original length: {original_length}")
        logger.debug(f"   Cleaned length: {len(cleaned_text)}")
        if cleaning_operations:
            logger.debug(f"   Operations: {', '.join(cleaning_operations)}")
        else:
            logger.debug("   No cleaning needed")
        
        return cleaned_text
    
    def _convert_to_resources(self, data: Dict, topic: str) -> Dict[str, List[Resource]]:
        """Convert parsed JSON data to Resource objects"""
        if not isinstance(data, dict):
            logger.error(f"Expected dict, got {type(data).__name__}")
            return {}
        
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
        
        total_resources = sum(len(resources) for resources in categories.values())
        logger.debug(f"Converted {total_resources} resources across {len([c for c in categories.values() if c])} categories")
        
        return categories
    
    def _create_resource_from_dict(self, resource_dict: Dict, topic: str) -> Resource:
        """Create Resource object from dictionary"""
        logger.debug(f"🔨 Creating resource from dict")
        
        try:
            title = resource_dict.get('title', '').strip()
            if not title:
                logger.debug("   ❌ Missing or empty title")
                return None
            
            url = resource_dict.get('url', '').strip()
            if not url:
                url = f"https://www.google.com/search?q={title.replace(' ', '+')}"
                logger.debug("   ⚠️ Missing URL, generated search URL")
            
            description = resource_dict.get('description', '').strip()
            if not description:
                description = f"Learn {topic} with {title}"
                logger.debug("   ⚠️ Missing description, generated default")
            
            platform = resource_dict.get('platform', '').strip()
            if not platform:
                platform = "Web"
                logger.debug("   ⚠️ Missing platform, set to 'Web'")
            
            price = resource_dict.get('price', '').strip()
            if not price:
                price = "Free"
                logger.debug("   ⚠️ Missing price, set to 'Free'")
            
            resource = Resource(
                title=title,
                url=url,
                description=description,
                platform=platform,
                price=price
            )
            
            logger.debug(f"   ✅ Resource created: '{title}' on {platform}")
            return resource
            
        except Exception as e:
            logger.error(f"   💥 Error creating resource: {str(e)}")
            logger.error(f"   Resource data: {resource_dict}")
            return None
    
    def _extract_json_from_text(self, text: str, topic: str) -> Dict[str, List[Resource]]:
        """Fallback: try to extract JSON from malformed text"""
        logger.warning("🔧 FALLBACK: Attempting JSON extraction from malformed text")
        logger.warning(f"   Text length: {len(text)} characters")
        
        try:
            # Look for JSON-like patterns in the text
            import re
            
            # Find JSON object boundaries
            json_pattern = r'\{.*\}'
            matches = re.findall(json_pattern, text, re.DOTALL)
            
            logger.info(f"   Found {len(matches)} potential JSON matches")
            
            for i, match in enumerate(matches):
                logger.debug(f"   Trying match {i+1}/{len(matches)} (length: {len(match)})")
                try:
                    data = json.loads(match)
                    logger.info(f"     ✅ Match {i+1}: Valid JSON found")
                    
                    result = self._convert_to_resources(data, topic)
                    if result and any(result.values()):
                        total_extracted = sum(len(resources) for resources in result.values())
                        logger.info("✅ FALLBACK JSON EXTRACTION SUCCESSFUL")
                        logger.info(f"   Extracted {total_extracted} resources from malformed text")
                        logger.info("   🔧 SOURCE CONFIRMED: AI-generated (via fallback extraction)")
                        return result
                    else:
                        logger.debug(f"     ❌ Match {i+1}: Valid JSON but no resources extracted")
                        
                except json.JSONDecodeError as e:
                    logger.debug(f"     ❌ Match {i+1}: Invalid JSON - {str(e)}")
                    continue
            
            logger.error("❌ FALLBACK EXTRACTION FAILED")
            logger.error("   Could not extract valid JSON with resources from response")
            return {}
            
        except Exception as e:
            logger.error("💥 FALLBACK EXTRACTION ERROR")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            return {} 