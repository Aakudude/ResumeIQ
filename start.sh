#!/bin/bash
set -e

echo "🧠 Starting ResumeIQ..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Install backend deps
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt -q

# Start backend in background
echo "🚀 Starting FastAPI backend on port 8000..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
echo "🎨 Starting React frontend on port 5173..."
cd ../frontend
npm install --legacy-peer-deps -q
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ ResumeIQ is running!"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
