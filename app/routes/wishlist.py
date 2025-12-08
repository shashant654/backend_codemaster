from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.database import get_db
from app.models.models import User, Course
from app.schemas.schemas import CourseWithInstructor
from app.core.security import get_current_user

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.get("/", response_model=List[CourseWithInstructor])
def get_wishlist(
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wishlist"""
    # Re-fetch user to ensure attached to current session
    user = db.query(User).filter(User.id == current_user.id).first()
    return user.wishlist_courses

@router.post("/add/{course_id}")
def add_to_wishlist(
    course_id: int,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add course to wishlist"""
    user = db.query(User).filter(User.id == current_user.id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course in user.wishlist_courses:
        raise HTTPException(status_code=400, detail="Course already in wishlist")
    
    user.wishlist_courses.append(course)
    db.commit()
    return {"message": "Course added to wishlist"}

@router.delete("/remove/{course_id}")
def remove_from_wishlist(
    course_id: int,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove course from wishlist"""
    user = db.query(User).filter(User.id == current_user.id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course not in user.wishlist_courses:
        raise HTTPException(status_code=400, detail="Course not in wishlist")
    
    user.wishlist_courses.remove(course)
    db.commit()
    return {"message": "Course removed from wishlist"}

@router.get("/check/{course_id}")
def check_in_wishlist(
    course_id: int,
    current_user: Any = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if course is in wishlist"""
    user = db.query(User).filter(User.id == current_user.id).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    is_wishlisted = course in user.wishlist_courses
    return {"is_wishlisted": is_wishlisted}
