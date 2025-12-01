#!/usr/bin/env python3
"""
Great Commission Benchmark - User-Friendly GUI Launcher

Double-click this file to run the benchmark pipeline with a simple interface.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import threading
import yaml

# Add benchmark directory to path
SCRIPT_DIR = Path(__file__).parent.absolute()
BENCHMARK_DIR = SCRIPT_DIR  # Script is already in benchmark directory
sys.path.insert(0, str(BENCHMARK_DIR))

# Try to find and activate venv
VENV_PYTHON = None
if (BENCHMARK_DIR / "venv" / "bin" / "python").exists():
    VENV_PYTHON = str(BENCHMARK_DIR / "venv" / "bin" / "python")
elif (BENCHMARK_DIR / "venv" / "bin" / "python3").exists():
    VENV_PYTHON = str(BENCHMARK_DIR / "venv" / "bin" / "python3")


class BenchmarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Great Commission Benchmark")
        self.root.geometry("700x600")
        
        # Change to benchmark directory
        os.chdir(BENCHMARK_DIR)
        
        # Configuration
        self.config_path = BENCHMARK_DIR / "config.yaml"
        self.load_config()
        
        # UI Setup
        self.setup_ui()
        
    def load_config(self):
        """Load configuration from config.yaml"""
        self.config = {}
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f) or {}
        
        llm_config = self.config.get("llm", {})
        self.model = llm_config.get("test_model", "local-model")
        self.provider = llm_config.get("provider", "lmstudio")
        self.base_url = llm_config.get("base_url", "http://localhost:1234/v1")
        self.api_key = llm_config.get("api_key", "lm-studio")
        
    def save_config(self):
        """Save configuration to config.yaml"""
        if "llm" not in self.config:
            self.config["llm"] = {}
        
        self.config["llm"]["test_model"] = self.model_var.get()
        self.config["llm"]["provider"] = self.provider_var.get()
        self.config["llm"]["base_url"] = self.base_url_var.get()
        self.config["llm"]["api_key"] = self.api_key_var.get()
        
        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Great Commission Benchmark", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Model Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Model
        ttk.Label(config_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value=self.model)
        ttk.Entry(config_frame, textvariable=self.model_var, width=40).grid(row=0, column=1, pady=5, padx=5)
        
        # Provider
        ttk.Label(config_frame, text="Provider:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.provider_var = tk.StringVar(value=self.provider)
        provider_combo = ttk.Combobox(config_frame, textvariable=self.provider_var, 
                                     values=["lmstudio", "openrouter"], width=37)
        provider_combo.grid(row=1, column=1, pady=5, padx=5)
        
        # Base URL
        ttk.Label(config_frame, text="Base URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.base_url_var = tk.StringVar(value=self.base_url)
        ttk.Entry(config_frame, textvariable=self.base_url_var, width=40).grid(row=2, column=1, pady=5, padx=5)
        
        # API Key
        ttk.Label(config_frame, text="API Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=self.api_key)
        ttk.Entry(config_frame, textvariable=self.api_key_var, width=40, show="*").grid(row=3, column=1, pady=5, padx=5)
        
        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.skip_promptfoo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Skip PromptFoo execution (use existing results)", 
                       variable=self.skip_promptfoo_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.auto_evaluate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-evaluate responses after import", 
                       variable=self.auto_evaluate_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="Run Full Pipeline", 
                                     command=self.run_pipeline, width=20)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Save Config", 
                  command=self.save_config_click, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Test Connection", 
                  command=self.test_connection, width=15).pack(side=tk.LEFT, padx=5)
        
        # Output Log
        log_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def run_command(self, cmd, cwd=None):
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
    
    def run_promptfoo_in_terminal(self):
        """Launch PromptFoo in a separate Terminal window"""
        script_path = BENCHMARK_DIR / "run_promptfoo.command"
        
        # Create the command script if it doesn't exist
        if not script_path.exists():
            self.create_promptfoo_script()
        
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
            self.log(f"Error opening Terminal: {e}")
            return False
    
    def create_promptfoo_script(self):
        """Create the .command script for running PromptFoo"""
        script_path = BENCHMARK_DIR / "run_promptfoo.command"
        python_cmd = VENV_PYTHON if VENV_PYTHON else sys.executable
        
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
    
    def run_pipeline(self):
        """Run the full pipeline"""
        self.run_button.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
        
        # Save config first
        self.save_config()
        self.log("Configuration saved.")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self._run_pipeline_thread)
        thread.daemon = True
        thread.start()
    
    def _run_pipeline_thread(self):
        """Run pipeline steps in background thread"""
        try:
            # Step 1: Prepare (Export)
            self.log("=" * 60)
            self.log("Step 1: Preparing - Exporting questions to PromptFoo format...")
            self.log("=" * 60)
            
            success, stdout, stderr = self.run_command([
                "prepare",
                "--model", self.model_var.get(),
                "--provider", self.provider_var.get(),
                "--base-url", self.base_url_var.get(),
                "--api-key", self.api_key_var.get()
            ])
            
            if not success:
                self.log(f"ERROR: {stderr}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Prepare step failed:\n{stderr}"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
            
            self.log(stdout)
            self.log("✓ Step 1 complete: Questions exported\n")
            
            # Step 2: Execute PromptFoo (if not skipped)
            if not self.skip_promptfoo_var.get():
                self.log("=" * 60)
                self.log("Step 2: Executing PromptFoo evaluation...")
                self.log("=" * 60)
                self.log("Opening PromptFoo in a separate Terminal window...")
                self.log("Please monitor the Terminal window for progress.")
                self.log("This step may take a while depending on the number of questions.\n")
                
                if self.run_promptfoo_in_terminal():
                    self.log("✓ PromptFoo Terminal window opened")
                    self.log("Waiting for PromptFoo to complete...")
                    self.log("Please check the Terminal window and press OK when it's done.")
                    
                    # Show dialog to wait for user confirmation
                    self.root.after(0, lambda: messagebox.showinfo(
                        "PromptFoo Running",
                        "PromptFoo is running in a separate Terminal window.\n\n"
                        "Please wait for it to complete, then click OK to continue."
                    ))
                else:
                    self.log("ERROR: Could not open Terminal window")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Could not open Terminal window for PromptFoo"))
                    self.root.after(0, lambda: self.run_button.config(state="normal"))
                    return
            else:
                self.log("Skipping PromptFoo execution (using existing results)\n")
            
            # Step 3: Import Results
            self.log("=" * 60)
            self.log("Step 3: Importing results into database...")
            self.log("=" * 60)
            
            success, stdout, stderr = self.run_command([
                "import-results",
                "--model", self.model_var.get()
            ])
            
            if not success:
                self.log(f"ERROR: {stderr}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Import step failed:\n{stderr}"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
            
            self.log(stdout)
            self.log("✓ Step 3 complete: Results imported\n")
            
            # Step 4: Evaluate (if enabled)
            if self.auto_evaluate_var.get():
                self.log("=" * 60)
                self.log("Step 4: Evaluating responses...")
                self.log("=" * 60)
                
                success, stdout, stderr = self.run_command(["evaluate"])
                
                if not success:
                    self.log(f"ERROR: {stderr}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Evaluate step failed:\n{stderr}"))
                    self.root.after(0, lambda: self.run_button.config(state="normal"))
                    return
                
                self.log(stdout)
                self.log("✓ Step 4 complete: Responses evaluated\n")
            
            # Step 5: Generate Report
            self.log("=" * 60)
            self.log("Step 5: Generating report...")
            self.log("=" * 60)
            
            success, stdout, stderr = self.run_command(["report"])
            
            if not success:
                self.log(f"ERROR: {stderr}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Report step failed:\n{stderr}"))
                self.root.after(0, lambda: self.run_button.config(state="normal"))
                return
            
            self.log(stdout)
            self.log("✓ Step 5 complete: Report generated\n")
            
            self.log("=" * 60)
            self.log("Pipeline complete! ✓")
            self.log("=" * 60)
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Pipeline completed successfully!"))
            
        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Pipeline failed:\n{str(e)}"))
        finally:
            self.root.after(0, lambda: self.run_button.config(state="normal"))
    
    def test_connection(self):
        """Test connection to LLM"""
        self.log("Testing connection...")
        success, stdout, stderr = self.run_command(["test-connection"])
        
        if success:
            self.log(stdout)
            messagebox.showinfo("Success", "Connection test passed!")
        else:
            self.log(f"ERROR: {stderr}")
            messagebox.showerror("Error", f"Connection test failed:\n{stderr}")
    
    def save_config_click(self):
        """Save configuration (button click handler)"""
        try:
            self.save_config()
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config:\n{str(e)}")


def main():
    root = tk.Tk()
    app = BenchmarkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

