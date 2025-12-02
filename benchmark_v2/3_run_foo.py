#!/usr/bin/env python3
"""
Run script for Benchmark V2 Pipeline.

Executes all promptfoo YAML configurations and tracks progress.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def get_base_dir() -> Path:
    """Get the base directory (where this script is located)."""
    return Path(__file__).parent


def get_yaml_files() -> list[Path]:
    """Get all promptfoo YAML files to process."""
    base = get_base_dir()
    promptfoo_dir = base / "_3_promptfoo"
    
    if not promptfoo_dir.exists():
        raise FileNotFoundError(f"PromptFoo folder not found: {promptfoo_dir}")
    
    yaml_files = sorted(promptfoo_dir.glob("*-promptfoo.yaml"))
    return yaml_files


def run_promptfoo(yaml_file: Path, verbose: bool = False) -> tuple[bool, str]:
    """Run promptfoo evaluation for a single YAML file.
    
    Args:
        yaml_file: Path to the promptfoo YAML config
        verbose: Whether to show verbose output
        
    Returns:
        Tuple of (success, message)
    """
    # Use --yes to auto-accept any installation prompts
    cmd = ["npx", "--yes", "promptfoo@latest", "eval", "-c", str(yaml_file)]
    
    if verbose:
        cmd.append("--verbose")
    
    try:
        # Run without capturing output so user can see progress in real-time
        result = subprocess.run(
            cmd,
            timeout=7200,  # 2 hour timeout per model
        )
        
        if result.returncode == 0:
            return True, "Success"
        else:
            return False, f"Error: promptfoo exited with code {result.returncode}"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout (exceeded 2 hours)"
    except FileNotFoundError:
        return False, "npx not found. Please install Node.js and npm."
    except Exception as e:
        return False, f"Exception: {str(e)}"


def main():
    """Run all promptfoo evaluations."""
    print("=" * 50)
    print("Benchmark V2 - Run PromptFoo Evaluations")
    print("=" * 50)
    print()
    
    # Get YAML files
    yaml_files = get_yaml_files()
    
    if not yaml_files:
        print("No promptfoo YAML files found in _3_promptfoo/")
        print("Run: python 2_build_foo.py first")
        sys.exit(1)
    
    print(f"Found {len(yaml_files)} promptfoo config(s) to run:")
    for f in yaml_files:
        print(f"  - {f.name}")
    print()
    
    # Track results
    results = []
    start_time = datetime.now()
    
    # Run each config
    for i, yaml_file in enumerate(yaml_files, 1):
        model_name = yaml_file.stem.replace("-promptfoo", "")
        print(f"[{i}/{len(yaml_files)}] Running: {model_name}")
        print(f"    Config: {yaml_file.name}")
        
        run_start = datetime.now()
        success, message = run_promptfoo(yaml_file)
        run_duration = datetime.now() - run_start
        
        results.append({
            "model": model_name,
            "yaml_file": yaml_file.name,
            "success": success,
            "message": message,
            "duration": str(run_duration),
        })
        
        status = "✓" if success else "✗"
        print(f"    {status} {message} ({run_duration})")
        print()
    
    # Summary
    total_duration = datetime.now() - start_time
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    print(f"Total:      {len(results)} evaluations")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Duration:   {total_duration}")
    print()
    
    if failed > 0:
        print("Failed evaluations:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['model']}: {r['message']}")
        print()
    
    print("Next step: python 4_import.py")
    print("=" * 50)
    
    # Exit with error code if any failed
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()



