#!/usr/bin/env bash
# Local development server on port 8001 (frontend expects 8001; use 3001 for frontend).
set -e
cd "$(dirname "$0")"
exec uvicorn main:app --reload --port 8001
