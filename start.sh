#!/bin/bash

# Café OS - Railway Startup Script

set -e

echo "🚀 Starting Café OS..."

# Navigate to backend
cd backend

# Install dependencies
echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Load demo data
echo "☕ Loading demo café data..."
python init_demo_data.py

# Start the server
echo "🌐 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
