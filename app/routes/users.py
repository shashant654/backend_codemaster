from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.models.models import User, Course
from app.schemas.schemas import UserResponse, UserUpdate
from app.core.security import get_current_user, hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    website: Optional[str] = None

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name:
        user.name = user_update.name
    if user_update.bio:
        user.bio = user_update.bio
    if user_update.avatar:
        user.avatar = user_update.avatar
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/profile/update", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile"""
    user = current_user
    
    # Only update fields that exist in the User model
    if profile_data.name is not None:
        user.name = profile_data.name
    if profile_data.email is not None:
        # Check if email already exists
        existing_user = db.query(User).filter(
            User.email == profile_data.email,
            User.id != user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = profile_data.email
    if profile_data.avatar is not None:
        user.avatar = profile_data.avatar
    if profile_data.bio is not None:
        user.bio = profile_data.bio
    
    # Note: phone, location, occupation, website are ignored as they don't exist in the User model
    # To store these fields, you would need to add them to the User model first
    
    db.commit()
    db.refresh(user)
    return user

@router.post("/password/change", status_code=status.HTTP_200_OK)
def change_password(
    password_data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change user's password"""
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@router.get("/{user_id}/enrolled-courses")
def get_enrolled_courses(user_id: int, db: Session = Depends(get_db)):
    """Get user's enrolled courses"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.enrolled_courses

@router.post("/{user_id}/enroll/{course_id}")
def enroll_course(user_id: int, course_id: int, db: Session = Depends(get_db)):
    """Enroll user in a course"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course in user.enrolled_courses:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    user.enrolled_courses.append(course)
    course.enrolled_count += 1
    db.commit()
    return {"message": "Successfully enrolled in course"}
