#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
echo "==================================================="
echo "              Starting Noto Workspace              "
echo "  Local-First AI Notes & Human-in-the-Loop Review  "
echo "==================================================="

# 1. Backend Setup
echo "Checking backend environment..."
cd "$DIR/backend"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

echo "Starting Backend API on http://localhost:8050..."
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload &
BACKEND_PID=$!

# 2. Frontend Setup
echo "Starting Frontend on http://localhost:5180..."
cd "$DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

# Trap Ctrl+C and exit cleanly
cleanup() {
    echo ""
    echo "Shutting down Noto servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo ""
echo "✨ Noto is running!"
echo "   - Web App: http://localhost:5180"
echo "   - API Docs: http://localhost:8050/docs"
echo "   Press Ctrl+C to stop."
echo ""

wait
