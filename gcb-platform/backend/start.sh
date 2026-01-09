#!/bin/bash
set -e

# Minimal startup - get to uvicorn ASAP for health checks
echo "=== GCB Backend Starting $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo "PORT=${PORT:-8080}"

# Quick sanity check - don't block on this
if [ ! -f /app/main.py ]; then
    echo "ERROR: main.py not found!"
    exit 1
fi

# SKIP migrations at startup - run them separately via Railway CLI
# This ensures the app starts FAST for health checks
# Migrations should be run manually: railway run alembic upgrade head
echo "Skipping migrations at startup (run manually via: railway run alembic upgrade head)"
echo "This ensures fast startup for health checks."

# Start the application IMMEDIATELY (use exec to replace shell process)
# Railway sets PORT environment variable
PORT=${PORT:-8080}
echo "=== STARTING UVICORN on port ${PORT} $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --log-level info
