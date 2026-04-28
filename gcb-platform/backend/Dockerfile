# Great Commission Benchmark - Backend Dockerfile
#
# Build context: monorepo root (so the gcb-mcp/ directory is available
# for installation alongside the backend). Configure the Railway
# service with `dockerfilePath: gcb-platform/backend/Dockerfile` and
# `rootDirectory: ` (i.e. monorepo root). The COPY commands below are
# expressed relative to that root.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies. We install the gcb-mcp package first so
# it's available as a sibling module to the backend (provides the
# FastMCP instance with all 33 tools that we mount under /mcp).
COPY gcb-mcp /tmp/gcb-mcp
RUN pip install --no-cache-dir /tmp/gcb-mcp

COPY gcb-platform/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY gcb-platform/backend/ /app/

# Copy startup script
RUN chmod +x /app/start.sh

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Run startup script which handles migrations and starts the app
CMD ["/app/start.sh"]
