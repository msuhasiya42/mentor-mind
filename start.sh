#!/bin/bash

# Mentor Mind Startup Script
echo "🧠 Starting Mentor Mind..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Function to install backend dependencies
install_backend() {
    echo "📦 Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
}

# Function to install frontend dependencies
install_frontend() {
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
}

# Function to start backend
start_backend() {
    echo "🚀 Starting backend server..."
    cd backend
    python main.py &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🚀 Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if dependencies need to be installed
if [ "$1" = "--install" ] || [ ! -d "backend/__pycache__" ] || [ ! -d "frontend/node_modules" ]; then
    install_backend
    install_frontend
fi

# Start servers
start_backend
sleep 3  # Give backend time to start
start_frontend

echo ""
echo "✅ Mentor Mind is running!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to stop
wait 