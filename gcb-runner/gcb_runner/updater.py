"""
Auto-update functionality for GCB Runner.

This module handles checking for updates, downloading new versions,
and applying updates for the standalone executable distribution.
"""

import contextlib
import hashlib
import os
import platform
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

import httpx

from gcb_runner import __version__

# Update check URL - points to the platform API
DEFAULT_UPDATE_URL = "https://greatcommissionbenchmark.ai/api/runner/latest"
# Fallback to static manifest if API is unavailable
FALLBACK_MANIFEST_URL = "https://greatcommissionbenchmark.ai/downloads/manifest.json"


def get_platform_key() -> str:
    """Get the platform key for the current system."""
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


def is_frozen() -> bool:
    """Check if running as a frozen (PyInstaller) executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_executable_path() -> Path | None:
    """Get the path to the current executable if frozen."""
    if is_frozen():
        return Path(sys.executable)
    return None


def parse_version(version: str) -> tuple[int, ...]:
    """Parse a semantic version string into a tuple for comparison."""
    # Handle versions like "0.1.0" or "0.1.0-beta.1"
    base_version = version.split("-")[0]
    try:
        return tuple(int(x) for x in base_version.split("."))
    except ValueError:
        return (0, 0, 0)


def is_newer_version(remote_version: str, local_version: str) -> bool:
    """Check if the remote version is newer than the local version."""
    return parse_version(remote_version) > parse_version(local_version)


async def check_for_updates(update_url: str | None = None) -> dict[str, Any] | None:
    """
    Check if a newer version is available.
    
    Returns:
        dict with update info if available, None if no update or check failed.
        {
            "current_version": "0.1.0",
            "latest_version": "0.2.0",
            "download_url": "https://...",
            "sha256": "abc123...",
            "release_notes": "...",
        }
    """
    if not is_frozen():
        # Don't check for updates when running from source
        return None
    
    urls_to_try = [update_url] if update_url else [DEFAULT_UPDATE_URL, FALLBACK_MANIFEST_URL]
    platform_key = get_platform_key()
    manifest = None
    
    for url in urls_to_try:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                manifest = response.json()
                break
        except Exception:
            continue
    
    if not manifest:
        # All URLs failed
        return None
    
    remote_version = manifest.get("version", "0.0.0")
    
    if not is_newer_version(remote_version, __version__):
        return None
    
    # Check if we have a download for this platform
    downloads = manifest.get("downloads", {})
    platform_download = downloads.get(platform_key)
    
    if not platform_download:
        return None
    
    # Get the download URL - API response includes full URL, manifest needs to build it
    download_url = platform_download.get("url", "")
    if not download_url:
        # Fallback: build URL from filename (for static manifest)
        filename = platform_download.get("filename", "")
        if filename:
            base_url = urls_to_try[0].rsplit("/", 1)[0]
            download_url = f"{base_url}/{filename}"
    
    if not download_url:
        return None
    
    return {
        "current_version": __version__,
        "latest_version": remote_version,
        "download_url": download_url,
        "sha256": platform_download.get("sha256", ""),
        "size": platform_download.get("size", 0),
        "release_notes": manifest.get("release_notes", ""),
    }


def check_for_updates_sync(update_url: str | None = None) -> dict[str, Any] | None:
    """Synchronous version of check_for_updates."""
    import asyncio
    
    try:
        return asyncio.run(check_for_updates(update_url))
    except Exception:
        return None


def calculate_sha256(filepath: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


async def download_update(
    download_url: str,
    expected_sha256: str,
    progress_callback: Any | None = None,
) -> Path | None:
    """
    Download an update and verify its hash.
    
    Args:
        download_url: URL to download from
        expected_sha256: Expected SHA256 hash of the download
        progress_callback: Optional callable(downloaded_bytes, total_bytes)
    
    Returns:
        Path to the downloaded file if successful, None otherwise.
    """
    try:
        # Create temp file for download
        fd, temp_path = tempfile.mkstemp(prefix="gcb-runner-update-")
        os.close(fd)
        temp_file = Path(temp_path)
        
        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:  # noqa: SIM117
            async with client.stream("GET", download_url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                
                with open(temp_file, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
        
        # Verify hash
        actual_hash = calculate_sha256(temp_file)
        if actual_hash.lower() != expected_sha256.lower():
            temp_file.unlink()
            return None
        
        return temp_file
        
    except Exception:
        # Clean up on error
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return None


def download_update_sync(
    download_url: str,
    expected_sha256: str,
    progress_callback: Any | None = None,
) -> Path | None:
    """Synchronous version of download_update."""
    import asyncio
    
    try:
        return asyncio.run(download_update(download_url, expected_sha256, progress_callback))
    except Exception:
        return None


def apply_update(new_executable: Path) -> bool:
    """
    Replace the current executable with the new one.
    
    This function handles the tricky process of replacing a running executable.
    On Unix, we can directly replace the file. On Windows, we rename the old
    executable and copy the new one.
    
    Args:
        new_executable: Path to the new executable file
    
    Returns:
        True if successful, False otherwise.
    """
    current_exe = get_executable_path()
    
    if not current_exe:
        return False
    
    try:
        if platform.system() == "Windows":
            # On Windows, rename the old executable first
            old_exe = current_exe.with_suffix(".old")
            if old_exe.exists():
                old_exe.unlink()
            current_exe.rename(old_exe)
            shutil.copy2(new_executable, current_exe)
            # Clean up
            new_executable.unlink()
            # Note: old_exe cleanup happens on next launch
        else:
            # On Unix, we can directly replace
            shutil.copy2(new_executable, current_exe)
            # Make executable
            current_exe.chmod(current_exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            new_executable.unlink()
        
        return True
        
    except Exception:
        return False


def cleanup_old_executable() -> None:
    """Clean up old executable files from previous updates (Windows only)."""
    if platform.system() != "Windows":
        return
    
    current_exe = get_executable_path()
    if not current_exe:
        return
    
    old_exe = current_exe.with_suffix(".old")
    if old_exe.exists():
        with contextlib.suppress(Exception):
            old_exe.unlink()


def format_size(size_bytes: int) -> str:
    """Format a size in bytes as a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
