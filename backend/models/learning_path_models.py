from pydantic import BaseModel
from typing import List


class LearningPathRequest(BaseModel):
    topic: str


class PydanticResource(BaseModel):
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""


class PydanticLearningPath(BaseModel):
    blogs: List[PydanticResource] = []
    docs: List[PydanticResource] = []
    youtube: List[PydanticResource] = []
    free_courses: List[PydanticResource] = []
    paid_courses: List[PydanticResource] = []


class LearningPathResponse(BaseModel):
    topic: str
    learning_path: PydanticLearningPath 