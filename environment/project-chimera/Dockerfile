# Dockerfile for Project Chimera
# 
# Purpose:
#   - Containerize Project Chimera for reproducible deployment
#   - Support development and production environments
#   - Enable CI/CD integration
# 
# Spec Reference: specs/technical.md Section 8 (Environment Configuration)
# 
# Governor Mode Compliance:
#   - No real agent execution during build
#   - No real MCP calls during build
#   - No real database connections during build
#   - Stub endpoints only (/health returns 200 OK)

# Base image: Python 3.11 slim (Debian-based)
FROM python:3.11-slim

# Metadata
LABEL maintainer="Tekleab Alemayehu <tekleab@10academy.org>"
LABEL description="Project Chimera - Autonomous AI Influencer Agent Orchestration System"
LABEL version="0.1.0"
LABEL spec_reference="specs/technical.md"

# Set environment variables
# PYTHONUNBUFFERED: Ensure Python output is sent straight to terminal
# PYTHONDONTWRITEBYTECODE: Prevent Python from writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
# - curl: Health checks
# - git: Version control (optional for CI/CD)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
# Copy pyproject.toml first for better layer caching
COPY pyproject.toml ./

# Install Python dependencies
# Use pip to install from pyproject.toml
# Note: In production, use uv for faster installs
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy application source code
COPY src/ ./src/
COPY tests/ ./tests/

# Copy configuration files
COPY .env.example ./.env.example

# Create non-root user for security
# Governor Mode: No real execution, but follow security best practices
RUN useradd -m -u 1000 chimera && \
    chown -R chimera:chimera /app

# Switch to non-root user
USER chimera

# Expose port 8000 for FastAPI
EXPOSE 8000

# Health check
# Verify FastAPI app is running and returns 200 OK
# Spec Reference: specs/technical.md Section 7 (API Contracts)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Run FastAPI app with uvicorn
# Governor Mode: All endpoints return HTTP 501 Not Implemented (except / and /health)
# 
# Options:
#   --host 0.0.0.0: Listen on all interfaces
#   --port 8000: Default port
#   --reload: Auto-reload on code changes (development only)
# 
# For production, use:
#   CMD ["uvicorn", "chimera.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
CMD ["uvicorn", "chimera.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Build Instructions:
# 
# Development:
#   docker build -t chimera:dev .
#   docker run -p 8000:8000 chimera:dev
# 
# Production:
#   docker build -t chimera:latest .
#   docker run -d -p 8000:8000 --name chimera chimera:latest
# 
# With environment variables:
#   docker run -p 8000:8000 --env-file .env chimera:dev
# 
# Governor Mode Verification:
#   docker run -p 8000:8000 chimera:dev
#   curl http://localhost:8000/          # Should return 200 OK
#   curl http://localhost:8000/health    # Should return 200 OK
#   curl http://localhost:8000/planner/tasks  # Should return 501 Not Implemented

