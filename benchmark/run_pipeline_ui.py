#!/usr/bin/env python3
"""
Great Commission Benchmark - Pipeline Launcher (Streamlit)

Run the full benchmark pipeline with a user-friendly web interface.
Double-click run_pipeline.command to launch this in your browser.
"""

import sys
from pathlib import Path

# Add benchmark directory to path
BENCHMARK_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BENCHMARK_DIR))

import streamlit as st
import subprocess
import yaml
from pathlib import Path

st.set_page_config(
    page_title="GCB Pipeline Launcher",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Try to find venv Python
VENV_PYTHON = None
if (BENCHMARK_DIR / "venv" / "bin" / "python").exists():
    VENV_PYTHON = str(BENCHMARK_DIR / "venv" / "bin" / "python")
elif (BENCHMARK_DIR / "venv" / "bin" / "python3").exists():
    VENV_PYTHON = str(BENCHMARK_DIR / "venv" / "bin" / "python3")

# Change to benchmark directory
import os
os.chdir(BENCHMARK_DIR)

# Initialize session state
if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False
if "pipeline_log" not in st.session_state:
    st.session_state.pipeline_log = []
if "current_step" not in st.session_state:
    st.session_state.current_step = None


def load_config():
    """Load configuration from config.yaml"""
    config_path = BENCHMARK_DIR / "config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    
    llm_config = config.get("llm", {})
    return {
        "model": llm_config.get("test_model", "local-model"),
        "provider": llm_config.get("provider", "lmstudio"),
        "base_url": llm_config.get("base_url", "http://localhost:1234/v1"),
        "api_key": llm_config.get("api_key", "lm-studio"),
        "config": config,
    }


def save_config(model, provider, base_url, api_key):
    """Save configuration to config.yaml"""
    config_path = BENCHMARK_DIR / "config.yaml"
    config = load_config()["config"]
    
    if "llm" not in config:
        config["llm"] = {}
    
    config["llm"]["test_model"] = model
    config["llm"]["provider"] = provider
    config["llm"]["base_url"] = base_url
    config["llm"]["api_key"] = api_key
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def run_command(cmd, cwd=None):
    """Run a command and return output"""
    python_cmd = VENV_PYTHON if VENV_PYTHON else sys.executable
    full_cmd = [python_cmd, "-m", "gcb"] + cmd
    
    try:
        result = subprocess.run(
            full_cmd,
            cwd=cwd or str(BENCHMARK_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out after 5 minutes"
    except Exception as e:
        return False, "", str(e)


def run_promptfoo_in_terminal():
    """Launch PromptFoo in a separate Terminal window"""
    script_path = BENCHMARK_DIR / "run_promptfoo.command"
    
    # Create the command script if it doesn't exist
    if not script_path.exists():
        create_promptfoo_script()
    
    # Use osascript to open Terminal and run the script
    applescript = f'''
    tell application "Terminal"
        activate
        do script "cd '{BENCHMARK_DIR}' && chmod +x run_promptfoo.command && ./run_promptfoo.command"
    end tell
    '''
    
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        return True
    except Exception as e:
        st.error(f"Error opening Terminal: {e}")
        return False


def create_promptfoo_script():
    """Create the .command script for running PromptFoo"""
    script_path = BENCHMARK_DIR / "run_promptfoo.command"
    
    script_content = f'''#!/bin/bash
# PromptFoo Runner Script
# This script runs PromptFoo evaluation in Terminal

cd "{BENCHMARK_DIR}"

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
'''
    
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)


def run_pipeline_step(step_name, step_func, *args, **kwargs):
    """Run a pipeline step and update UI"""
    st.session_state.current_step = step_name
    st.session_state.pipeline_log.append(f"\n{'='*60}")
    st.session_state.pipeline_log.append(f"Step: {step_name}")
    st.session_state.pipeline_log.append(f"{'='*60}\n")
    
    try:
        result = step_func(*args, **kwargs)
        if result:
            st.session_state.pipeline_log.append(f"✓ {step_name} complete\n")
        else:
            st.session_state.pipeline_log.append(f"✗ {step_name} failed\n")
        return result
    except Exception as e:
        st.session_state.pipeline_log.append(f"✗ {step_name} error: {str(e)}\n")
        return False


def step_prepare(model, provider, base_url, api_key):
    """Step 1: Prepare (Export)"""
    success, stdout, stderr = run_command([
        "prepare",
        "--model", model,
        "--provider", provider,
        "--base-url", base_url,
        "--api-key", api_key
    ])
    
    if stdout:
        st.session_state.pipeline_log.append(stdout)
    if stderr:
        st.session_state.pipeline_log.append(f"ERROR: {stderr}")
    
    return success


def step_execute(skip_promptfoo):
    """Step 2: Execute PromptFoo"""
    if skip_promptfoo:
        st.session_state.pipeline_log.append("Skipping PromptFoo execution (using existing results)\n")
        return True
    
    st.session_state.pipeline_log.append("Opening PromptFoo in a separate Terminal window...\n")
    st.session_state.pipeline_log.append("Please monitor the Terminal window for progress.\n")
    
    if run_promptfoo_in_terminal():
        st.session_state.pipeline_log.append("✓ PromptFoo Terminal window opened\n")
        return "wait_for_user"  # Special return value
    else:
        st.session_state.pipeline_log.append("ERROR: Could not open Terminal window\n")
        return False


def step_import(model):
    """Step 3: Import Results"""
    success, stdout, stderr = run_command([
        "import-results",
        "--model", model
    ])
    
    if stdout:
        st.session_state.pipeline_log.append(stdout)
    if stderr:
        st.session_state.pipeline_log.append(f"ERROR: {stderr}")
    
    return success


def step_evaluate():
    """Step 4: Evaluate Responses"""
    success, stdout, stderr = run_command(["evaluate"])
    
    if stdout:
        st.session_state.pipeline_log.append(stdout)
    if stderr:
        st.session_state.pipeline_log.append(f"ERROR: {stderr}")
    
    return success


def step_report():
    """Step 5: Generate Report"""
    success, stdout, stderr = run_command(["report"])
    
    if stdout:
        st.session_state.pipeline_log.append(stdout)
    if stderr:
        st.session_state.pipeline_log.append(f"ERROR: {stderr}")
    
    return success


def main():
    st.title("🚀 Great Commission Benchmark - Pipeline Launcher")
    st.markdown("Run the full benchmark pipeline with a simple interface.")
    
    # Load current config
    config = load_config()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        model = st.text_input("Model", value=config["model"], help="Model name (e.g., gpt-4, qwen/qwen3-4b)")
        provider = st.selectbox("Provider", ["lmstudio", "openrouter"], 
                               index=0 if config["provider"] == "lmstudio" else 1)
        base_url = st.text_input("Base URL", value=config["base_url"])
        api_key = st.text_input("API Key", value=config["api_key"], type="password")
        
        st.divider()
        
        st.header("Options")
        skip_promptfoo = st.checkbox("Skip PromptFoo execution", 
                                     help="Use existing results instead of running PromptFoo")
        auto_evaluate = st.checkbox("Auto-evaluate responses", value=True,
                                   help="Automatically evaluate responses after import")
        
        st.divider()
        
        if st.button("💾 Save Configuration", use_container_width=True):
            save_config(model, provider, base_url, api_key)
            st.success("Configuration saved!")
        
        if st.button("🔌 Test Connection", use_container_width=True):
            with st.spinner("Testing connection..."):
                success, stdout, stderr = run_command(["test-connection"])
                if success:
                    st.success("Connection test passed!")
                    st.code(stdout)
                else:
                    st.error("Connection test failed!")
                    st.code(stderr)
    
    # Main content area
    if st.session_state.pipeline_running or st.session_state.pipeline_log:
        # Show current step
        if st.session_state.current_step:
            st.info(f"🔄 {st.session_state.current_step}")
        
        # Check if we're waiting for user confirmation
        if st.session_state.get("waiting_for_promptfoo", False):
            st.warning("⚠️ Waiting for PromptFoo to complete in Terminal window...")
            if st.button("✅ PromptFoo Complete - Continue", type="primary", use_container_width=True):
                st.session_state.waiting_for_promptfoo = False
                st.session_state.pipeline_running = True
                st.rerun()
        
        # Show log
        st.subheader("Pipeline Log")
        log_text = "\n".join(st.session_state.pipeline_log) if st.session_state.pipeline_log else "No log entries yet."
        st.text_area("", value=log_text, height=400, disabled=True, key="log_display")
        
        if st.session_state.pipeline_running:
            st.info("Pipeline is running... Please wait.")
        
        st.divider()
        
    else:
        st.subheader("Pipeline Steps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Step 1: Prepare** - Export questions to PromptFoo format
            
            **Step 2: Execute** - Run PromptFoo evaluation (opens in Terminal)
            
            **Step 3: Import** - Import results into database
            """)
        
        with col2:
            st.markdown("""
            **Step 4: Evaluate** - Judge responses using LLM (if enabled)
            
            **Step 5: Report** - Generate benchmark statistics
            """)
        
        st.divider()
        
        if st.button("🚀 Run Full Pipeline", type="primary", use_container_width=True):
            st.session_state.pipeline_running = True
            st.session_state.pipeline_log = []
            st.session_state.current_step = None
            st.session_state.waiting_for_promptfoo = False
            
            # Save config first
            save_config(model, provider, base_url, api_key)
            st.session_state.pipeline_log.append("Configuration saved.\n")
            
            # Run pipeline steps sequentially
            try:
                # Step 1: Prepare
                st.session_state.current_step = "Step 1: Prepare"
                with st.spinner("Step 1: Preparing - Exporting questions..."):
                    if not step_prepare(model, provider, base_url, api_key):
                        st.error("Step 1 failed. Check the log below.")
                        st.session_state.pipeline_running = False
                    else:
                        st.session_state.pipeline_log.append("✓ Step 1 complete: Questions exported\n")
                
                if not st.session_state.pipeline_running:
                    st.stop()
                
                # Step 2: Execute
                st.session_state.current_step = "Step 2: Execute"
                if not skip_promptfoo:
                    st.info("Step 2: Opening PromptFoo in Terminal window...")
                    if step_execute(skip_promptfoo) == "wait_for_user":
                        st.session_state.waiting_for_promptfoo = True
                        st.warning("⚠️ Please wait for PromptFoo to complete in the Terminal window, then click the button below to continue.")
                        st.stop()
                    elif not st.session_state.pipeline_running:
                        st.error("Step 2 failed. Check the log below.")
                        st.stop()
                    else:
                        st.session_state.pipeline_log.append("✓ Step 2 complete: PromptFoo executed\n")
                else:
                    st.session_state.pipeline_log.append("Skipping PromptFoo execution (using existing results)\n")
                
                # Step 3: Import
                st.session_state.current_step = "Step 3: Import"
                with st.spinner("Step 3: Importing results..."):
                    if not step_import(model):
                        st.error("Step 3 failed. Check the log below.")
                        st.session_state.pipeline_running = False
                    else:
                        st.session_state.pipeline_log.append("✓ Step 3 complete: Results imported\n")
                
                if not st.session_state.pipeline_running:
                    st.stop()
                
                # Step 4: Evaluate (if enabled)
                if auto_evaluate:
                    st.session_state.current_step = "Step 4: Evaluate"
                    with st.spinner("Step 4: Evaluating responses..."):
                        if not step_evaluate():
                            st.error("Step 4 failed. Check the log below.")
                            st.session_state.pipeline_running = False
                        else:
                            st.session_state.pipeline_log.append("✓ Step 4 complete: Responses evaluated\n")
                    
                    if not st.session_state.pipeline_running:
                        st.stop()
                
                # Step 5: Report
                st.session_state.current_step = "Step 5: Report"
                with st.spinner("Step 5: Generating report..."):
                    if not step_report():
                        st.error("Step 5 failed. Check the log below.")
                        st.session_state.pipeline_running = False
                    else:
                        st.session_state.pipeline_log.append("✓ Step 5 complete: Report generated\n")
                
                if st.session_state.pipeline_running:
                    st.session_state.pipeline_log.append("\n" + "="*60)
                    st.session_state.pipeline_log.append("Pipeline complete! ✓")
                    st.session_state.pipeline_log.append("="*60)
                    st.success("🎉 Pipeline completed successfully!")
                    st.session_state.pipeline_running = False
                    st.session_state.current_step = None
                
            except Exception as e:
                st.session_state.pipeline_log.append(f"\nERROR: {str(e)}")
                st.error(f"Pipeline failed: {str(e)}")
                st.session_state.pipeline_running = False
                st.session_state.current_step = None
        
        # Show log if there is one
        if st.session_state.pipeline_log:
            st.subheader("Last Run Log")
            log_text = "\n".join(st.session_state.pipeline_log)
            st.text_area("", value=log_text, height=300, disabled=True, key="last_log")


if __name__ == "__main__":
    main()

