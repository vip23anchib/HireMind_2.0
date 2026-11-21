# ==============================================================================
# Multi-Stage Production Dockerfile for HireMind Enterprise ATS
# Stage 1: Build modern React + TypeScript Vite frontend
# Stage 2: Production Python 3.12 + Gunicorn + WhiteNoise backend
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Frontend Build
# ------------------------------------------------------------------------------
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Backend Runtime
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (PostgreSQL client libraries, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . /app/

# Copy compiled frontend assets from Stage 1 into backend for static serving fallback
COPY --from=frontend-builder /app/frontend/dist /app/frontend_dist

# Create necessary directories
RUN mkdir -p /app/media /app/productionfiles /app/globalCSSfiles

# Collect static files using production settings
ENV DJANGO_SETTINGS_MODULE=my_project.settings.production \
    SECRET_KEY=dummy-build-key-for-collectstatic \
    DATABASE_URL=sqlite:///tmp.db

RUN python manage.py collectstatic --noinput || true

# Clean up build artifacts
RUN rm -f tmp.db

# Expose standard application port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Default runtime command: Launch Gunicorn WSGI server
CMD ["gunicorn", "my_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
