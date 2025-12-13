from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Any
from app.db.database import get_db
from app.models.models import DailyClass, Course, User
from app.core.security import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/daily-classes", tags=["daily-classes"])

@router.get("/upcoming")
def get_upcoming_daily_classes(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Get all active daily classes for enrolled courses (both upcoming and past for recordings)"""
    try:
        # Re-fetch user to ensure relationships are loaded
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user:
            logger.error(f"User {current_user.id} not found in database")
            return []
        
        # Get user's enrolled course IDs
        enrolled_course_ids = [course.id for course in user.enrolled_courses]
        
        logger.info(f"User {user.id} has {len(enrolled_course_ids)} enrolled courses: {enrolled_course_ids}")
        
        if not enrolled_course_ids:
            logger.info(f"User {user.id} has no enrolled courses")
            return []
        
        # Get all active classes for enrolled courses, ordered by most recent first
        daily_classes = db.query(DailyClass).filter(
            DailyClass.course_id.in_(enrolled_course_ids),
            DailyClass.is_active == True
        ).order_by(DailyClass.scheduled_date.desc()).limit(20).all()
        
        logger.info(f"Found {len(daily_classes)} daily classes for user {user.id}")
        
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
        
    except Exception as e:
        logger.error(f"Error fetching daily classes: {e}", exc_info=True)
        return []

@router.get("/debug-auth")
def debug_daily_classes_auth(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Debug endpoint for authenticated users to see their daily classes"""
    try:
        # Re-fetch user to ensure relationships are loaded
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user:
            return {"error": "User not found", "user_id": current_user.id}
        
        # Get user's enrolled course IDs
        enrolled_course_ids = [course.id for course in user.enrolled_courses]
        
        logger.info(f"[DEBUG-AUTH] User {user.id} ({user.name}) has {len(enrolled_course_ids)} enrolled courses: {enrolled_course_ids}")
        
        if not enrolled_course_ids:
            return {
                "user_id": user.id,
                "message": "User has no enrolled courses",
                "enrolled_courses": []
            }
        
        # Get all active classes for enrolled courses
        daily_classes = db.query(DailyClass).filter(
            DailyClass.course_id.in_(enrolled_course_ids),
            DailyClass.is_active == True
        ).order_by(DailyClass.scheduled_date.desc()).all()
        
        logger.info(f"[DEBUG-AUTH] Found {len(daily_classes)} daily classes for user {user.id}")
        
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
        
        return {
            "user_id": user.id,
            "user_name": user.name,
            "enrolled_course_ids": enrolled_course_ids,
            "enrolled_courses": [{"id": c.id, "title": c.title} for c in user.enrolled_courses],
            "daily_classes_count": len(result),
            "daily_classes": result
        }
        
    except Exception as e:
        logger.error(f"[DEBUG-AUTH] Error: {e}", exc_info=True)
        return {"error": str(e), "type": type(e).__name__}

@router.get("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Daily classes route is working"}

@router.get("/debug-public")
def debug_daily_classes_public(db: Session = Depends(get_db)):
    """Public debug endpoint to check all daily classes and enrollments"""
    try:
        # Get all users
        all_users = db.query(User).all()
        
        # Get all daily classes
        all_daily_classes = db.query(DailyClass).all()
        
        # Get enrollment data
        users_data = []
        for user in all_users:
            enrolled_courses = user.enrolled_courses
            daily_classes_for_user = db.query(DailyClass).filter(
                DailyClass.course_id.in_([c.id for c in enrolled_courses]) if enrolled_courses else False,
                DailyClass.is_active == True
            ).all()
            
            users_data.append({
                "user_id": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "enrolled_courses": [
                    {"id": c.id, "title": c.title} for c in enrolled_courses
                ],
                "daily_classes_count": len(daily_classes_for_user),
                "daily_classes": [
                    {
                        "id": dc.id,
                        "title": dc.title,
                        "course_id": dc.course_id,
                        "scheduled_date": dc.scheduled_date.isoformat(),
                        "is_active": dc.is_active
                    } for dc in daily_classes_for_user
                ]
            })
        
        return {
            "total_users": len(all_users),
            "total_daily_classes": len(all_daily_classes),
            "users": users_data,
            "all_daily_classes_in_system": [
                {
                    "id": dc.id,
                    "title": dc.title,
                    "course_id": dc.course_id,
                    "scheduled_date": dc.scheduled_date.isoformat(),
                    "is_active": dc.is_active
                } for dc in all_daily_classes
            ]
        }
    except Exception as e:
        logger.error(f"Debug error: {e}", exc_info=True)
        return {"error": str(e)}

@router.get("/debug")
def debug_daily_classes(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Debug endpoint to check user enrollment and daily classes"""
    try:
        # Re-fetch user
        user = db.query(User).filter(User.id == current_user.id).first()
        
        if not user:
            return {"error": "User not found", "user_id": current_user.id}
        
        # Get enrolled courses
        enrolled_courses = user.enrolled_courses
        enrolled_course_ids = [c.id for c in enrolled_courses]
        
        # Get all daily classes for those courses
        daily_classes = db.query(DailyClass).filter(
            DailyClass.course_id.in_(enrolled_course_ids) if enrolled_course_ids else False
        ).all()
        
        # Get ALL daily classes in system
        all_daily_classes = db.query(DailyClass).all()
        
        return {
            "user_id": user.id,
            "user_name": user.name,
            "enrolled_courses": [
                {"id": c.id, "title": c.title} for c in enrolled_courses
            ],
            "enrolled_course_ids": enrolled_course_ids,
            "daily_classes_for_enrolled": [
                {
                    "id": dc.id,
                    "title": dc.title,
                    "course_id": dc.course_id,
                    "scheduled_date": dc.scheduled_date.isoformat(),
                    "is_active": dc.is_active
                } for dc in daily_classes
            ],
            "all_daily_classes": [
                {
                    "id": dc.id,
                    "title": dc.title,
                    "course_id": dc.course_id,
                    "scheduled_date": dc.scheduled_date.isoformat(),
                    "is_active": dc.is_active
                } for dc in all_daily_classes
            ]
        }
    except Exception as e:
        logger.error(f"Debug error: {e}", exc_info=True)
        return {"error": str(e)}

@router.get("/detail/{class_id}")
def get_daily_class_detail(class_id: int, db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """Get details of a specific daily class, ensuring the user is enrolled in the course.
    Returns the meet link and other class info.
    """
    # Verify the class exists
    daily_class = db.query(DailyClass).filter(DailyClass.id == class_id).first()
    if not daily_class:
        raise HTTPException(status_code=404, detail="Daily class not found")
    # Verify user is enrolled in the class's course
    if daily_class.course_id not in [c.id for c in current_user.enrolled_courses]:
        raise HTTPException(status_code=403, detail="Not authorized to view this class")
    course = db.query(Course).filter(Course.id == daily_class.course_id).first()
    return {
        "id": daily_class.id,
        "course_id": daily_class.course_id,
        "title": daily_class.title,
        "topic": daily_class.topic,
        "description": daily_class.description,
        "meet_link": daily_class.meet_link,
        "scheduled_date": daily_class.scheduled_date.isoformat(),
        "duration_minutes": daily_class.duration_minutes,
        "is_active": daily_class.is_active,
        "created_at": daily_class.created_at.isoformat(),
        "course_title": course.title if course else None,
    }
