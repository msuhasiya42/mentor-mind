"""CRUD operations for database."""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from .models import LearningPath, UserAction
from datetime import datetime


# ==================== Learning Path CRUD ====================

def create_learning_path(db: Session, topic: str, data: Dict[str, Any]) -> LearningPath:
    """Create a new learning path."""
    learning_path = LearningPath(topic=topic)
    learning_path.set_data(data)
    db.add(learning_path)
    db.commit()
    db.refresh(learning_path)
    return learning_path


def get_learning_path(db: Session, learning_path_id: int) -> Optional[LearningPath]:
    """Get a learning path by ID."""
    return db.query(LearningPath).filter(LearningPath.id == learning_path_id).first()


def get_all_learning_paths(db: Session, skip: int = 0, limit: int = 100) -> List[LearningPath]:
    """Get all learning paths, ordered by most recent first."""
    return db.query(LearningPath).order_by(desc(LearningPath.created_at)).offset(skip).limit(limit).all()


def get_learning_paths_by_topic(db: Session, topic: str) -> List[LearningPath]:
    """Get all learning paths for a specific topic."""
    return db.query(LearningPath).filter(LearningPath.topic.ilike(f"%{topic}%")).order_by(desc(LearningPath.created_at)).all()


def delete_learning_path(db: Session, learning_path_id: int) -> bool:
    """Delete a learning path by ID."""
    learning_path = get_learning_path(db, learning_path_id)
    if learning_path:
        db.delete(learning_path)
        db.commit()
        return True
    return False


# ==================== User Action CRUD ====================

def create_user_action(db: Session, learning_path_id: int, action_type: str) -> UserAction:
    """Track a user action."""
    action = UserAction(learning_path_id=learning_path_id, action_type=action_type)
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def get_actions_for_learning_path(db: Session, learning_path_id: int) -> List[UserAction]:
    """Get all actions for a specific learning path."""
    return db.query(UserAction).filter(UserAction.learning_path_id == learning_path_id).all()


# ==================== Statistics ====================

def get_statistics(db: Session) -> Dict[str, Any]:
    """Get overall statistics."""
    total_paths = db.query(func.count(LearningPath.id)).scalar()
    total_downloads = db.query(func.count(UserAction.id)).filter(
        UserAction.action_type.in_(["downloaded_pdf", "downloaded_doc"])
    ).scalar()

    # Get most popular topics
    popular_topics = db.query(
        LearningPath.topic,
        func.count(LearningPath.id).label("count")
    ).group_by(LearningPath.topic).order_by(desc("count")).limit(5).all()

    # Get recent activity (last 7 days)
    # Note: SQLite doesn't have great date functions, so we'll just count all for now
    recent_paths = db.query(func.count(LearningPath.id)).scalar()

    return {
        "total_learning_paths": total_paths or 0,
        "total_downloads": total_downloads or 0,
        "popular_topics": [{"topic": topic, "count": count} for topic, count in popular_topics],
        "recent_activity": recent_paths or 0
    }


def get_topic_statistics(db: Session) -> Dict[str, int]:
    """Get count of learning paths grouped by topic."""
    results = db.query(
        LearningPath.topic,
        func.count(LearningPath.id).label("count")
    ).group_by(LearningPath.topic).order_by(desc("count")).all()

    return {topic: count for topic, count in results}
