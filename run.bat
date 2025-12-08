@echo off
echo Starting CodeMaster Backend with PostgreSQL...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show fastapi > nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed.
    echo.
)

REM Create database
echo Setting up PostgreSQL database...
python create_db.py > nul 2>&1

REM Seed database
echo Seeding database...
python seed_data.py > nul 2>&1

REM Run the application
echo Starting FastAPI server...
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
