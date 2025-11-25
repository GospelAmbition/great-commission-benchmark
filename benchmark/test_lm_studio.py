#!/usr/bin/env python3
"""
Test script to verify LM Studio availability and connectivity.

This script checks:
1. LM Studio API endpoint is accessible
2. Models are available
3. The configured model exists
4. A simple completion request works
"""

import sys
import yaml
from pathlib import Path
from openai import OpenAI
from typing import Optional


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from config.yaml."""
    path = Path(config_path)
    if not path.exists():
        print(f"⚠️  Config file not found: {config_path}")
        print("Using default values...")
        return {}
    
    with open(path) as f:
        return yaml.safe_load(f) or {}


def test_lm_studio(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    config_path: str = "config.yaml",
) -> bool:
    """
    Test LM Studio connection and availability.
    
    Args:
        base_url: LM Studio API base URL (overrides config)
        api_key: API key (overrides config)
        model_name: Model name to test (overrides config)
        config_path: Path to config file
        
    Returns:
        True if all tests pass, False otherwise
    """
    # Load config if not provided
    config = load_config(config_path)
    llm_config = config.get("llm", {})
    
    base_url = base_url or llm_config.get("base_url", "http://127.0.0.1:1234/v1")
    api_key = api_key or llm_config.get("api_key", "lm-studio")
    test_model = model_name or llm_config.get("test_model", None)
    
    print("=" * 60)
    print("LM Studio Connection Test")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key}")
    if test_model:
        print(f"Test Model: {test_model}")
    print()
    
    try:
        # Create client
        print("1️⃣  Creating OpenAI client...")
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=10.0,  # 10 second timeout
        )
        print("   ✅ Client created successfully")
        print()
        
        # Test 1: List models
        print("2️⃣  Testing API endpoint (listing models)...")
        try:
            models = client.models.list()
            print(f"   ✅ API endpoint accessible")
            print(f"   ✅ Found {len(models.data)} model(s)")
            
            if len(models.data) == 0:
                print("   ⚠️  Warning: No models found. Make sure a model is loaded in LM Studio.")
                return False
            
            # Print available models
            print("\n   Available models:")
            for model in models.data:
                marker = " ← configured" if test_model and model.id == test_model else ""
                print(f"      - {model.id}{marker}")
            print()
            
        except Exception as e:
            print(f"   ❌ Failed to list models: {e}")
            return False
        
        # Test 2: Check if configured model exists
        if test_model:
            print(f"3️⃣  Checking if configured model '{test_model}' is available...")
            model_ids = [m.id for m in models.data]
            if test_model in model_ids:
                print(f"   ✅ Model '{test_model}' is available")
            else:
                print(f"   ⚠️  Warning: Model '{test_model}' not found in available models")
                print(f"   Available models: {', '.join(model_ids)}")
                if len(model_ids) > 0:
                    print(f"   Using first available model: {model_ids[0]}")
                    test_model = model_ids[0]
            print()
        
        # Test 3: Simple completion test
        print("4️⃣  Testing completion request...")
        model_to_use = test_model or models.data[0].id
        print(f"   Using model: {model_to_use}")
        
        try:
            response = client.chat.completions.create(
                model=model_to_use,
                messages=[{"role": "user", "content": "Say 'Hello' if you can hear me."}],
                max_tokens=20,
                temperature=0.1,
            )
            
            response_text = response.choices[0].message.content.strip()
            print(f"   ✅ Completion successful")
            print(f"   Response: {response_text[:100]}")
            print()
            
        except Exception as e:
            print(f"   ❌ Completion test failed: {e}")
            return False
        
        # All tests passed
        print("=" * 60)
        print("✅ All tests passed! LM Studio is ready to use.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Connection test failed!")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure LM Studio is running")
        print("  2. Check that a model is loaded in LM Studio")
        print("  3. Verify the base_url in config.yaml matches LM Studio's API URL")
        print("  4. Check that LM Studio's API server is enabled")
        print("  5. Try accessing the API directly:")
        print(f"     curl {base_url}/models")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test LM Studio connection and availability"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--base-url",
        help="Override base URL from config",
    )
    parser.add_argument(
        "--api-key",
        help="Override API key from config",
    )
    parser.add_argument(
        "--model",
        help="Override model name from config",
    )
    
    args = parser.parse_args()
    
    success = test_lm_studio(
        base_url=args.base_url,
        api_key=args.api_key,
        model_name=args.model,
        config_path=args.config,
    )
    
    sys.exit(0 if success else 1)

