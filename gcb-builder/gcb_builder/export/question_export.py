"""
Question export utilities for GCB Builder.

Exports benchmark versions to JSON format for platform publication.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from gcb_builder.core.categories import TIER_WEIGHTS
from gcb_builder.core.database import get_db
from gcb_builder.core.models import BenchmarkVersion, Question
from gcb_builder.versioning.builder import VersionBuilder


def export_version_to_json(
    version_id: int,
    output_path: Optional[Path] = None,
    include_judge_prompts: bool = True,
) -> Path:
    """
    Export a benchmark version to JSON format.
    
    Args:
        version_id: ID of the version to export
        output_path: Output file path (defaults to data/exports/)
        include_judge_prompts: Whether to include judge prompt templates
        
    Returns:
        Path to the exported file
    """
    builder = VersionBuilder()
    version = builder.get_version(version_id)
    
    if not version:
        raise ValueError(f"Version {version_id} not found")
    
    questions = builder.get_version_questions(version_id)
    stats = builder.get_version_stats(version_id)
    
    # Build export data
    export_data = {
        "format_version": "2.0",
        "benchmark_version": version.version,
        "name": version.name,
        "description": version.description,
        "status": version.status,
        "created_at": version.created_at.isoformat() if version.created_at else None,
        "locked_at": version.locked_at.isoformat() if version.locked_at else None,
        "published_at": version.published_at.isoformat() if version.published_at else None,
        "checksum": version.checksum,
        "questions": [
            _export_question(q) for q in questions
        ],
        "scoring": {
            "weights": {
                "tier1": 0.70,
                "tier2": 0.20,
                "tier3": 0.10,
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
                f"tier{k}": round(v, 1) for k, v in stats.tier_percentages.items()
            },
            "category_counts": stats.category_counts,
            "filter_dimensions": {
                "tests_capability_count": stats.capability_only + stats.both,
                "tests_willingness_count": stats.willingness_only + stats.both,
            },
        },
    }
    
    # Add judge prompts if requested
    if include_judge_prompts:
        export_data["judge_prompts"] = _load_judge_prompts()
    
    # Determine output path
    if output_path is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"gcb-v{version.version}.json"
    
    # Write file
    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)
    
    return output_path


def _export_question(question: Question) -> dict[str, Any]:
    """Convert a question to export format."""
    return {
        "id": question.id,
        "content": question.content,
        "category": question.category,
        "tier": question.tier,
        "difficulty": question.difficulty,
        "expected_verdict": question.expected_verdict,
        "expected_refusal_type": question.expected_refusal_type,
        "tests_capability": question.tests_capability,
        "tests_willingness": question.tests_willingness,
        "use_case_tags": question.use_case_tags_list,
        "audience_context": question.audience_context,
        "ministry_type": question.ministry_type,
    }


def _load_judge_prompts() -> dict[str, str]:
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


def export_questions_csv(
    version_id: int,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Export questions to CSV format.
    
    Args:
        version_id: ID of the version to export
        output_path: Output file path
        
    Returns:
        Path to the exported file
    """
    import csv
    
    builder = VersionBuilder()
    version = builder.get_version(version_id)
    
    if not version:
        raise ValueError(f"Version {version_id} not found")
    
    questions = builder.get_version_questions(version_id)
    
    # Determine output path
    if output_path is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"gcb-v{version.version}-questions.csv"
    
    # Write CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "content", "category", "tier", "difficulty",
            "expected_verdict", "expected_refusal_type",
            "tests_capability", "tests_willingness",
            "use_case_tags", "audience_context", "ministry_type",
        ])
        writer.writeheader()
        
        for q in questions:
            writer.writerow({
                "id": q.id,
                "content": q.content,
                "category": q.category,
                "tier": q.tier,
                "difficulty": q.difficulty,
                "expected_verdict": q.expected_verdict,
                "expected_refusal_type": q.expected_refusal_type or "",
                "tests_capability": q.tests_capability,
                "tests_willingness": q.tests_willingness,
                "use_case_tags": ",".join(q.use_case_tags_list),
                "audience_context": q.audience_context or "",
                "ministry_type": q.ministry_type or "",
            })
    
    return output_path
