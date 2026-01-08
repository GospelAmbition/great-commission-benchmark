#!/bin/bash
set -e

# Immediate startup diagnostics - output ASAP to catch early failures
echo "=== STARTUP BEGIN $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo "PID: $$"
echo "PWD: $(pwd)"
echo "USER: $(whoami)"

echo "============================================"
echo "Starting Great Commission Benchmark Backend"
echo "============================================"
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "PORT=${PORT:-8000}"
echo "PYTHON: $(python --version 2>&1)"
echo "DATABASE_URL is $([ -n "$DATABASE_URL" ] && echo 'SET (length: '${#DATABASE_URL}')' || echo 'NOT SET')"
echo "NEXTAUTH_SECRET is $([ -n "$NEXTAUTH_SECRET" ] && echo 'SET' || echo 'NOT SET')"

# List files to verify deployment
echo "Checking key files..."
ls -la /app/main.py /app/start.sh /app/requirements.txt 2>&1 || echo "Some files missing!"

# Quick Python import test to catch early errors
echo "Testing Python imports..."
python -c "
import sys
import traceback
print(f'Python path: {sys.executable}')
try:
    from app.core.config import settings
    print('Config loaded OK')
    print(f'  CORS origins: {len(settings.CORS_ORIGINS)} configured')
except Exception as e:
    print(f'Config load FAILED: {e}')
    traceback.print_exc()
    sys.exit(1)

try:
    from main import app
    print('FastAPI app imported OK')
except Exception as e:
    print(f'FastAPI app import FAILED: {e}')
    traceback.print_exc()
    sys.exit(1)
" || {
    echo "ERROR: Failed to import application. Check logs above."
    exit 1
}

# Run database migrations with timeout (allow failure - app might still work with existing schema)
# The timeout prevents blocking if DB is not ready, allowing the health check to pass
# Reduced timeout to 10s to ensure app starts faster for healthcheck
echo "Running database migrations (10s timeout)..."
set +e  # Temporarily disable exit on error for migrations

# Check if timeout command is available, use Python fallback if not
if command -v timeout &> /dev/null; then
    timeout 10 alembic upgrade head 2>&1
    MIGRATION_STATUS=$?
else
    echo "Note: timeout command not available, using Python subprocess"
    python -c "
import subprocess
import sys
try:
    result = subprocess.run(['alembic', 'upgrade', 'head'], timeout=10, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print('Migration timed out')
    sys.exit(124)
except Exception as e:
    print(f'Migration error: {e}')
    sys.exit(1)
" 2>&1
    MIGRATION_STATUS=$?
fi
set -e  # Re-enable exit on error

if [ $MIGRATION_STATUS -eq 124 ]; then
    echo "Warning: Migration timed out, continuing anyway (DB may not be ready yet)..."
elif [ $MIGRATION_STATUS -ne 0 ]; then
    echo "Warning: Migration failed (exit code $MIGRATION_STATUS), continuing anyway..."
else
    echo "Migrations completed successfully."
fi

# Start the application (use exec to replace shell process)
PORT=${PORT:-8000}
echo "============================================"
echo "Starting uvicorn server on port ${PORT}..."
echo "============================================"
echo "Environment check:"
echo "  PORT=${PORT}"
echo "  DATABASE_URL=${DATABASE_URL:+SET (length: ${#DATABASE_URL})}"
echo "  NEXTAUTH_SECRET=${NEXTAUTH_SECRET:+SET}"
echo "Memory check:"
free -h 2>/dev/null || echo "  (free command not available)"
echo "Process check before uvicorn:"
ps aux 2>/dev/null | head -5 || echo "  (ps command not available)"
echo ""
echo "=== STARTING UVICORN $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --log-level info
