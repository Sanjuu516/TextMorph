#!/bin/bash
# TextMorph Launcher Script

echo "🚀 Starting TextMorph Services..."

# Create virtual environment if not present
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Start FastAPI backend server in background
echo "⚡ Starting FastAPI Backend Server on http://127.0.0.1:8000 ..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend initialization
sleep 3

# Start Streamlit frontend
echo "🎨 Starting Streamlit Frontend Dashboard on http://localhost:8501 ..."
streamlit run frontend/app.py --server.port 8501 &
FRONTEND_PID=$!

echo "✅ TextMorph is live!"
echo "   - Backend API: http://127.0.0.1:8000 (Swagger docs at http://127.0.0.1:8000/docs)"
echo "   - Frontend UI: http://localhost:8501"

# Trap SIGINT to stop both background processes cleanly
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
