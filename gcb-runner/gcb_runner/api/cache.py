"""Local caching for benchmark questions."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast

from gcb_runner.config import get_cache_dir


class QuestionCache:
    """Local cache for benchmark questions and prompts."""
    
    CACHE_TTL_DAYS = 7
    
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or get_cache_dir()
    
    def _get_version_dir(self, version: str) -> Path:
        """Get the cache directory for a specific version."""
        version_dir = self.cache_dir / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        return version_dir
    
    def _read_metadata(self, version: str) -> dict[str, Any] | None:
        """Read metadata for a cached version."""
        meta_path = self._get_version_dir(version) / "metadata.json"
        if meta_path.exists():
            try:
                return cast(dict[str, Any], json.loads(meta_path.read_text()))
            except (json.JSONDecodeError, OSError):
                pass
        return None
    
    def is_stale(self, version: str) -> bool:
        """Check if the cache for a version is stale."""
        metadata = self._read_metadata(version)
        if not metadata:
            return True
        
        cached_at = metadata.get("cached_at")
        if not cached_at:
            return True
        
        try:
            cached_time = datetime.fromisoformat(cached_at)
            return datetime.now() - cached_time > timedelta(days=self.CACHE_TTL_DAYS)
        except ValueError:
            return True
    
    def get(self, version: str) -> dict[str, Any] | None:
        """Get cached questions for a version."""
        version_dir = self._get_version_dir(version)
        questions_path = version_dir / "questions.json"
        
        if not questions_path.exists():
            return None
        
        try:
            return cast(dict[str, Any], json.loads(questions_path.read_text()))
        except (json.JSONDecodeError, OSError):
            return None
    
    def get_judge_prompts(self, version: str) -> dict[str, str] | None:
        """Get cached judge prompts for a version."""
        version_dir = self._get_version_dir(version)
        prompts_path = version_dir / "judge-prompts.json"
        
        if not prompts_path.exists():
            return None
        
        try:
            return cast(dict[str, str], json.loads(prompts_path.read_text()))
        except (json.JSONDecodeError, OSError):
            return None
    
    def store(self, version: str, data: dict[str, Any]) -> None:
        """Store questions for a version in the cache."""
        version_dir = self._get_version_dir(version)
        
        # Store questions
        questions_path = version_dir / "questions.json"
        questions_path.write_text(json.dumps(data, indent=2))
        
        # Store judge prompts separately if present
        if "judge_prompts" in data:
            prompts_path = version_dir / "judge-prompts.json"
            prompts_path.write_text(json.dumps(data["judge_prompts"], indent=2))
        
        # Update metadata
        version_data = data.get("version")
        checksum = version_data.get("checksum") if isinstance(version_data, dict) else None
        metadata = {
            "version": version,
            "cached_at": datetime.now().isoformat(),
            "checksum": checksum,
            "question_count": len(data.get("questions", [])),
        }
        meta_path = version_dir / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2))
    
    def get_versions_list(self) -> dict[str, Any] | None:
        """Get cached versions list."""
        versions_path = self.cache_dir / "versions.json"
        if not versions_path.exists():
            return None
        
        try:
            data = cast(dict[str, Any], json.loads(versions_path.read_text()))
            # Check if stale
            cached_at = data.get("_cached_at")
            if cached_at:
                cached_time = datetime.fromisoformat(cached_at)
                if datetime.now() - cached_time > timedelta(days=1):  # 1 day TTL for versions list
                    return None
            return data
        except (json.JSONDecodeError, OSError, ValueError):
            return None
    
    def store_versions_list(self, data: dict[str, Any]) -> None:
        """Store versions list in cache."""
        versions_path = self.cache_dir / "versions.json"
        data["_cached_at"] = datetime.now().isoformat()
        versions_path.write_text(json.dumps(data, indent=2))
    
    def clear(self, version: str | None = None) -> None:
        """Clear cache for a specific version or all versions."""
        if version:
            version_dir = self._get_version_dir(version)
            if version_dir.exists():
                import shutil
                shutil.rmtree(version_dir)
        else:
            # Clear all
            if self.cache_dir.exists():
                import shutil
                for item in self.cache_dir.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
