from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Course, Section, Lecture, User
from app.schemas.schemas import CourseCreate, CourseUpdate, CourseResponse, SectionResponse, LectureResponse
from app.core.security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/instructor", tags=["instructor"])


def check_is_instructor(current_user: User) -> User:
    """Verify that current user is an instructor"""
    if not current_user.is_instructor:
        raise HTTPException(status_code=403, detail="Only instructors can create courses")
    return current_user


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new course"""
    check_is_instructor(current_user)
    
    # Check if slug already exists
    existing_course = db.query(Course).filter(Course.slug == course_data.slug).first()
    if existing_course:
        raise HTTPException(status_code=400, detail="Course slug already exists")
    
    db_course = Course(
        **course_data.dict(),
        instructor_id=current_user.id,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/courses", response_model=list[CourseResponse])
def get_instructor_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all courses created by the current instructor"""
    check_is_instructor(current_user)
    
    courses = db.query(Course).filter(
        Course.instructor_id == current_user.id
    ).all()
    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_instructor_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific course created by the current instructor"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a course (only by the course instructor)"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update fields
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a course (only by the course instructor)"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(course)
    db.commit()
    return None


@router.post("/courses/{course_id}/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(
    course_id: int,
    section_data: dict,  # title, description, order
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new section for a course"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_section = Section(
        course_id=course_id,
        title=section_data.get("title"),
        description=section_data.get("description"),
        order=section_data.get("order", 0),
    )
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section


@router.delete("/courses/{course_id}/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(
    course_id: int,
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a section from a course"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    section = db.query(Section).filter(
        Section.id == section_id,
        Section.course_id == course_id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    db.delete(section)
    db.commit()
    return None


@router.post("/courses/{course_id}/sections/{section_id}/lectures", response_model=LectureResponse, status_code=status.HTTP_201_CREATED)
def create_lecture(
    course_id: int,
    section_id: int,
    lecture_data: dict,  # title, description, video_url, duration, order, is_preview
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new lecture in a section"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    section = db.query(Section).filter(
        Section.id == section_id,
        Section.course_id == course_id
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    db_lecture = Lecture(
        section_id=section_id,
        title=lecture_data.get("title"),
        description=lecture_data.get("description"),
        video_url=lecture_data.get("video_url"),
        duration=lecture_data.get("duration", "0:00"),
        order=lecture_data.get("order", 0),
        is_preview=lecture_data.get("is_preview", False),
    )
    db.add(db_lecture)
    db.commit()
    db.refresh(db_lecture)
    return db_lecture


@router.delete("/courses/{course_id}/sections/{section_id}/lectures/{lecture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lecture(
    course_id: int,
    section_id: int,
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a lecture from a section"""
    check_is_instructor(current_user)
    
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    lecture = db.query(Lecture).filter(
        Lecture.id == lecture_id,
        Lecture.section_id == section_id
    ).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    db.delete(lecture)
    db.commit()
    return None
