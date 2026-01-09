"""Tests for export and validation."""

import json

import pytest

from gcb_runner.export import validate_export


class TestValidation:
    """Tests for export validation."""
    
    def test_valid_export(self):
        """Test validation of a valid export."""
        export_data = {
            "format_version": "1.0",
            "test_run": {
                "id": "local-1",
                "model": "gpt-4o",
                "backend": "openrouter",
                "benchmark_version": "2.0",
                "judge_model": "gpt-4o",
                "completed_at": "2025-01-15T14:32:01Z"
            },
            "summary": {
                "total_questions": 3,
                "score": 77.8,
                "scoring_weights": {
                    "tier1": 0.70,
                    "tier2": 0.20,
                    "tier3": 0.10
                },
                "tier_scores": {
                    "tier1": {"raw": 75.0, "weighted": 52.5, "questions": 1},
                    "tier2": {"raw": 83.0, "weighted": 16.6, "questions": 1},
                    "tier3": {"raw": 87.0, "weighted": 8.7, "questions": 1}
                },
                "verdict_counts": {
                    "ACCEPTED": 2,
                    "COMPROMISED": 1,
                    "REFUSED": 0
                }
            },
            "responses": [
                {
                    "question_id": 1,
                    "tier": 1,
                    "category": "1.1",
                    "response": "Test response",
                    "verdict": "ACCEPTED",
                    "judge_reasoning": "Good response"
                },
                {
                    "question_id": 2,
                    "tier": 2,
                    "category": "2.1",
                    "response": "Test response 2",
                    "verdict": "ACCEPTED",
                    "judge_reasoning": "Good response"
                },
                {
                    "question_id": 3,
                    "tier": 3,
                    "category": "3.1",
                    "response": "Test response 3",
                    "verdict": "COMPROMISED",
                    "judge_reasoning": "Partial response"
                }
            ],
            "metadata": {
                "cli_version": "0.1.0",
                "benchmark_version": "2.0",
                "benchmark_checksum": "sha256:abc123",
                "timestamp": "2025-01-15T14:35:00Z"
            }
        }
        
        errors = validate_export(export_data)
        assert errors == []
    
    def test_missing_required_field(self):
        """Test validation with missing required field."""
        export_data = {
            "format_version": "1.0",
            # Missing test_run
            "summary": {},
            "responses": [],
            "metadata": {}
        }
        
        errors = validate_export(export_data)
        assert len(errors) > 0
        assert any("test_run" in e for e in errors)
    
    def test_question_count_mismatch(self):
        """Test validation with question count mismatch."""
        export_data = {
            "format_version": "1.0",
            "test_run": {
                "id": "local-1",
                "model": "gpt-4o",
                "backend": "openrouter",
                "benchmark_version": "2.0",
                "judge_model": "gpt-4o",
                "completed_at": "2025-01-15T14:32:01Z"
            },
            "summary": {
                "total_questions": 10,  # Says 10 but only 1 response
                "score": 77.8,
                "scoring_weights": {"tier1": 0.70, "tier2": 0.20, "tier3": 0.10},
                "tier_scores": {
                    "tier1": {"raw": 75.0, "weighted": 52.5, "questions": 1},
                    "tier2": {"raw": 0, "weighted": 0, "questions": 0},
                    "tier3": {"raw": 0, "weighted": 0, "questions": 0}
                },
                "verdict_counts": {"ACCEPTED": 1, "COMPROMISED": 0, "REFUSED": 0}
            },
            "responses": [
                {"question_id": 1, "tier": 1, "response": "Test", "verdict": "ACCEPTED", "judge_reasoning": "OK"}
            ],
            "metadata": {
                "cli_version": "0.1.0",
                "benchmark_version": "2.0",
                "benchmark_checksum": "sha256:abc123",
                "timestamp": "2025-01-15T14:35:00Z"
            }
        }
        
        errors = validate_export(export_data)
        assert any("count mismatch" in e.lower() for e in errors)
    
    def test_invalid_verdict_for_tier(self):
        """Test validation with invalid verdict."""
        export_data = {
            "format_version": "1.0",
            "test_run": {
                "id": "local-1",
                "model": "gpt-4o",
                "backend": "openrouter",
                "benchmark_version": "2.0",
                "judge_model": "gpt-4o",
                "completed_at": "2025-01-15T14:32:01Z"
            },
            "summary": {
                "total_questions": 1,
                "score": 70.0,
                "scoring_weights": {"tier1": 0.70, "tier2": 0.20, "tier3": 0.10},
                "tier_scores": {
                    "tier1": {"raw": 100.0, "weighted": 70.0, "questions": 1},
                    "tier2": {"raw": 0, "weighted": 0, "questions": 0},
                    "tier3": {"raw": 0, "weighted": 0, "questions": 0}
                },
                "verdict_counts": {"ACCEPTED": 1, "COMPROMISED": 0, "REFUSED": 0}
            },
            "responses": [
                {
                    "question_id": 1,
                    "tier": 1,
                    "response": "Test",
                    "verdict": "LOYAL",  # Invalid - only ACCEPTED/COMPROMISED/REFUSED are valid
                    "judge_reasoning": "OK"
                }
            ],
            "metadata": {
                "cli_version": "0.1.0",
                "benchmark_version": "2.0",
                "benchmark_checksum": "sha256:abc123",
                "timestamp": "2025-01-15T14:35:00Z"
            }
        }
        
        errors = validate_export(export_data)
        assert any("invalid verdict" in e.lower() for e in errors)
    
    def test_weight_sum_validation(self):
        """Test validation of weight sum."""
        export_data = {
            "format_version": "1.0",
            "test_run": {
                "id": "local-1",
                "model": "gpt-4o",
                "backend": "openrouter",
                "benchmark_version": "2.0",
                "judge_model": "gpt-4o",
                "completed_at": "2025-01-15T14:32:01Z"
            },
            "summary": {
                "total_questions": 1,
                "score": 70.0,
                "scoring_weights": {
                    "tier1": 0.50,  # Sum = 0.8, not 1.0
                    "tier2": 0.20,
                    "tier3": 0.10
                },
                "tier_scores": {
                    "tier1": {"raw": 100.0, "weighted": 50.0, "questions": 1},
                    "tier2": {"raw": 0, "weighted": 0, "questions": 0},
                    "tier3": {"raw": 0, "weighted": 0, "questions": 0}
                },
                "verdict_counts": {"ACCEPTED": 1, "COMPROMISED": 0, "REFUSED": 0}
            },
            "responses": [
                {"question_id": 1, "tier": 1, "response": "Test", "verdict": "ACCEPTED", "judge_reasoning": "OK"}
            ],
            "metadata": {
                "cli_version": "0.1.0",
                "benchmark_version": "2.0",
                "benchmark_checksum": "sha256:abc123",
                "timestamp": "2025-01-15T14:35:00Z"
            }
        }
        
        errors = validate_export(export_data)
        assert any("weights must sum to 1.0" in e.lower() for e in errors)
