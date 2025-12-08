#!/bin/bash

echo "Starting CodeMaster Backend API..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "Virtual environment created."
    echo
fi

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
pip show fastapi > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Dependencies installed."
    echo
fi

# Run the application
echo "Starting FastAPI server..."
echo
echo "API Documentation: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
