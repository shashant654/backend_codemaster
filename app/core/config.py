from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/fast_api_course"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CodeMaster API"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8081"]
    
    # Razorpay
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # Email
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str = "shashantshekhar10@gmail.com"
    EMAIL_HOST_PASSWORD: str = "rkwl thar ysvn vzgj"
    DEFAULT_FROM_EMAIL: str = "Code Learn <shashantshekhar10@gmail.com>"
    
    class Config:
        env_file = ".env"

settings = Settings()
