from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_instructor: bool
    is_admin: bool = False
    avatar: Optional[str]
    bio: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Course Schemas
class LectureBase(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    duration: str
    order: int
    is_preview: bool = False

class LectureResponse(LectureBase):
    id: int
    section_id: int
    
    class Config:
        from_attributes = True

class SectionBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int

class SectionResponse(SectionBase):
    id: int
    course_id: int
    lectures: List[LectureResponse] = []
    
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    slug: str
    description: str
    short_description: str
    thumbnail: str
    price: float
    original_price: Optional[float] = None
    duration: str
    lecture_count: int
    level: str
    category: str

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    level: Optional[str] = None

class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    rating: float
    review_count: int
    enrolled_count: int
    is_bestseller: bool
    is_trending: bool
    is_new: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CourseDetailResponse(CourseResponse):
    instructor: UserResponse
    sections: List[SectionResponse] = []

# Cart Schemas
class CourseWithInstructor(CourseResponse):
    instructor: UserResponse
    
    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    course_id: int

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    course: CourseWithInstructor
    added_at: datetime
    
    class Config:
        from_attributes = True

# Review Schemas
class ReviewBase(BaseModel):
    rating: int
    comment: str

class ReviewCreate(ReviewBase):
    course_id: int

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: int
    course_id: int
    user_id: int
    user: UserResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

# Enrollment Schemas
class EnrollmentResponse(BaseModel):
    course_id: int
    course: CourseResponse
    enrolled_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderItemResponse(BaseModel):
    id: int
    course_id: int
    course: Optional['CourseResponse'] = None
    price: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    course_ids: Optional[list[int]] = None
    payment_method: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    payment_method: Optional[str]
    order_items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
