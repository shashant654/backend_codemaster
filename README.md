# CodeMaster Backend API

FastAPI-based backend for the CodeMaster online learning platform.

## Project Structure

```
backend/
├── app/
│   ├── core/              # Core configuration and security
│   │   ├── config.py      # Settings and configuration
│   │   └── security.py    # JWT and password utilities
│   ├── db/                # Database configuration
│   │   └── database.py    # SQLAlchemy setup
│   ├── models/            # SQLAlchemy models
│   │   └── models.py      # Database models
│   ├── routes/            # API routes
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── courses.py     # Courses endpoints
│   │   ├── cart.py        # Shopping cart endpoints
│   │   ├── wishlist.py    # Wishlist endpoints
│   │   └── users.py       # User profile endpoints
│   ├── schemas/           # Pydantic schemas
│   │   └── schemas.py     # Request/response schemas
│   └── main.py            # FastAPI application
├── requirements.txt       # Python dependencies
└── .env.example          # Environment variables template
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
```

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update variables if needed:

```bash
cp .env.example .env
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Courses
- `GET /api/v1/courses/` - Get all courses
- `GET /api/v1/courses/{course_id}` - Get course details
- `GET /api/v1/courses/category/{category}` - Get courses by category
- `GET /api/v1/courses/search/` - Search courses

### Cart
- `GET /api/v1/cart/` - Get cart items
- `POST /api/v1/cart/add` - Add to cart
- `DELETE /api/v1/cart/{cart_item_id}` - Remove from cart
- `DELETE /api/v1/cart/` - Clear cart

### Wishlist
- `GET /api/v1/wishlist/` - Get wishlist
- `POST /api/v1/wishlist/add/{course_id}` - Add to wishlist
- `DELETE /api/v1/wishlist/remove/{course_id}` - Remove from wishlist
- `POST /api/v1/wishlist/check/{course_id}` - Check if in wishlist

### Users
- `GET /api/v1/users/{user_id}` - Get user profile
- `PUT /api/v1/users/{user_id}` - Update user profile
- `GET /api/v1/users/{user_id}/enrolled-courses` - Get enrolled courses
- `POST /api/v1/users/{user_id}/enroll/{course_id}` - Enroll in course

## Database Models

- **User**: User accounts and profiles
- **Course**: Course information and metadata
- **CartItem**: Items in user shopping carts
- **Review**: Course reviews and ratings
- **Section**: Course sections/modules
- **Lecture**: Individual lectures within sections
- **Associations**: Many-to-many relationships (wishlist, enrollment)

## Features

✅ User authentication with JWT tokens
✅ Course management and browsing
✅ Shopping cart functionality
✅ Wishlist management
✅ User profiles and enrollments
✅ CORS enabled for frontend integration
✅ Comprehensive API documentation
✅ SQLite database (can be switched to PostgreSQL)

## Security

- Password hashing with bcrypt
- JWT token-based authentication
- CORS middleware configured
- Trusted host middleware
- Input validation with Pydantic

## Environment Variables

```
DATABASE_URL          # Database connection string
SECRET_KEY           # JWT secret key
ALGORITHM            # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiration time
BACKEND_CORS_ORIGINS # Allowed CORS origins
```

## Development

To add new endpoints:

1. Create a new route file in `app/routes/`
2. Define Pydantic schemas in `app/schemas/schemas.py`
3. Include the router in `app/main.py`

## Production Deployment

Before deploying to production:

1. Change `SECRET_KEY` in `.env`
2. Set `DATABASE_URL` to production database
3. Configure `BACKEND_CORS_ORIGINS` appropriately
4. Use a production ASGI server (Gunicorn + Uvicorn)
5. Enable HTTPS
6. Set up proper logging and monitoring

## License

MIT


## to check is admin created or not
cd d:\codemasterr\backend; python -c "from app.db.database import SessionLocal; from app.models.models import User; db = SessionLocal(); admins = db.query(User).filter(User.is_admin == True).all(); print('Admins found:', len(admins)); [print(f'{a.id}: {a.email} (admin={a.is_admin})') for a in admins]"


1. python create_admin.py
2. python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

3. 