# =============================================================================
# Stage 1: Build the frontend (Vite + Tailwind) static assets
#
# We use a separate Node stage only to run "npm run build". The final
# production image (stage 4) does NOT contain Node at all — only the
# already-built files are copied over. This keeps the production image
# smaller and avoids shipping a JS toolchain we don't need at runtime.
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy only the dependency manifests first. Docker caches each layer, so as
# long as package.json/package-lock.json don't change, "npm ci" is skipped
# on rebuilds even if we change frontend source files afterwards.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# tailwind.config.js scans "../backend/templates" AND
# "../backend/apps/*/templates" (relative to frontend/, i.e. resolves to
# /backend/... given WORKDIR /frontend here). Copying the whole backend/
# (not just backend/templates) means any app's templates are covered
# without editing this Dockerfile again later — this stage is discarded
# after the build, so the extra Python files add zero cost to the final
# image.
COPY backend /backend

RUN npm run build
# Output lands in /frontend/dist (manifest.json + hashed JS/CSS bundles),
# which is exactly what django-vite reads in production mode.


# =============================================================================
# Stage 2: Python base — shared setup for both the "dev" and "prod" targets
# below, so we don't repeat these steps twice.
# =============================================================================
FROM python:3.12-slim AS python-base

# PYTHONDONTWRITEBYTECODE: don't create .pyc files (not useful in a container
#   that gets rebuilt from scratch anyway).
# PYTHONUNBUFFERED: send stdout/stderr straight out instead of buffering them,
#   otherwise "docker logs" can show messages late or out of order.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System libraries required to build/run psycopg2 (the PostgreSQL driver).
# libpq-dev = PostgreSQL client headers, gcc = C compiler needed to build it.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# /app mirrors the repository root, so paths inside the container match
# local development, where backend/ and frontend/ sit next to each other.
WORKDIR /app

COPY backend/requirements/ /app/backend/requirements/


# =============================================================================
# Stage 3: Development target — used by docker-compose.yml
# =============================================================================
FROM python-base AS dev

RUN pip install --no-cache-dir -r backend/requirements/dev.txt

# We deliberately do NOT copy the source code here. docker-compose.yml
# bind-mounts ./backend into the container instead, so code changes on the
# host are picked up immediately without rebuilding the image.

WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# =============================================================================
# Stage 4: Production target — used by docker-compose.prod.yml
# =============================================================================
FROM python-base AS prod

RUN pip install --no-cache-dir -r backend/requirements/prod.txt

# Unlike "dev", production bakes the code into the image (no bind mount),
# so the image is a self-contained, deployable artifact.
COPY backend/ /app/backend/

# Bring in the frontend build from stage 1, placed in the same relative
# position ("../frontend/dist" as seen from backend/) that django-vite's
# settings.py configuration expects locally.
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

WORKDIR /app/backend

# NOTE (Phase 0 TODO): collectstatic needs a valid SECRET_KEY and DB
# configuration to run, which requires settings.py to read from .env first.
# We wire that up in Phase 0 — until then this stays commented out.
# RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]