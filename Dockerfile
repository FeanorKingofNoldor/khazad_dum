# ==============================================================================
# KHAZAD-DÛM TRADING SYSTEM - PRODUCTION DOCKERFILE
# Multi-stage build for optimal production image
# ==============================================================================

# -----------------------------------------------------------------------------
# Build Stage - Compile dependencies and prepare environment
# -----------------------------------------------------------------------------
FROM python:3.13-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create build user
RUN useradd --create-home --shell /bin/bash builder
WORKDIR /home/builder

# Copy requirements first for better caching
COPY requirements-py313.txt ./
COPY tradingagents_lib/requirements.txt ./tradingagents_requirements.txt

# Install Python dependencies in virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install main app dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements-py313.txt
RUN pip install --no-cache-dir -r tradingagents_requirements.txt

# Add additional production dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    uvicorn[standard] \
    fastapi \
    psycopg2-binary \
    prometheus-client \
    structlog

# -----------------------------------------------------------------------------
# Production Stage - Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.13-slim as production

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 khazad
WORKDIR /home/khazad/app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=khazad:khazad . .

# Create necessary directories with proper permissions
RUN mkdir -p \
    /home/khazad/app/logs \
    /home/khazad/app/data \
    /home/khazad/app/config/data/databases \
    /home/khazad/app/cache \
    /home/khazad/app/results \
    && chown -R khazad:khazad /home/khazad/app

# Switch to non-root user
USER khazad

# Expose ports
EXPOSE 8000 8001 8002

# Environment variables
ENV PYTHONPATH=/home/khazad/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PRODUCTION=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "main.py"]