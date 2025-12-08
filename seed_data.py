"""
Script to seed initial data into the database
Run: python seed_data.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.database import Base
from app.models.models import User, Course, Section, Lecture
from app.core.security import get_password_hash
from datetime import datetime

# Create engine using the configured DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():
    """Seed database with initial data"""
    db = SessionLocal()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if data already exists
    if db.query(User).count() > 0:
        print("Database already has data. Skipping seed.")
        db.close()
        return
    
    # Create sample users
    users = [
        User(
            name="John Doe",
            email="john@example.com",
            hashed_password=get_password_hash("password123"),
            is_instructor=True,
            bio="Experienced Python developer and instructor",
            avatar="https://api.example.com/avatars/john.jpg"
        ),
        User(
            name="Jane Smith",
            email="jane@example.com",
            hashed_password=get_password_hash("password123"),
            is_instructor=True,
            bio="Full-stack web developer",
            avatar="https://api.example.com/avatars/jane.jpg"
        ),
        User(
            name="Student User",
            email="student@example.com",
            hashed_password=get_password_hash("password123"),
            is_instructor=False,
            bio="Eager to learn",
        ),
    ]
    
    db.add_all(users)
    db.commit()
    
    # Create sample courses
    courses = [
        Course(
            title="Python for Beginners",
            slug="python-beginners",
            description="Learn Python programming from scratch",
            short_description="Complete Python course for beginners",
            thumbnail="https://api.example.com/images/python.jpg",
            price=49.99,
            original_price=99.99,
            duration="40 hours",
            lecture_count=50,
            level="Beginner",
            category="Programming",
            language="English",
            certificate=True,
            is_bestseller=True,
            is_trending=True,
            is_new=False,
            instructor_id=1,
            rating=4.8,
            review_count=234,
            enrolled_count=1500
        ),
        Course(
            title="Advanced JavaScript",
            slug="advanced-javascript",
            description="Master JavaScript for modern web development",
            short_description="Advanced JavaScript concepts and techniques",
            thumbnail="https://api.example.com/images/js.jpg",
            price=59.99,
            original_price=119.99,
            duration="50 hours",
            lecture_count=60,
            level="Advanced",
            category="Web Development",
            language="English",
            certificate=True,
            is_bestseller=False,
            is_trending=True,
            is_new=True,
            instructor_id=1,
            rating=4.9,
            review_count=189,
            enrolled_count=892
        ),
        Course(
            title="React and Redux",
            slug="react-redux",
            description="Build modern web applications with React",
            short_description="Complete React and Redux course",
            thumbnail="https://api.example.com/images/react.jpg",
            price=69.99,
            duration="45 hours",
            lecture_count=55,
            level="Intermediate",
            category="Web Development",
            language="English",
            certificate=True,
            is_bestseller=True,
            is_trending=False,
            is_new=False,
            instructor_id=2,
            rating=4.7,
            review_count=156,
            enrolled_count=1200
        ),
    ]
    
    db.add_all(courses)
    db.commit()
    
    # Create sample sections and lectures
    sections_data = [
        {
            "course_id": 1,
            "title": "Getting Started",
            "order": 1,
            "lectures": [
                {"title": "Welcome to Python", "duration": "10:32", "order": 1},
                {"title": "Installation and Setup", "duration": "15:45", "order": 2},
                {"title": "Your First Program", "duration": "12:20", "order": 3},
            ]
        },
        {
            "course_id": 1,
            "title": "Data Types and Variables",
            "order": 2,
            "lectures": [
                {"title": "Understanding Variables", "duration": "18:30", "order": 1},
                {"title": "Integers and Floats", "duration": "22:15", "order": 2},
                {"title": "Strings", "duration": "25:40", "order": 3},
            ]
        },
    ]
    
    for section_data in sections_data:
        section = Section(
            course_id=section_data["course_id"],
            title=section_data["title"],
            order=section_data["order"]
        )
        db.add(section)
        db.flush()
        
        for lecture_data in section_data["lectures"]:
            lecture = Lecture(
                section_id=section.id,
                title=lecture_data["title"],
                duration=lecture_data["duration"],
                order=lecture_data["order"],
                is_preview=(lecture_data["order"] == 1)  # First lecture is preview
            )
            db.add(lecture)
    
    db.commit()
    
    print("✅ Database seeded successfully!")
    print(f"   - Created {len(users)} users")
    print(f"   - Created {len(courses)} courses")
    print(f"   - Created {len(sections_data)} sections with lectures")
    print("\nTest credentials:")
    print("   Email: john@example.com")
    print("   Password: password123")
    
    db.close()

if __name__ == "__main__":
    seed_database()
