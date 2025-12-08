from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base

# Version: 1.0.1 - Fixed Python 3.13 type annotation issues
# Import all routers
from app.routes import (
    auth,
    courses,
    cart,
    wishlist,
    users,
    reviews,
    orders,
    instructor,
    payments,
    admin,
    daily_classes
)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not create tables - {e}")
    print("Make sure PostgreSQL database is created first:")
    print("  Run: python create_db.py")

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CodeMaster API - Online Learning Platform with Authentication, Courses, Cart, Orders, and Enrollment",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
from fastapi.staticfiles import StaticFiles
import os
os.makedirs("static/uploads/payment_proofs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include all routers with API version prefix
api_prefix = settings.API_V1_STR

app.include_router(auth.router, prefix=api_prefix)
app.include_router(courses.router, prefix=api_prefix)
app.include_router(cart.router, prefix=api_prefix)
app.include_router(wishlist.router, prefix=api_prefix)
app.include_router(orders.router, prefix=api_prefix)
app.include_router(reviews.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(instructor.router, prefix=api_prefix)
app.include_router(payments.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)
app.include_router(daily_classes.router, prefix=api_prefix)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CodeMaster API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "User Authentication (Register/Login)",
            "Course Management & Search",
            "Shopping Cart",
            "Wishlist",
            "Course Enrollment",
            "Order Processing",
            "Reviews & Ratings",
            "Instructor Tools",
            "Progress Tracking",
            "Admin Panel"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "postgresql",
        "version": "2.0.0"
    }

@app.get("/api-info")
def api_info():
    """API information and available endpoints"""
    return {
        "api_version": "2.0.0",
        "base_url": api_prefix,
        "endpoints": {
            "auth": f"{api_prefix}/auth",
            "courses": f"{api_prefix}/courses",
            "cart": f"{api_prefix}/cart",
            "wishlist": f"{api_prefix}/wishlist",
            "orders": f"{api_prefix}/orders",
            "reviews": f"{api_prefix}/reviews",
            "users": f"{api_prefix}/users",
            "instructor": f"{api_prefix}/instructor",
            "admin": f"{api_prefix}/admin"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )