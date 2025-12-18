#!/bin/bash
set -e

echo "Starting Great Commission Benchmark Backend..."

# Run database migrations (allow failure - app might still work with existing schema)
echo "Running database migrations..."
set +e  # Temporarily disable exit on error for migrations
alembic upgrade head
MIGRATION_STATUS=$?
set -e  # Re-enable exit on error

if [ $MIGRATION_STATUS -ne 0 ]; then
    echo "Warning: Migration failed (exit code $MIGRATION_STATUS), continuing anyway..."
fi

# Start the application (use exec to replace shell process)
echo "Starting uvicorn server on port ${PORT:-8000}..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
