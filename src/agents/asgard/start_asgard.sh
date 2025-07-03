#!/bin/sh
set -e

# Get script directory (sh compatible)
SCRIPT_DIR=$(dirname "$0")
SCRIPT_DIR=$(cd "$SCRIPT_DIR" && pwd)
PROJECT_ROOT="/media/starscream/wheeljack1/projects/casper"
export PYTHONPATH="$PROJECT_ROOT"

cleanup() {
    [ -n "$MCP_PID" ] && kill $MCP_PID 2>/dev/null || true
    [ -n "$API_PID" ] && kill $API_PID 2>/dev/null || true
}
trap cleanup INT TERM EXIT

# Kill existing processes
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start MCP server on port 8000
cd "$PROJECT_ROOT"
python3 "$SCRIPT_DIR/mcp_server.py" &
MCP_PID=$!

# Wait for server
i=1
while [ $i -le 10 ]; do
    if curl -s "http://localhost:8000/mcp" >/dev/null 2>&1; then
        echo "MCP server ready"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "MCP server failed to start"
        exit 1
    fi
    sleep 1
    i=$((i + 1))
done

# Start API on port 8001
PORT=8001 python3 -m src.agents.asgard.api &
API_PID=$!

echo "Asgard ready:"
echo "  MCP: http://localhost:8000"
echo "  API: http://localhost:8001"
wait
