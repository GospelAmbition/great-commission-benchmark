#!/bin/bash
set -e

echo "Starting Great Commission Benchmark Backend..."
echo "PORT=${PORT:-8000}"
echo "DATABASE_URL is $([ -n "$DATABASE_URL" ] && echo 'set' || echo 'NOT SET')"

# Run database migrations with timeout (allow failure - app might still work with existing schema)
# The timeout prevents blocking if DB is not ready, allowing the health check to pass
# Reduced timeout to 15s to ensure app starts faster for healthcheck
echo "Running database migrations (15s timeout)..."
set +e  # Temporarily disable exit on error for migrations
timeout 15 alembic upgrade head 2>&1
MIGRATION_STATUS=$?
set -e  # Re-enable exit on error

if [ $MIGRATION_STATUS -eq 124 ]; then
    echo "Warning: Migration timed out, continuing anyway (DB may not be ready yet)..."
elif [ $MIGRATION_STATUS -ne 0 ]; then
    echo "Warning: Migration failed (exit code $MIGRATION_STATUS), continuing anyway..."
else
    echo "Migrations completed successfully."
fi

# Start the application (use exec to replace shell process)
echo "Starting uvicorn server on port ${PORT:-8000}..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
