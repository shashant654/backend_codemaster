from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

# Association table for many-to-many relationship between users and courses (wishlist)
wishlist_association = Table(
    'wishlist',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('course_id', Integer, ForeignKey('course.id', ondelete='CASCADE'))
)

# Association table for many-to-many relationship between users and courses (enrolled)
enrollment_association = Table(
    'enrollment',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id', ondelete='CASCADE')),
    Column('course_id', Integer, ForeignKey('course.id', ondelete='CASCADE')),
    Column('enrolled_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    avatar = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_instructor = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses_created = relationship("Course", back_populates="instructor")
    wishlist_courses = relationship("Course", secondary=wishlist_association, back_populates="wishlisted_by")
    enrolled_courses = relationship("Course", secondary=enrollment_association, back_populates="enrolled_users")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "course"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    short_description = Column(String)
    thumbnail = Column(String)
    preview_video = Column(String, nullable=True)
    price = Column(Float)
    original_price = Column(Float, nullable=True)
    rating = Column(Float, default=0)
    review_count = Column(Integer, default=0)
    enrolled_count = Column(Integer, default=0)
    duration = Column(String)
    lecture_count = Column(Integer, default=0)
    level = Column(String)  # Beginner, Intermediate, Advanced
    category = Column(String, index=True)
    language = Column(String, default="English")
    certificate = Column(Boolean, default=True)
    is_bestseller = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    instructor_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = relationship("User", back_populates="courses_created")
    wishlisted_by = relationship("User", secondary=wishlist_association, back_populates="wishlist_courses")
    enrolled_users = relationship("User", secondary=enrollment_association, back_populates="enrolled_courses")
    cart_items = relationship("CartItem", back_populates="course", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="course", cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="course", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_item"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete='CASCADE'))
    course_id = Column(Integer, ForeignKey("course.id", ondelete='CASCADE'))
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    course = relationship("Course", back_populates="cart_items")

class Review(Base):
    __tablename__ = "review"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id", ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey("user.id", ondelete='CASCADE'))
    rating = Column(Integer)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class Section(Base):
    __tablename__ = "section"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id", ondelete='CASCADE'))
    title = Column(String)
    description = Column(Text, nullable=True)
    order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="sections")
    lectures = relationship("Lecture", back_populates="section", cascade="all, delete-orphan")

class Lecture(Base):
    __tablename__ = "lecture"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("section.id", ondelete='CASCADE'))
    title = Column(String)
    description = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    duration = Column(String)
    order = Column(Integer)
    is_preview = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    section = relationship("Section", back_populates="lectures")

class Order(Base):
    __tablename__ = "order"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete='CASCADE'))
    total_price = Column(Float)
    status = Column(String, default="pending")  # pending, completed, cancelled
    payment_method = Column(String, nullable=True)
    payment_proof = Column(String, nullable=True) # URL/Path to uploaded screenshot
    transaction_id = Column(String, nullable=True) # UTR or Transaction ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_item"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id", ondelete='CASCADE'))
    course_id = Column(Integer, ForeignKey("course.id", ondelete='CASCADE'))
    price = Column(Float)  # Price at time of purchase
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    course = relationship("Course", back_populates="order_items")

class PaymentMethod(Base):
    __tablename__ = "payment_method"
    
    id = Column(Integer, primary_key=True, index=True)
    method_id = Column(String, unique=True, index=True) # e.g., 'upi', 'card'
    name = Column(String)
    description = Column(String)
    icon = Column(String)
    is_active = Column(Boolean, default=True)
    settings = Column(Text, nullable=True) # JSON string for extra settings like merchant_upi_id
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyClass(Base):
    __tablename__ = "daily_class"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id", ondelete='CASCADE'))
    title = Column(String)
    topic = Column(String)
    description = Column(Text, nullable=True)
    meet_link = Column(String)
    scheduled_date = Column(DateTime)
    duration_minutes = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", backref="daily_classes")
