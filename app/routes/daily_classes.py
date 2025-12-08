from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.db.database import get_db
from app.models.models import DailyClass, Course, User
from app.core.security import get_current_user

router = APIRouter(prefix="/daily-classes", tags=["daily-classes"])

@router.get("/upcoming")
def get_upcoming_daily_classes(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Get upcoming daily classes for all enrolled courses"""
    # Get user's enrolled course IDs
    enrolled_course_ids = [course.id for course in current_user.enrolled_courses]
    
    if not enrolled_course_ids:
        return []
    
    # Get upcoming active classes for enrolled courses
    now = datetime.utcnow()
    daily_classes = db.query(DailyClass).filter(
        DailyClass.course_id.in_(enrolled_course_ids),
        DailyClass.is_active == True,
        DailyClass.scheduled_date >= now
    ).order_by(DailyClass.scheduled_date.asc()).limit(20).all()
    
    result = []
    for dc in daily_classes:
        course = db.query(Course).filter(Course.id == dc.course_id).first()
        result.append({
            "id": dc.id,
            "course_id": dc.course_id,
            "title": dc.title,
            "topic": dc.topic,
            "description": dc.description,
            "meet_link": dc.meet_link,
            "scheduled_date": dc.scheduled_date.isoformat(),
            "duration_minutes": dc.duration_minutes,
            "is_active": dc.is_active,
            "created_at": dc.created_at.isoformat(),
            "course_title": course.title if course else None
        })
    
    return result
