#!/usr/bin/env python3
"""
Shared Configuration Module for Great Commission Benchmark

This module provides centralized configuration management for all benchmark versions.
It automatically looks for API keys in the project root .env file and environment variables.
"""

import os
from pathlib import Path
from typing import Optional

def find_project_root() -> Path:
    """
    Find the project root directory by looking for the .env file
    """
    current_dir = Path(__file__).parent.absolute()
    
    # Look for .env file in current directory and parent directories
    while current_dir != current_dir.parent:
        if (current_dir / '.env').exists():
            return current_dir
        current_dir = current_dir.parent
    
    # If not found, return the directory containing this file
    return Path(__file__).parent.absolute()

def load_env_file(env_path: Path) -> dict:
    """
    Load environment variables from .env file
    """
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def get_openrouter_api_key() -> Optional[str]:
    """
    Get OpenRouter API key from multiple sources in order of preference:
    1. Environment variable OPENROUTER_API_KEY
    2. Project root .env file
    3. None if not found
    """
    # First, check environment variable
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        return api_key
    
    # If not in environment, look for .env file in project root
    project_root = find_project_root()
    env_file = project_root / '.env'
    
    if env_file.exists():
        env_vars = load_env_file(env_file)
        api_key = env_vars.get('OPENROUTER_API_KEY')
        if api_key:
            return api_key
    
    return None

def get_benchmark_config() -> dict:
    """
    Get complete benchmark configuration
    """
    return {
        'openrouter_api_key': get_openrouter_api_key(),
        'project_root': find_project_root(),
        'has_api_key': get_openrouter_api_key() is not None
    }

def validate_config() -> tuple[bool, str]:
    """
    Validate that the configuration is properly set up
    Returns: (is_valid, error_message)
    """
    config = get_benchmark_config()
    
    if not config['has_api_key']:
        project_root = config['project_root']
        return False, f"""
OpenRouter API key not found. Please ensure one of the following:

1. Set environment variable:
   export OPENROUTER_API_KEY='your-api-key-here'

2. Or create a .env file at project root ({project_root}/.env) with:
   OPENROUTER_API_KEY=your-api-key-here

3. Or place the API key directly in the .env file at: {project_root}/.env
"""
    
    return True, "Configuration valid"

if __name__ == "__main__":
    # Test the configuration
    config = get_benchmark_config()
    print(f"Project root: {config['project_root']}")
    print(f"Has API key: {config['has_api_key']}")
    
    if config['has_api_key']:
        print(f"API key: {config['openrouter_api_key'][:20]}...")
    else:
        is_valid, error = validate_config()
        print(f"Configuration valid: {is_valid}")
        if not is_valid:
            print(error)
