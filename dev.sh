#!/bin/bash
# dev.sh — start scaffold-ai locally
# Backend: http://localhost:8001
# Frontend: http://localhost:3000
#
# When running alongside project-planner-ai (via its dev.sh),
# scaffold-ai uses port 8001 (backend) and 3001 (frontend).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Backend
cd apps/backend
if [[ ! -d ".venv" ]]; then
  echo "📦  Installing backend dependencies..."
  uv sync
fi
DEPLOYMENT_TIER=testing AWS_REGION=us-east-1 uv run uvicorn scaffold_ai.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Frontend
cd apps/web
if [[ ! -d "node_modules" ]]; then
  echo "📦  Installing frontend dependencies..."
  pnpm install
fi
VITE_BACKEND_URL=http://localhost:8001 pnpm dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

cleanup() {
  echo ""
  echo "🛑  Stopping..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  wait 2>/dev/null
  echo "👋  Done"
}
trap cleanup EXIT INT TERM

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🏗️   Scaffold AI — local dev"
echo ""
echo "  Backend   →  http://localhost:8001"
echo "  Frontend  →  http://localhost:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop"
echo ""

wait
