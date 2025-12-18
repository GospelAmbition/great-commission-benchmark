#!/bin/bash
# Quick wrapper script for watching Railway build failures

# Default to checking all services, but allow override
SERVICE="${1:-}"
OUTPUT="${2:-.build-errors.md}"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Error: Railway CLI not found."
    echo "Install with: npm install -g @railway/cli"
    echo "Then login with: railway login"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python 3 not found."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Run the Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$PYTHON_CMD "$SCRIPT_DIR/watch_builds.py" \
    ${SERVICE:+--service "$SERVICE"} \
    --output "$OUTPUT" \
    ${WATCH_MODE:+--watch} \
    ${INTERVAL:+--interval "$INTERVAL"}
