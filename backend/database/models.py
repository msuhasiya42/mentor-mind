"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base
import json


class LearningPath(Base):
    """Model for storing generated learning paths."""

    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String(255), nullable=False, index=True)
    data = Column(Text, nullable=False)  # JSON string of learning path
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to user actions
    actions = relationship("UserAction", back_populates="learning_path")

    def set_data(self, data_dict):
        """Convert dict to JSON string and store."""
        self.data = json.dumps(data_dict)

    def get_data(self):
        """Parse JSON string and return dict."""
        return json.loads(self.data)

    def __repr__(self):
        return f"<LearningPath(id={self.id}, topic='{self.topic}')>"


class UserAction(Base):
    """Model for tracking user actions (downloads, views, etc.)."""

    __tablename__ = "user_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # "viewed", "downloaded_pdf", "downloaded_doc"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to learning path
    learning_path = relationship("LearningPath", back_populates="actions")

    def __repr__(self):
        return f"<UserAction(id={self.id}, type='{self.action_type}')>"
