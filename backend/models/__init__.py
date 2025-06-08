from .learning_path_models import (
    LearningPathRequest,
    LearningPathResponse,
    PydanticResource,
    PydanticLearningPath
)

# Import dataclass models from services
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.learning_path_generator import Resource, LearningPath, SearchResult

__all__ = [
    "LearningPathRequest",
    "LearningPathResponse",
    "PydanticResource",
    "PydanticLearningPath",
    "Resource", 
    "LearningPath",
    "SearchResult"
] 