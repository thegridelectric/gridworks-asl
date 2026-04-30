# syntax=docker/dockerfile:1.7
# sema-explorer — single-port image for Control Plane.
#
# uvicorn binds :$PORT (default 8765) and serves:
#   /api/*           — FastAPI handlers (registry CRUD + auth proxy)
#   /, /assets/*, …  — built Vite SPA, with SPA-fallback for client-side routes
#
# The runtime resolves the SPA dist via SEMA_SPA_DIST (default /app/web/dist)
# and the rulebook via SEMA_RULEBOOK_PATH (default /app/effortless-rulebook/effortless-rulebook.json).

# ---------- 1) Build the React SPA ----------
FROM node:20-alpine AS web-build
WORKDIR /src
COPY app/web/package*.json ./
RUN npm install
COPY app/web/ ./
RUN npm run build

# ---------- 2) Python runtime ----------
FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8765 \
    SEMA_SPA_DIST=/app/web/dist \
    SEMA_RULEBOOK_PATH=/app/effortless-rulebook/effortless-rulebook.json

COPY app/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/api/                /app/api/
COPY rulebook-emitters/      /app/rulebook-emitters/
COPY effortless-rulebook/    /app/effortless-rulebook/
COPY --from=web-build /src/dist/ /app/web/dist/

EXPOSE 8765
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
