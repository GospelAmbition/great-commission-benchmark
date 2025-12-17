"""
Version publisher for GCB Builder.

Handles publishing workflow:
- Version locking
- Checksum generation
- JSON export
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from gcb_builder.core.categories import TIER_WEIGHTS
from gcb_builder.core.database import get_db
from gcb_builder.core.models import BenchmarkVersion
from gcb_builder.versioning.builder import VersionBuilder
from gcb_builder.versioning.validator import VersionValidator, ValidationResult


class VersionPublisher:
    """
    Publishes benchmark versions.
    
    Workflow:
    1. Validate version
    2. Lock version
    3. Generate checksum
    4. Export to JSON
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize publisher.
        
        Args:
            output_dir: Directory for export files. Defaults to data/exports/
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "data" / "exports"
        self.output_dir = output_dir
        self.builder = VersionBuilder()
        self.validator = VersionValidator()
    
    def validate(self, version_id: int) -> ValidationResult:
        """Validate a version before publishing."""
        return self.validator.validate(version_id)
    
    def lock_version(self, version_id: int, force: bool = False) -> tuple[bool, str]:
        """
        Lock a version for publishing.
        
        Args:
            version_id: Version ID
            force: If True, skip validation
            
        Returns:
            Tuple of (success, message)
        """
        version = self.builder.get_version(version_id)
        if not version:
            return False, f"Version {version_id} not found"
        
        if version.status == "locked":
            return False, "Version is already locked"
        
        if version.status == "published":
            return False, "Version is already published"
        
        if version.status not in ("building", "validating"):
            return False, f"Cannot lock version in status '{version.status}'"
        
        # Validate unless forced
        if not force:
            result = self.validate(version_id)
            if not result.is_valid:
                error_messages = [i.message for i in result.errors]
                return False, f"Validation failed: {'; '.join(error_messages)}"
        
        # Generate checksum
        checksum = self._generate_checksum(version_id)
        
        # Lock the version
        with get_db() as db:
            v = db.get(BenchmarkVersion, version_id)
            v.status = "locked"
            v.locked_at = datetime.utcnow()
            v.checksum = checksum
            db.commit()
        
        return True, f"Version {version.version} locked successfully"
    
    def publish_version(self, version_id: int) -> tuple[bool, str]:
        """
        Publish a locked version.
        
        Args:
            version_id: Version ID
            
        Returns:
            Tuple of (success, message)
        """
        version = self.builder.get_version(version_id)
        if not version:
            return False, f"Version {version_id} not found"
        
        if version.status != "locked":
            return False, f"Version must be locked before publishing (current: {version.status})"
        
        # Export to JSON
        try:
            export_path = self.export_json(version_id)
        except Exception as e:
            return False, f"Export failed: {str(e)}"
        
        # Update status
        with get_db() as db:
            v = db.get(BenchmarkVersion, version_id)
            v.status = "published"
            v.published_at = datetime.utcnow()
            db.commit()
        
        return True, f"Version {version.version} published to {export_path}"
    
    def export_json(self, version_id: int) -> Path:
        """
        Export a version to JSON format.
        
        Args:
            version_id: Version ID
            
        Returns:
            Path to the exported file
        """
        version = self.builder.get_version(version_id)
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        questions = self.builder.get_version_questions(version_id)
        stats = self.builder.get_version_stats(version_id)
        
        # Load judge prompts
        judge_prompts = self._load_judge_prompts()
        
        # Build export data
        export_data = {
            "format_version": "2.0",
            "benchmark_version": version.version,
            "name": version.name,
            "description": version.description,
            "locked_at": version.locked_at.isoformat() if version.locked_at else None,
            "questions": [
                {
                    "id": q.id,
                    "content": q.content,
                    "category": q.category,
                    "tier": q.tier,
                    "difficulty": q.difficulty,
                    "expected_verdict": q.expected_verdict,
                    "expected_refusal_type": q.expected_refusal_type,
                    "tests_capability": q.tests_capability,
                    "tests_willingness": q.tests_willingness,
                    "use_case_tags": q.use_case_tags_list,
                    "audience_context": q.audience_context,
                    "ministry_type": q.ministry_type,
                }
                for q in questions
            ],
            "judge_prompts": judge_prompts,
            "scoring": {
                "weights": {
                    "tier1": TIER_WEIGHTS.get(1, 0.70),
                    "tier2": TIER_WEIGHTS.get(2, 0.20),
                    "tier3": TIER_WEIGHTS.get(3, 0.10),
                },
                "formula": "(tier1_score * 0.70) + (tier2_score * 0.20) + (tier3_score * 0.10)",
                "rationale": "70/20/10 weighting prioritizes practical task capability",
                "refusal_analysis": {
                    "enabled": True,
                    "types": ["capability", "safety", "ideological", "unclear"],
                    "report_breakdown": True,
                },
            },
            "metadata": {
                "total_questions": stats.total_questions,
                "tier_counts": stats.tier_counts,
                "tier_percentages": {
                    f"tier{k}": v for k, v in stats.tier_percentages.items()
                },
                "category_counts": stats.category_counts,
                "checksum": version.checksum,
                "filter_dimensions": {
                    "use_case_tags": self._get_unique_tags(questions),
                    "audience_contexts": self._get_unique_values(questions, "audience_context"),
                    "ministry_types": self._get_unique_values(questions, "ministry_type"),
                    "tests_capability_count": stats.capability_only + stats.both,
                    "tests_willingness_count": stats.willingness_only + stats.both,
                },
            },
            "reporting": {
                "supported_filters": [
                    "by_tier",
                    "by_category",
                    "by_use_case_tag",
                    "by_audience_context",
                    "by_ministry_type",
                    "by_capability_vs_willingness",
                    "by_refusal_type",
                ],
            },
        }
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write file
        filename = f"gcb-v{version.version}.json"
        output_path = self.output_dir / filename
        
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        return output_path
    
    def _generate_checksum(self, version_id: int) -> str:
        """Generate a checksum for the version content."""
        questions = self.builder.get_version_questions(version_id)
        
        # Sort questions by ID for deterministic ordering
        questions.sort(key=lambda q: q.id)
        
        # Build content string
        content_parts = []
        for q in questions:
            content_parts.append(
                f"{q.id}:{q.content}:{q.category}:{q.expected_verdict}"
            )
        
        content_string = "\n".join(content_parts)
        
        # Generate SHA-256 hash
        hash_obj = hashlib.sha256(content_string.encode("utf-8"))
        return f"sha256:{hash_obj.hexdigest()}"
    
    def _load_judge_prompts(self) -> dict[str, str]:
        """Load judge prompt templates."""
        prompts = {}
        prompts_dir = Path(__file__).parent.parent.parent / "judge_prompts"
        
        prompt_files = {
            "tier1_task": "tier1_task.md",
            "tier2_doctrine": "tier2_doctrine.md",
            "tier3_worldview": "tier3_worldview.md",
        }
        
        for key, filename in prompt_files.items():
            path = prompts_dir / filename
            if path.exists():
                prompts[key] = path.read_text()
            else:
                prompts[key] = ""
        
        return prompts
    
    def _get_unique_tags(self, questions: list) -> list[str]:
        """Get unique use case tags from questions."""
        tags = set()
        for q in questions:
            if q.use_case_tags:
                for tag in q.use_case_tags_list:
                    tags.add(tag)
        return sorted(tags)
    
    def _get_unique_values(self, questions: list, attr: str) -> list[str]:
        """Get unique values for an attribute."""
        values = set()
        for q in questions:
            value = getattr(q, attr, None)
            if value:
                values.add(value)
        return sorted(values)


def publish_version(version_id: int, force: bool = False) -> tuple[bool, str, Optional[Path]]:
    """
    Convenience function to publish a version.
    
    Returns:
        Tuple of (success, message, export_path)
    """
    publisher = VersionPublisher()
    
    # Lock first
    success, message = publisher.lock_version(version_id, force=force)
    if not success:
        return False, message, None
    
    # Then publish
    success, message = publisher.publish_version(version_id)
    if not success:
        return False, message, None
    
    # Get export path
    version = publisher.builder.get_version(version_id)
    export_path = publisher.output_dir / f"gcb-v{version.version}.json"
    
    return True, message, export_path
