#!/usr/bin/env python3
"""Test script to verify API key permissions."""

import sys
from pathlib import Path

# Add gcb-runner to path
sys.path.insert(0, str(Path(__file__).parent / "gcb-runner"))

from gcb_runner.api.client import get_user_info_sync
from gcb_runner.config import Config

API_KEY = "gcb_f8c6e6d30b965176b820da89909151a111333bec0cc482567995e6a5415d0a4b"

print("Testing API key permissions...")
print(f"API Key: {API_KEY[:20]}...")
print()

# Get the configured URL, but also try production URL
try:
    config = Config.load()
    configured_url = config.platform.url if config.platform.url else None
    if configured_url:
        print(f"Configured URL: {configured_url}")
    print(f"Will also try production URL: https://api.greatcommissionbenchmark.ai")
    print()
except Exception as e:
    print(f"Could not load config: {e}")
    configured_url = None
    print()

# Try production URL first (this should work if it's properly configured)
base_url = "https://api.greatcommissionbenchmark.ai"
print(f"Testing with: {base_url}")
print()

# Use the actual client function
print("Calling get_user_info_sync...")
result = get_user_info_sync(API_KEY, base_url)

if result is None:
    print("❌ ERROR: get_user_info_sync returned None")
    print("   This could mean:")
    print("   - Invalid API key")
    print("   - Network error")
    print("   - Wrong endpoint URL")
    print()
    print("Trying direct HTTP call to debug...")
    import httpx
    
    # Test connectivity first - try various path combinations
    urls_to_try = [
        (base_url, "/health"),
        (base_url, "/api/runner/user-info"),
        (base_url, "/api/v1/runner/user-info"),
        (base_url, "/runner/user-info"),
    ]
    if configured_url:
        urls_to_try.extend([
            (configured_url, "/health"),
            (configured_url, "/api/runner/user-info"),
            (configured_url, "/api/v1/runner/user-info"),
            (configured_url, "/runner/user-info"),
            (configured_url, "/v1/runner/user-info"),
        ])
    
    result = None
    for test_url, endpoint in urls_to_try:
        try:
            print(f"Trying {test_url}{endpoint}...")
            with httpx.Client(
                base_url=test_url.rstrip("/"),
                headers={
                    "X-API-Key": API_KEY,
                    "User-Agent": "gcb-runner/0.1.1",
                },
                timeout=10.0,
                verify=False,
            ) as client:
                response = client.get(endpoint)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    if endpoint == "/api/runner/user-info":
                        result = response.json()
                        print("✅ Got result!")
                        break
                    else:
                        print(f"  Response: {response.text[:100]}")
                elif response.status_code == 401:
                    print(f"  ❌ Unauthorized - API key may be invalid")
                elif response.status_code == 404:
                    print(f"  ❌ Not Found - endpoint doesn't exist")
                else:
                    print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
    
    if result is None:
        print()
        print("❌ Could not fetch user info from any URL/endpoint combination")
        sys.exit(1)

print("✅ Successfully fetched user info:")
print()
print(f"  Role: {result.get('role', 'N/A')}")
print(f"  Email: {result.get('email', 'N/A')}")
print(f"  Name: {result.get('name', 'N/A')}")
print()
print("Permission Flags:")
print(f"  is_admin: {result.get('is_admin', False)}")
print(f"  is_benchmark_developer: {result.get('is_benchmark_developer', False)}")
print(f"  is_moderator: {result.get('is_moderator', False)}")
print()

# Check elevated access
has_elevated = result.get('is_admin', False) or result.get('is_benchmark_developer', False)

if has_elevated:
    print("✅ ELEVATED ACCESS: This API key has elevated permissions")
    print("   The viewer should show full responses and question text")
else:
    print("⚠️  STANDARD ACCESS: This API key has standard user permissions")
    print("   The viewer will truncate responses and hide question text")

print()
print("Full response:")
import json
print(json.dumps(result, indent=2))

