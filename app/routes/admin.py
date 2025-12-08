from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Course, Order, DailyClass
from app.core.security import get_current_admin, verify_password, create_access_token
from app.core.config import settings
from app.schemas.schemas import UserLogin, TokenResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    is_instructor: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_users: int
    total_courses: int
    total_orders: int
    total_revenue: float

@router.post("/login", response_model=TokenResponse)
def admin_login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Admin Login"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all users (Admin only)"""
    users = db.query(User).all()
    return users

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get system status (Admin only)"""
    total_users = db.query(User).count()
    total_courses = db.query(Course).count()
    total_orders = db.query(Order).count()
    
    # Calculate revenue
    orders = db.query(Order).filter(Order.status == "completed").all()
    total_revenue = sum(order.total_price for order in orders)
    
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_orders": total_orders,
        "total_revenue": total_revenue
    }

class OrderVerification(BaseModel):
    action: str # "approve" or "reject"

@router.get("/orders")
def get_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all orders with user details (Admin only)"""
    # Join with User to get user details efficiently if needed, or rely on lazy loading if configured
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return orders

from app.core.email import send_order_status_email

@router.post("/orders/{order_id}/verify")
def verify_order(
    order_id: int,
    verification: OrderVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Verify manual payment order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.status != "pending_verification":
        raise HTTPException(status_code=400, detail="Order is not pending verification")
        
    user = db.query(User).filter(User.id == order.user_id).first()
        
    if verification.action == "approve":
        order.status = "completed"
        # Enroll user in courses
        for item in order.order_items:
            course = db.query(Course).filter(Course.id == item.course_id).first()
            if course and course not in user.enrolled_courses:
                user.enrolled_courses.append(course)
                course.enrolled_count += 1
                
        # Send Email
        send_order_status_email(user.email, order.id, "completed")
        
    elif verification.action == "reject":
        order.status = "cancelled"
        # Send Email
        send_order_status_email(user.email, order.id, "cancelled")
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    db.commit()
    return {"message": f"Order {verification.action}d successfully"}

# Course Management Endpoints for Admin

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = None
    level: Optional[str] = None
    category: Optional[str] = None
    duration: Optional[str] = None
    lecture_count: Optional[int] = None
    is_published: Optional[bool] = None
    
    class Config:
        from_attributes = True

@router.put("/courses/{course_id}")
def admin_update_course(
    course_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    level: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    lecture_count: Optional[int] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    preview_video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update a course (Admin only - no instructor restriction)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update text fields
    if title:
        course.title = title
    if description:
        course.description = description
    if short_description:
        course.short_description = short_description
    if price is not None:
        course.price = price
    if level:
        course.level = level
    if category:
        course.category = category
    if duration:
        course.duration = duration
    if lecture_count is not None:
        course.lecture_count = lecture_count
    
    # Handle file uploads
    UPLOAD_DIR = Path("static/uploads/courses")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    if thumbnail:
        thumb_ext = os.path.splitext(thumbnail.filename)[1]
        thumb_filename = f"thumb_{title or course.title}_{int(datetime.utcnow().timestamp())}{thumb_ext}"
        thumb_path = UPLOAD_DIR / thumb_filename
        
        with open(thumb_path, "wb") as buffer:
            shutil.copyfileobj(thumbnail.file, buffer)
            
        course.thumbnail = f"/static/uploads/courses/{thumb_filename}"
    
    if preview_video:
        vid_ext = os.path.splitext(preview_video.filename)[1]
        vid_filename = f"preview_{title or course.title}_{int(datetime.utcnow().timestamp())}{vid_ext}"
        vid_path = UPLOAD_DIR / vid_filename
        
        with open(vid_path, "wb") as buffer:
            shutil.copyfileobj(preview_video.file, buffer)
            
        course.preview_video = f"/static/uploads/courses/{vid_filename}"
    
    course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(course)
    return course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a course (Admin only - no instructor restriction)"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return None

# Daily Class Management

class DailyClassCreate(BaseModel):
    course_id: int
    title: str
    topic: str
    description: Optional[str] = None
    meet_link: str
    scheduled_date: datetime
    duration_minutes: int = 60

class DailyClassUpdate(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    description: Optional[str] = None
    meet_link: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class DailyClassResponse(BaseModel):
    id: int
    course_id: int
    title: str
    topic: str
    description: Optional[str]
    meet_link: str
    scheduled_date: datetime
    duration_minutes: int
    is_active: bool
    created_at: datetime
    course_title: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.post("/daily-classes", response_model=DailyClassResponse)
def create_daily_class(
    daily_class: DailyClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Create a new daily class (Admin only)"""
    course = db.query(Course).filter(Course.id == daily_class.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_daily_class = DailyClass(
        course_id=daily_class.course_id,
        title=daily_class.title,
        topic=daily_class.topic,
        description=daily_class.description,
        meet_link=daily_class.meet_link,
        scheduled_date=daily_class.scheduled_date,
        duration_minutes=daily_class.duration_minutes
    )
    db.add(db_daily_class)
    db.commit()
    db.refresh(db_daily_class)
    
    return {
        **db_daily_class.__dict__,
        "course_title": course.title
    }

@router.get("/daily-classes", response_model=List[DailyClassResponse])
def get_all_daily_classes(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all daily classes (Admin only)"""
    query = db.query(DailyClass)
    if course_id:
        query = query.filter(DailyClass.course_id == course_id)
    
    daily_classes = query.order_by(DailyClass.scheduled_date.desc()).all()
    
    result = []
    for dc in daily_classes:
        course = db.query(Course).filter(Course.id == dc.course_id).first()
        result.append({
            **dc.__dict__,
            "course_title": course.title if course else None
        })
    return result

@router.get("/daily-classes/{daily_class_id}", response_model=DailyClassResponse)
def get_daily_class(
    daily_class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get a specific daily class (Admin only)"""
    daily_class = db.query(DailyClass).filter(DailyClass.id == daily_class_id).first()
    if not daily_class:
        raise HTTPException(status_code=404, detail="Daily class not found")
    
    course = db.query(Course).filter(Course.id == daily_class.course_id).first()
    return {
        **daily_class.__dict__,
        "course_title": course.title if course else None
    }

@router.put("/daily-classes/{daily_class_id}", response_model=DailyClassResponse)
def update_daily_class(
    daily_class_id: int,
    update_data: DailyClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update a daily class (Admin only)"""
    daily_class = db.query(DailyClass).filter(DailyClass.id == daily_class_id).first()
    if not daily_class:
        raise HTTPException(status_code=404, detail="Daily class not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(daily_class, key, value)
    
    daily_class.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(daily_class)
    
    course = db.query(Course).filter(Course.id == daily_class.course_id).first()
    return {
        **daily_class.__dict__,
        "course_title": course.title if course else None
    }

@router.delete("/daily-classes/{daily_class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daily_class(
    daily_class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a daily class (Admin only)"""
    daily_class = db.query(DailyClass).filter(DailyClass.id == daily_class_id).first()
    if not daily_class:
        raise HTTPException(status_code=404, detail="Daily class not found")
    
    db.delete(daily_class)
    db.commit()
    return None
