#!/bin/bash
# Pipeline Launcher Script
# Double-click this file to launch the pipeline UI in your browser

cd "$(dirname "$0")"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "=========================================="
echo "Great Commission Benchmark - Pipeline Launcher"
echo "=========================================="
echo ""
echo "Starting Streamlit web interface..."
echo "Your browser should open automatically."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run run_pipeline_ui.py --server.headless true

