"""
Result Saver Service - Automatically saves AI-generated learning paths
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from .learning_path_generator import Resource, LearningPath

logger = logging.getLogger(__name__)


class ResultSaver:
    """Handles automatic saving of AI-generated learning paths to results directory"""
    
    def __init__(self):
        logger.info("💾 INITIALIZING RESULT SAVER")
        
        self.results_dir = "results"
        self._ensure_results_directory()
        
        logger.info("✅ Result Saver initialized successfully")
        logger.info(f"   Results directory: {os.path.abspath(self.results_dir)}")
    
    def _ensure_results_directory(self):
        """Ensure the results directory exists"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            logger.info(f"📁 Created results directory: {self.results_dir}")
        else:
            logger.debug(f"📁 Results directory exists: {self.results_dir}")
    
    def save_ai_generated_result(self, topic: str, learning_path: LearningPath, source: str) -> bool:
        """
        Save AI-generated learning path result to JSON file
        
        Args:
            topic: The search topic
            learning_path: The generated learning path
            source: The source of the result (used to determine if it should be saved)
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        logger.info("💾 Evaluating result for saving")
        
        # Only save AI-generated results (not fallback)
        if not self._should_save_result(source):
            logger.info("⏭️ Skipping save: Not from AI source")
            return False
        
        try:
            # Generate filename
            filename = self._generate_filename(topic)
            filepath = os.path.join(self.results_dir, filename)
            
            logger.info(f"💾 Saving AI result: {filename}")
            
            # Convert learning path to JSON format
            result_data = self._convert_to_json_format(topic, learning_path)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=4, ensure_ascii=False)
            
            # Log success with statistics
            total_resources = sum(len(getattr(learning_path, category)) for category in ['docs', 'blogs', 'youtube', 'free_courses'])
            file_size = os.path.getsize(filepath)
            
            logger.info(f"✅ Saved: {total_resources} resources, {file_size} bytes")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Save failed: {str(e)}")
            return False
    
    def _should_save_result(self, source: str) -> bool:
        """
        Determine if a result should be saved based on its source
        
        Args:
            source: The source identifier string
            
        Returns:
            bool: True if the result should be saved
        """
        ai_indicators = [
            "AI TUTOR",
            "DeepSeek",
            "OpenRouter", 
            "AI-generated",
            "🤖"
        ]
        
        fallback_indicators = [
            "MANUAL CURATION",
            "BASIC FALLBACK", 
            "Fallback",
            "📋",
            "🔄"
        ]
        
        source_lower = source.lower()
        
        # Check for AI indicators
        has_ai_indicator = any(indicator.lower() in source_lower for indicator in ai_indicators)
        
        # Check for fallback indicators
        has_fallback_indicator = any(indicator.lower() in source_lower for indicator in fallback_indicators)
        
        # Save if it has AI indicators and no fallback indicators
        should_save = has_ai_indicator and not has_fallback_indicator
        
        logger.debug(f"   Source analysis:")
        logger.debug(f"     - Has AI indicator: {has_ai_indicator}")
        logger.debug(f"     - Has fallback indicator: {has_fallback_indicator}")
        logger.debug(f"     - Should save: {should_save}")
        
        return should_save
    
    def _generate_filename(self, topic: str) -> str:
        """
        Generate filename in format: {search_keyword}_res_{current_date}.json
        Crops search keyword to 15 characters if longer
        
        Args:
            topic: The search topic
            
        Returns:
            str: Generated filename
        """
        # Clean and normalize the topic
        cleaned_topic = self._clean_topic_for_filename(topic)
        
        # Crop to 15 characters if longer
        if len(cleaned_topic) > 15:
            cropped_topic = cleaned_topic[:15]
            logger.info(f"   Topic cropped: '{cleaned_topic}' -> '{cropped_topic}'")
        else:
            cropped_topic = cleaned_topic
        
        # Get current date in format: day_month
        current_date = datetime.now().strftime("%d_%B").lower()
        
        # Generate filename
        filename = f"{cropped_topic}_res_{current_date}.json"
        
        logger.debug(f"   Filename generation:")
        logger.debug(f"     - Original topic: '{topic}'")
        logger.debug(f"     - Cleaned topic: '{cleaned_topic}'")
        logger.debug(f"     - Final topic: '{cropped_topic}'")
        logger.debug(f"     - Date: '{current_date}'")
        logger.debug(f"     - Filename: '{filename}'")
        
        return filename
    
    def _clean_topic_for_filename(self, topic: str) -> str:
        """
        Clean topic to be safe for filename
        
        Args:
            topic: The original topic
            
        Returns:
            str: Cleaned topic safe for filename
        """
        import re
        
        # Convert to lowercase
        cleaned = topic.lower().strip()
        
        # Replace spaces and special characters with underscores
        cleaned = re.sub(r'[^\w\s-]', '', cleaned)  # Remove special chars except spaces and hyphens
        cleaned = re.sub(r'[\s-]+', '_', cleaned)   # Replace spaces and hyphens with underscores
        cleaned = re.sub(r'_+', '_', cleaned)       # Replace multiple underscores with single
        cleaned = cleaned.strip('_')                # Remove leading/trailing underscores
        
        return cleaned
    
    def _convert_to_json_format(self, topic: str, learning_path: LearningPath) -> Dict[str, Any]:
        """
        Convert learning path to JSON format matching existing files
        
        Args:
            topic: The search topic
            learning_path: The learning path object
            
        Returns:
            dict: JSON-serializable dictionary
        """
        logger.debug("🔄 Converting learning path to JSON format")
        
        def resources_to_dict_list(resources: List[Resource]) -> List[Dict[str, str]]:
            """Convert list of Resource objects to list of dictionaries"""
            return [
                {
                    "title": resource.title,
                    "url": resource.url,
                    "description": resource.description,
                    "platform": resource.platform,
                    "price": resource.price
                }
                for resource in resources
            ]
        
        # Convert all resource categories
        result_data = {
            "topic": topic,
            "learning_path": {
                "docs": resources_to_dict_list(learning_path.docs),
                "blogs": resources_to_dict_list(learning_path.blogs),
                "youtube": resources_to_dict_list(learning_path.youtube),
                "free_courses": resources_to_dict_list(learning_path.free_courses)
            }
        }
        
        # Log conversion summary
        total_resources = sum(len(category) for category in result_data["learning_path"].values())
        logger.debug(f"   Conversion summary:")
        for category, resources in result_data["learning_path"].items():
            logger.debug(f"     - {category}: {len(resources)} resources")
        logger.debug(f"   Total resources: {total_resources}")
        
        return result_data
    
    def list_saved_results(self) -> List[str]:
        """
        List all saved result files
        
        Returns:
            List of filenames in the results directory
        """
        try:
            if not os.path.exists(self.results_dir):
                return []
            
            files = [f for f in os.listdir(self.results_dir) if f.endswith('.json')]
            files.sort(reverse=True)  # Most recent first
            
            logger.info(f"📋 Found {len(files)} saved result files")
            return files
            
        except Exception as e:
            logger.error(f"❌ Error listing saved results: {str(e)}")
            return []
    
    def get_save_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about saved results
        
        Returns:
            Dictionary with save statistics
        """
        try:
            files = self.list_saved_results()
            total_size = 0
            
            for filename in files:
                filepath = os.path.join(self.results_dir, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
            
            stats = {
                "total_files": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "recent_files": files[:5]  # Most recent 5 files
            }
            
            logger.info(f"📊 Save statistics: {stats['total_files']} files, {stats['total_size_mb']} MB")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting save statistics: {str(e)}")
            return {"error": str(e)} 