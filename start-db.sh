#!/usr/bin/env bash
# start-db.sh — bring up the sema Postgres in Docker (idempotent).
#   Container : sema-pg  (postgres:16)
#   Host port : 5433  → maps to container 5432
#   Conn      : postgresql://postgres@localhost:5433/sema   (matches app/api/.env)
#
# Why 5433 and not 5432? A native Homebrew Postgres often already listens on
# 5432; binding 5433 sidesteps the conflict so both can coexist.
#
# Usage:
#   ./start-db.sh            # start container; init schema if the DB is empty
#   ./start-db.sh --no-init  # start container only, never run init-db.sh
#   ./start-db.sh --reinit   # start container and re-run init-db.sh unconditionally

set -euo pipefail

NAME=sema-pg
PORT=5433
IMAGE=postgres:16
CONN="postgresql://postgres@localhost:${PORT}/sema"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"

if ! docker info >/dev/null 2>&1; then
  echo "✗ Docker isn't running. Start Docker Desktop, then re-run."; exit 1
fi

# --- ensure the container exists and is running --------------------------------
if docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "• $NAME already running on :$PORT"
elif docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "• Starting existing container $NAME ..."
  docker start "$NAME" >/dev/null
else
  echo "• Creating container $NAME on :$PORT ..."
  docker run -d --name "$NAME" \
    -e POSTGRES_DB=sema \
    -e POSTGRES_HOST_AUTH_METHOD=trust \
    -p "${PORT}:5432" \
    "$IMAGE" >/dev/null
fi

# --- wait until Postgres accepts connections -----------------------------------
printf "• Waiting for Postgres to be ready"
until docker exec "$NAME" pg_isready -U postgres -d sema >/dev/null 2>&1; do
  printf "."; sleep 1
done
echo " ready."

# --- initialize schema ---------------------------------------------------------
schema_present() {
  psql "$CONN" -tAc "SELECT to_regclass('public.owners');" 2>/dev/null | grep -q owners
}

if [[ "$MODE" == "--no-init" ]]; then
  echo "• Skipping schema init (--no-init)."
elif [[ "$MODE" == "--reinit" ]]; then
  echo "• Re-initializing schema (--reinit) ..."
  "$ROOT/postgres/init-db.sh" "$CONN"
elif schema_present; then
  echo "• Schema already present — skipping init (use --reinit to rebuild)."
else
  echo "• Empty database — running postgres/init-db.sh ..."
  "$ROOT/postgres/init-db.sh" "$CONN"
fi

echo
echo "✓ DB ready → $CONN"
echo "  (app/api/.env already points SEMA_DATABASE_URL here.)"
