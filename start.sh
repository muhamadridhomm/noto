#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
echo "==================================================="
echo "              Starting Noto Workspace              "
echo "  Local-First AI Notes & ClickUp-Style Checklist   "
echo "==================================================="

DEV_MODE=false
OPEN_DESKTOP=false

for arg in "$@"; do
    if [ "$arg" == "--dev" ] || [ "$arg" == "--next" ] || [ "$arg" == "--react" ]; then
        DEV_MODE=true
    elif [ "$arg" == "--desktop" ]; then
        OPEN_DESKTOP=true
    fi
done

# 1. Backend Setup
echo "Checking backend environment..."
cd "$DIR/backend"
if [ ! -d "venv" ] || [ ! -f "venv/bin/uvicorn" ]; then
    echo "Creating Python virtual environment..."
    rm -rf venv
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

if [ "$DEV_MODE" = true ]; then
    # DEVELOPMENT MODE: Vite HMR (5180) + FastAPI reload (8050)
    echo "⚡ Running in DEVELOPMENT mode (Hot Module Replacement)..."

    echo "Starting Backend API on http://localhost:8050..."
    ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8050 --reload &
    BACKEND_PID=$!

    echo "Starting Frontend Dev Server on http://localhost:5180..."
    cd "$DIR/frontend"
    if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/vite" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!

    cleanup() {
        echo ""
        echo "Shutting down Noto dev servers..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        exit 0
    }
    trap cleanup INT TERM

    echo ""
    echo "✨ Noto Dev Server is running!"
    echo "   - Web App (Vite): http://localhost:5180"
    echo "   - API Docs:       http://localhost:8050/docs"
    echo "   Press Ctrl+C to stop."
    echo ""

    if [ "$OPEN_DESKTOP" = true ]; then
        sleep 1
        bash "$DIR/desktop/noto-launcher.sh" &
    fi
    wait
else
    # PRODUCTION / DESKTOP MODE: 100% Zero-NPM Unified Server
    echo "🚀 Running in UNIFIED mode (Zero NPM / No Node.js required)..."

    # Ensure frontend build exists
    if [ ! -d "$DIR/frontend/dist" ]; then
        echo "Building frontend production bundle once..."
        cd "$DIR/frontend"
        npm run build
        cd "$DIR/backend"
    fi

    if [ "$OPEN_DESKTOP" = true ]; then
        # Launch directly into desktop window with auto start/stop
        exec bash "$DIR/desktop/noto-launcher.sh"
    else
        echo "Starting Unified Noto App on http://localhost:8050..."
        ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8050 &
        BACKEND_PID=$!

        cleanup() {
            echo ""
            echo "Shutting down Noto server..."
            kill $BACKEND_PID 2>/dev/null || true
            exit 0
        }
        trap cleanup INT TERM

        echo ""
        echo "✨ Noto Workspace is running!"
        echo "   - Web App & API: http://localhost:8050"
        echo "   - API Docs:      http://localhost:8050/docs"
        echo "   Press Ctrl+C to stop."
        echo ""
        wait
    fi
fi
