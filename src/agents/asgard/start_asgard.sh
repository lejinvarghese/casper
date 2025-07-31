#!/bin/sh
set -e

# Get script directory (sh compatible)
SCRIPT_DIR=$(dirname "$0")
SCRIPT_DIR=$(cd "$SCRIPT_DIR" && pwd)
PROJECT_ROOT="/media/starscream/wheeljack1/projects/casper"
export PYTHONPATH="$PROJECT_ROOT"

echo "🚀 Starting Asgard System..."
echo "================================"

cleanup() {
    echo -e "\n🛑 Shutting down Asgard..."
    [ -n "$MCP_PID" ] && kill $MCP_PID 2>/dev/null || true
    [ -n "$API_PID" ] && kill $API_PID 2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ All services stopped"
}
trap cleanup INT TERM EXIT

# Kill existing processes on all ports
echo "🧹 Cleaning up existing processes..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8001 | xargs kill -9 2>/dev/null || true  
lsof -ti :5173 | xargs kill -9 2>/dev/null || true
sleep 1

# Start MCP server on port 8000
echo "🔧 Starting MCP server..."
cd "$PROJECT_ROOT"
python3 "$SCRIPT_DIR/mcp_server.py" &
MCP_PID=$!

# Wait for MCP server
i=1
while [ $i -le 10 ]; do
    if curl -s "http://localhost:8000/mcp" >/dev/null 2>&1; then
        echo "✅ MCP server ready"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ MCP server failed to start"
        exit 1
    fi
    sleep 1
    i=$((i + 1))
done

# Start API on port 8001
echo "🌐 Starting API server..."
PORT=8001 python3 -m src.agents.asgard.api &
API_PID=$!

# Wait for API server
echo "⏳ Waiting for API server..."
sleep 3

# Start frontend on port 5173 (Vite default)
echo "🎨 Starting frontend..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Asgard System Ready!"
echo "================================"
echo "🔧 MCP Server:  http://localhost:8000"
echo "🌐 API Server:  http://localhost:8001" 
echo "🎨 Frontend:    http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"
echo "================================"

wait
