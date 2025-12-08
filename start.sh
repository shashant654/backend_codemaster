#!/bin/bash
# Backend startup script for macOS/Linux

cd "$(dirname "$0")"

echo "🚀 Starting CodeMaster Backend with PostgreSQL"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Check PostgreSQL
echo "🔍 Checking PostgreSQL connection..."
python create_db.py > /dev/null 2>&1

# Seed database
echo "🌱 Seeding database..."
python seed_data.py > /dev/null 2>&1

# Start server
echo ""
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
