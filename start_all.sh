#!/bin/bash
# Quick Start Script for Jamii Connect
# Run this to start all services at once

echo "=========================================="
echo "Jamii Connect - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Check if Node is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check if PostgreSQL is running
echo "📊 Checking PostgreSQL connection..."
python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='huduma_connect',
        user='postgres',
        password='3698'
    )
    print('✓ PostgreSQL connected')
    conn.close()
except:
    print('❌ PostgreSQL not accessible. Make sure it is running.')
    exit(1)
" || exit 1

# Check if Redis is running
echo "📊 Checking Redis connection..."
python -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 6379))
if result == 0:
    print('✓ Redis connected')
else:
    print('⚠ Redis not accessible. USSD sessions won\'t work.')
sock.close()
"

echo ""
echo "=========================================="
echo "Installation Check"
echo "=========================================="

# Install backend dependencies if needed
if [ ! -d "app/venv" ]; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Install frontend dependencies if needed
if [ ! -d "admin-dashboard/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd admin-dashboard && npm install && cd ..
fi

echo ""
echo "=========================================="
echo "Starting Services"
echo "=========================================="
echo ""
echo "Note: Press Ctrl+C to stop all services"
echo ""

# Function to kill all background processes on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill %1 2>/dev/null
    kill %2 2>/dev/null
    echo "✓ All services stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo "🚀 Starting Backend (http://localhost:8000)"
echo "   API Docs: http://localhost:8000/docs"
echo ""
cd app && uvicorn main:app --reload &
BACKEND_PID=$!
sleep 2

# Start frontend
echo "🚀 Starting Frontend (http://localhost:5173)"
echo ""
cd ../admin-dashboard && npm run dev &
FRONTEND_PID=$!
sleep 2

echo ""
echo "=========================================="
echo "Services Ready!"
echo "=========================================="
echo ""
echo "Backend: http://localhost:8000"
echo "Dashboard: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Wait for both processes
wait
