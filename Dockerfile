# ShipFast v3.0 - Production Dockerfile
# Multi-stage build for optimized production deployment

# ============================================
# Stage 1: Build Frontend (React)
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY ui/client/package*.json ./

# Install frontend dependencies
RUN npm ci --production

# Copy frontend source code
COPY ui/client/ ./

# Build React app for production
RUN npm run build

# ============================================
# Stage 2: Build Backend (Python)
# ============================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY shipfast_v3/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Production Runtime
# ============================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY shipfast_v3/ ./shipfast_v3/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build ./ui/build

# Create necessary directories
RUN mkdir -p /app/shipfast_v3/shipfast_output && \
    mkdir -p /app/shipfast_v3/logs

# Create non-root user for security
RUN useradd -m -u 1000 shipfast && \
    chown -R shipfast:shipfast /app

# Switch to non-root user
USER shipfast

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "shipfast_v3.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
