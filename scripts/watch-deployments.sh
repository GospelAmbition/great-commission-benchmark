#!/bin/bash
# Quick wrapper script for watching Railway deployments

# Default to checking all services, but allow override
SERVICE="${1:-}"
OUTPUT="${2:-.deployment-errors.md}"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Error: Railway CLI not found."
    echo "Install with: npm install -g @railway/cli"
    echo "Then login with: railway login"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found."
    exit 1
fi

# Run the Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/watch_deployments.py" \
    ${SERVICE:+--service "$SERVICE"} \
    --output "$OUTPUT" \
    ${WATCH_MODE:+--watch} \
    ${INTERVAL:+--interval "$INTERVAL"}
