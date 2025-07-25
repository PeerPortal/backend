#!/bin/bash

# Full-Stack Application Startup Script
# This script starts both the backend API and serves the frontend

echo "🏗️  Starting Full-Stack Application"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "complete_app.py" ]; then
    echo "❌ Error: complete_app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if frontend is built
if [ ! -d "frontend/build" ]; then
    echo "📦 Frontend not built. Building now..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "📥 Installing frontend dependencies..."
        npm install
    fi
    echo "🔨 Building frontend..."
    npm run build
    cd ..
    echo "✅ Frontend built successfully!"
else
    echo "✅ Frontend build found!"
fi

echo ""
echo "🚀 Starting integrated server..."
echo "📡 Backend API: http://localhost:8000/api/"
echo "🌐 Frontend: http://localhost:8000/"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "============================================"
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo ""

# Start the server
uvicorn complete_app:app --host 0.0.0.0 --port 8000 --reload
