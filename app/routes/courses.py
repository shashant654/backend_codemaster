from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from typing import List, Any
from app.db.database import get_db
from app.models.models import Course, User, DailyClass
from app.schemas.schemas import CourseResponse, CourseDetailResponse
from datetime import datetime
from app.core.security import get_current_admin
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    level: str = Form(...),
    category: str = Form(...),
    short_description: str = Form(...),
    duration: str = Form(...),
    lecture_count: int = Form(0),
    thumbnail: UploadFile = File(...),
    preview_video: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_admin)
):
    """Create a new course (Admin only)"""
    # 1. Handle File Uploads
    UPLOAD_DIR = Path("static/uploads/courses")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Thumbnail
    thumb_ext = os.path.splitext(thumbnail.filename)[1]
    thumb_filename = f"thumb_{title.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}{thumb_ext}"
    thumb_path = UPLOAD_DIR / thumb_filename
    
    with open(thumb_path, "wb") as buffer:
        shutil.copyfileobj(thumbnail.file, buffer)
        
    thumbnail_url = f"/static/uploads/courses/{thumb_filename}"
    
    # Preview Video
    preview_url = None
    if preview_video:
        vid_ext = os.path.splitext(preview_video.filename)[1]
        vid_filename = f"preview_{title.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}{vid_ext}"
        vid_path = UPLOAD_DIR / vid_filename
        
        with open(vid_path, "wb") as buffer:
            shutil.copyfileobj(preview_video.file, buffer)
            
        preview_url = f"/static/uploads/courses/{vid_filename}"
        
    # 2. Create Course Record
    # Generate simple slug
    slug = title.lower().replace(" ", "-")
    # Check if slug exists
    if db.query(Course).filter(Course.slug == slug).first():
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    new_course = Course(
        title=title,
        description=description,
        short_description=short_description,
        price=price,
        level=level,
        category=category,
        duration=duration,
        lecture_count=lecture_count,
        thumbnail=thumbnail_url,
        preview_video=preview_url,
        slug=slug,
        instructor_id=current_user.id # Admin is the instructor for now
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course

@router.get("/", response_model=List[CourseResponse])
def get_all_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all courses with pagination"""
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get course details by ID"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/category/{category}", response_model=List[CourseResponse])
def get_courses_by_category(category: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get courses by category"""
    courses = db.query(Course).filter(Course.category == category).offset(skip).limit(limit).all()
    return courses

@router.get("/search/", response_model=List[CourseResponse])
def search_courses(q: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Search courses by title or description"""
    courses = db.query(Course).filter(
        (Course.title.ilike(f"%{q}%")) | (Course.description.ilike(f"%{q}%"))
    ).offset(skip).limit(limit).all()
    return courses

@router.get("/slug/{slug}", response_model=CourseDetailResponse)
def get_course_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get course details by slug"""
    course = db.query(Course).filter(Course.slug == slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/{course_id}/daily-classes")
def get_course_daily_classes(course_id: int, db: Session = Depends(get_db)):
    """Get active daily classes for a course (visible to enrolled users)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    daily_classes = db.query(DailyClass).filter(
        DailyClass.course_id == course_id,
        DailyClass.is_active == True
    ).order_by(DailyClass.scheduled_date.asc()).all()
    
    result = []
    for dc in daily_classes:
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
            "course_title": course.title
        })
    return result
