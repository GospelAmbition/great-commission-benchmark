#!/usr/bin/env python3
"""
Generate SHA256 hashes for GCB Runner executables.

This is a standalone utility for generating hashes when you already have
built executables. The build.py script generates these automatically.

Usage:
    python scripts/generate_hashes.py dist/release/
    python scripts/generate_hashes.py path/to/gcb-runner-macos-arm64
"""

import hashlib
import json
import sys
from pathlib import Path


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_hashes.py <file_or_directory>")
        print()
        print("Examples:")
        print("  python generate_hashes.py dist/release/")
        print("  python generate_hashes.py dist/release/gcb-runner-macos-arm64")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)
    
    if target.is_file():
        files = [target]
    else:
        # Find all gcb-runner executables in directory
        files = [f for f in target.iterdir() 
                 if f.name.startswith("gcb-runner") and f.suffix != ".json"]
    
    if not files:
        print(f"No gcb-runner executables found in {target}")
        sys.exit(1)
    
    hashes = {}
    
    print("SHA256 Hashes")
    print("=============")
    print()
    
    for file in sorted(files):
        hash_value = calculate_sha256(file)
        size_mb = file.stat().st_size / (1024 * 1024)
        hashes[file.name] = {
            "sha256": hash_value,
            "size": file.stat().st_size,
            "size_mb": f"{size_mb:.1f} MB"
        }
        print(f"{file.name}:")
        print(f"  SHA256: {hash_value}")
        print(f"  Size: {size_mb:.1f} MB")
        print()
    
    # Output as JSON for easy copying
    print()
    print("JSON format:")
    print(json.dumps(hashes, indent=2))


if __name__ == "__main__":
    main()
