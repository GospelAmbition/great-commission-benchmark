#!/usr/bin/env python3
"""
Build script for creating GCB Runner standalone executables.

This script uses PyInstaller to create single-file executables that can be
distributed without requiring users to have Python installed.

Usage:
    python scripts/build.py                    # Build for current platform
    python scripts/build.py --platform macos   # Build for macOS
    python scripts/build.py --platform linux   # Build for Linux
    python scripts/build.py --platform windows # Build for Windows
    python scripts/build.py --all              # Build for all platforms (requires cross-compilation setup)

Requirements:
    pip install pyinstaller

Note: Cross-platform builds require running on the target platform or using
      a CI system like GitHub Actions that can run on multiple platforms.
"""

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_version() -> str:
    """Get the current version from __init__.py."""
    init_file = get_project_root() / "gcb_runner" / "__init__.py"
    content = init_file.read_text()
    for line in content.splitlines():
        if line.startswith("__version__"):
            # Extract version from: __version__ = "0.1.0"
            return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"


def get_platform_name() -> str:
    """Get the current platform name for the build."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine == "arm64":
            return "macos-arm64"
        return "macos-x64"
    elif system == "linux":
        if machine == "aarch64":
            return "linux-arm64"
        return "linux-x64"
    elif system == "windows":
        return "windows-x64"
    else:
        return f"{system}-{machine}"


def get_executable_name(platform_name: str) -> str:
    """Get the executable filename for a platform."""
    if platform_name.startswith("windows"):
        return "gcb-runner.exe"
    return f"gcb-runner-{platform_name}"


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def build_executable(output_dir: Path) -> Path:
    """Build the executable using PyInstaller."""
    project_root = get_project_root()
    spec_file = project_root / "gcb-runner.spec"
    
    if not spec_file.exists():
        print(f"Error: Spec file not found at {spec_file}")
        sys.exit(1)
    
    # Clean previous builds
    build_dir = project_root / "build"
    dist_dir = project_root / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Run PyInstaller
    print("Running PyInstaller...")
    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            str(spec_file)
        ],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("PyInstaller failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    
    # Find the built executable
    built_exe = dist_dir / "gcb-runner"
    if platform.system() == "Windows":
        built_exe = dist_dir / "gcb-runner.exe"
    
    if not built_exe.exists():
        print(f"Error: Built executable not found at {built_exe}")
        print(f"Contents of dist: {list(dist_dir.iterdir()) if dist_dir.exists() else 'directory not found'}")
        sys.exit(1)
    
    # Move to output directory with platform-specific name
    output_dir.mkdir(parents=True, exist_ok=True)
    platform_name = get_platform_name()
    final_name = get_executable_name(platform_name)
    final_path = output_dir / final_name
    
    shutil.move(str(built_exe), str(final_path))
    
    # Make executable on Unix
    if platform.system() != "Windows":
        final_path.chmod(0o755)
    
    print(f"Built: {final_path}")
    print(f"Size: {final_path.stat().st_size / (1024*1024):.1f} MB")
    
    return final_path


def generate_manifest(output_dir: Path, executables: list[Path]) -> Path:
    """Generate manifest.json with version info and hashes."""
    version = get_version()
    
    downloads = {}
    for exe_path in executables:
        # Determine platform from filename
        name = exe_path.name
        if name == "gcb-runner.exe":
            platform_key = "windows-x64"
        else:
            # Extract platform from gcb-runner-{platform}
            platform_key = name.replace("gcb-runner-", "")
        
        downloads[platform_key] = {
            "filename": name,
            "sha256": calculate_sha256(exe_path),
            "size": exe_path.stat().st_size,
        }
    
    manifest = {
        "version": version,
        "released_at": datetime.now(timezone.utc).isoformat(),
        "downloads": downloads,
        "release_notes": f"GCB Runner v{version}",
        "minimum_version": "0.1.0",  # Minimum version that supports auto-update
    }
    
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    print(f"Generated manifest: {manifest_path}")
    return manifest_path


def main():
    parser = argparse.ArgumentParser(description="Build GCB Runner executables")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("dist/release"),
        help="Output directory for built executables (default: dist/release)"
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Only generate manifest from existing executables in output directory"
    )
    args = parser.parse_args()
    
    project_root = get_project_root()
    output_dir = project_root / args.output
    
    print(f"GCB Runner Build Script")
    print(f"=======================")
    print(f"Version: {get_version()}")
    print(f"Platform: {get_platform_name()}")
    print(f"Output: {output_dir}")
    print()
    
    if args.manifest_only:
        # Find existing executables
        executables = list(output_dir.glob("gcb-runner*"))
        executables = [e for e in executables if e.suffix != ".json"]
        if not executables:
            print(f"No executables found in {output_dir}")
            sys.exit(1)
        print(f"Found {len(executables)} executable(s)")
    else:
        # Check for PyInstaller
        try:
            import PyInstaller
            print(f"PyInstaller version: {PyInstaller.__version__}")
        except ImportError:
            print("Error: PyInstaller not installed")
            print("Install with: pip install pyinstaller")
            sys.exit(1)
        
        # Build executable
        exe_path = build_executable(output_dir)
        executables = [exe_path]
    
    print()
    
    # Generate manifest
    manifest_path = generate_manifest(output_dir, executables)
    
    print()
    print("Build complete!")
    print()
    print("Files to upload to frontend/public/downloads/:")
    for exe in executables:
        print(f"  - {exe.name}")
    print(f"  - {manifest_path.name}")


if __name__ == "__main__":
    main()
