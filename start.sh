#!/usr/bin/env bash
# start.sh — kill anything on :8765 and :8766, then start API + Web from scratch.
#   API → http://127.0.0.1:8765   (FastAPI / uvicorn,  log: .logs/api.log)
#   Web → http://127.0.0.1:8766   (Vite dev server,    log: .logs/web.log)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
mkdir -p .logs

kill_port() {
  local pids
  pids=$(lsof -nP -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null || true)
  [[ -n "${pids:-}" ]] || return 0
  # shellcheck disable=SC2086
  kill $pids 2>/dev/null || true
  sleep 0.3
  pids=$(lsof -nP -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null || true)
  # shellcheck disable=SC2086
  [[ -n "${pids:-}" ]] && kill -9 $pids 2>/dev/null || true
}

kill_port 8765
kill_port 8766

(
  cd "$ROOT/app"
  # shellcheck disable=SC1091
  source api/.venv/bin/activate
  exec python -m uvicorn api.main:app --host 127.0.0.1 --port 8765 --reload
) >.logs/api.log 2>&1 &
API_PID=$!

(
  cd "$ROOT/app/web"
  exec npm run dev -- --port 8766 --strictPort
) >.logs/web.log 2>&1 &
WEB_PID=$!

echo "API  pid=$API_PID  → http://127.0.0.1:8765   (.logs/api.log)"
echo "Web  pid=$WEB_PID  → http://127.0.0.1:8766   (.logs/web.log)"
