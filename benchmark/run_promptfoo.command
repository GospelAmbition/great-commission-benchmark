#!/bin/bash
# PromptFoo Runner Script
# This script runs PromptFoo evaluation in Terminal
# Double-click this file to run PromptFoo evaluation

cd "$(dirname "$0")"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "=========================================="
echo "Great Commission Benchmark - PromptFoo"
echo "=========================================="
echo ""
echo "Running PromptFoo evaluation..."
echo "This may take a while depending on the number of questions."
echo ""
echo "Press Ctrl+C to cancel"
echo ""

# Run PromptFoo
npx promptfoo@latest eval -c prompts/promptfoo.yaml

echo ""
echo "=========================================="
echo "PromptFoo evaluation complete!"
echo "=========================================="
echo ""
echo "You can now close this window."
echo "Press any key to close..."
read -n 1

