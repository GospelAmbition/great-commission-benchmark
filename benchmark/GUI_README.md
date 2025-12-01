# Pipeline Launcher - Quick Start Guide

## Overview

The Great Commission Benchmark includes a user-friendly web-based launcher that makes it easy for non-engineering users to run the benchmark pipeline. The launcher uses Streamlit (already installed) and opens in your web browser.

## Files

- **`run_pipeline.command`** - Launcher script (double-click to run)
- **`run_pipeline_ui.py`** - Streamlit web application
- **`run_promptfoo.command`** - Terminal script for running PromptFoo (auto-created, can also be double-clicked)

## Usage

### First Time Setup

1. **Make sure dependencies are installed:**
   ```bash
   cd benchmark
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize databases (if not already done):**
   ```bash
   python -m gcb init
   ```

### Running the Pipeline Launcher

1. **Double-click `run_pipeline.command`** in Finder
   - This will open a Terminal window and launch the web interface
   - Your browser should open automatically to `http://localhost:8501`
   - If it doesn't open automatically, go to that URL manually

2. **Or run from terminal:**
   ```bash
   cd benchmark
   streamlit run run_pipeline_ui.py
   ```

2. **Configure your model settings:**
   - **Model**: Name of the model (e.g., `gpt-4`, `qwen/qwen3-4b`)
   - **Provider**: Choose `lmstudio` or `openrouter`
   - **Base URL**: API endpoint URL
   - **API Key**: Your API key (hidden for security)

3. **Click "Save Config"** to save your settings

4. **Optional: Click "Test Connection"** to verify your settings work

5. **Click "Run Full Pipeline"** to start the benchmark

### What Happens When You Run

1. **Step 1: Prepare** - Exports questions to PromptFoo format
2. **Step 2: Execute** - Opens PromptFoo in a separate Terminal window
   - Monitor progress in the Terminal window
   - When complete, click OK in the dialog to continue
3. **Step 3: Import** - Imports results into the database
4. **Step 4: Evaluate** - Evaluates responses (if enabled)
5. **Step 5: Report** - Generates the benchmark report

### Options

- **Skip PromptFoo execution**: Check this if you already have results and want to skip the PromptFoo step
- **Auto-evaluate responses**: Uncheck if you want to evaluate manually later

### Running PromptFoo Separately

You can also double-click `run_promptfoo.command` to run PromptFoo evaluation independently in a Terminal window. This is useful if you want to:
- Run PromptFoo multiple times
- Monitor PromptFoo output separately
- Run PromptFoo without the full pipeline

## Troubleshooting

### Web interface won't open
- Make sure Streamlit is installed: `pip install streamlit`
- Check if the port is already in use (another Streamlit app might be running)
- Try accessing manually: Open `http://localhost:8501` in your browser
- Check the Terminal window for error messages

### PromptFoo Terminal window doesn't open
- Make sure Terminal app has permission to run scripts
- Try running `run_promptfoo.command` directly from Terminal first

### Virtual environment not found
- The script will use system Python if venv is not found
- Make sure dependencies are installed: `pip install -r requirements.txt`

### Connection test fails
- Verify your API endpoint is running (for LM Studio, make sure it's started)
- Check your Base URL and API Key settings
- For OpenRouter, make sure your API key is valid

## Tips

- The GUI automatically saves your configuration to `config.yaml`
- All output is logged in the "Output Log" section
- You can resize the window to see more of the log
- The GUI will detect and use your virtual environment automatically

