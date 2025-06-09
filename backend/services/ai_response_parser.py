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
        logger.info("🔬 AI RESPONSE PARSING: Starting JSON analysis")
        logger.info(f"   Topic: '{topic}'")
        logger.info(f"   Raw response length: {len(generated_text)} characters")
        logger.debug(f"   First 200 chars: {generated_text[:200]}...")
        
        try:
            # Clean the response text - remove any markdown or extra formatting
            logger.info("🧹 Cleaning response text")
            cleaned_text = self._clean_response_text(generated_text)
            logger.info(f"   Cleaned text length: {len(cleaned_text)} characters")
            
            if len(cleaned_text) != len(generated_text):
                logger.info("   ✂️ Text was cleaned (removed formatting)")
            else:
                logger.info("   ✅ Text was already clean")
            
            # Try to parse as JSON
            logger.info("📊 Attempting JSON parsing")
            data = json.loads(cleaned_text)
            logger.info("✅ JSON parsing successful")
            logger.info(f"   Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Convert to Resource objects
            logger.info("🔄 Converting parsed data to Resource objects")
            result = self._convert_to_resources(data, topic)
            
            if result:
                total_resources = sum(len(resources) for resources in result.values())
                logger.info("✅ AI RESPONSE PARSING COMPLETED SUCCESSFULLY")
                logger.info(f"   Successfully parsed: {total_resources} resources")
                logger.info("   🤖 SOURCE CONFIRMED: AI-generated resources")
                return result
            else:
                logger.warning("❌ No resources extracted from parsed data")
                return {}
            
        except json.JSONDecodeError as e:
            logger.warning("❌ JSON PARSING FAILED")
            logger.warning(f"   JSON Error: {str(e)}")
            logger.warning(f"   Error position: {getattr(e, 'pos', 'unknown')}")
            logger.warning("   🔄 Attempting fallback JSON extraction")
            
            # Try to extract JSON from text if it's embedded
            fallback_result = self._extract_json_from_text(generated_text, topic)
            if fallback_result:
                logger.info("✅ Fallback JSON extraction successful")
                return fallback_result
            else:
                logger.error("❌ Fallback JSON extraction also failed")
                return {}
                
        except Exception as e:
            logger.error("💥 AI RESPONSE PARSING ERROR")
            logger.error(f"   Topic: '{topic}'")
            logger.error(f"   Error type: {type(e).__name__}")
            logger.error(f"   Error message: {str(e)}")
            logger.error("   Response text preview:", exc_info=True)
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
        logger.info("🔄 CONVERTING JSON DATA TO RESOURCES")
        logger.info(f"   Input data type: {type(data).__name__}")
        
        if not isinstance(data, dict):
            logger.error(f"   ❌ Expected dict, got {type(data).__name__}")
            return {}
        
        categories = {
            'docs': [],
            'blogs': [],
            'youtube': [],
            'free_courses': [],
            'paid_courses': []
        }
        
        logger.info(f"   Processing {len(data)} categories from AI response")
        
        for category, resources in data.items():
            logger.debug(f"   Processing category: '{category}'")
            
            if category in categories:
                if isinstance(resources, list):
                    logger.debug(f"     Found {len(resources)} items in '{category}'")
                    
                    for i, resource_data in enumerate(resources):
                        if isinstance(resource_data, dict):
                            resource = self._create_resource_from_dict(resource_data, topic)
                            if resource:
                                categories[category].append(resource)
                                logger.debug(f"       ✅ Resource {i+1}: '{resource.title}'")
                            else:
                                logger.debug(f"       ❌ Resource {i+1}: Failed to create")
                        else:
                            logger.debug(f"       ❌ Resource {i+1}: Not a dict (type: {type(resource_data).__name__})")
                else:
                    logger.warning(f"     ❌ Category '{category}' is not a list (type: {type(resources).__name__})")
            else:
                logger.debug(f"     ⚠️ Unknown category: '{category}' (ignored)")
        
        # Log the results
        total_resources = sum(len(resources) for resources in categories.values())
        logger.info("✅ RESOURCE CONVERSION COMPLETED")
        logger.info(f"   Conversion summary:")
        for category, resources in categories.items():
            logger.info(f"     - {category}: {len(resources)} resources")
        logger.info(f"   Total resources converted: {total_resources}")
        
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