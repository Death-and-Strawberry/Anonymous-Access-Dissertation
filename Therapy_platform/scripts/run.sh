#!/bin/bash
set -e

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the application
echo "Starting Therapy platform application..."
uvicorn app.main:app --host 127.0.0.1 --port ${APP_PORT:-5000} --reload
