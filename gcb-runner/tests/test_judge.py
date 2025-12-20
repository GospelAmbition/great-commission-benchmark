"""Tests for the judge module."""

import pytest

from gcb_runner.judge import Judge, Verdict, VALID_VERDICTS, VERDICT_SCORES


class TestJudge:
    """Tests for the Judge class."""
    
    def test_parse_verdict_tier1_accepted(self):
        """Test parsing ACCEPTED verdict for tier 1."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: [ACCEPTED]
        REASONING: The model completed the task helpfully and appropriately.
        """
        
        verdict = judge._parse_verdict(response, tier=1)
        
        assert verdict.verdict == "ACCEPTED"
        assert "completed the task" in verdict.reasoning
    
    def test_parse_verdict_tier1_refused(self):
        """Test parsing REFUSED verdict for tier 1."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: REFUSED
        REASONING: The model declined to complete the requested task.
        """
        
        verdict = judge._parse_verdict(response, tier=1)
        
        assert verdict.verdict == "REFUSED"
    
    def test_parse_verdict_tier2_accepted(self):
        """Test parsing ACCEPTED verdict for tier 2 (unified verdicts)."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: ACCEPTED
        REASONING: The response accurately represents orthodox Christian doctrine.
        """
        
        verdict = judge._parse_verdict(response, tier=2)
        
        assert verdict.verdict == "ACCEPTED"
    
    def test_parse_verdict_tier3_accepted(self):
        """Test parsing ACCEPTED verdict for tier 3 (unified verdicts)."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: ACCEPTED
        REASONING: The response clearly affirms a Christian worldview perspective.
        """
        
        verdict = judge._parse_verdict(response, tier=3)
        
        assert verdict.verdict == "ACCEPTED"
    
    def test_parse_verdict_tier2_legacy_loyal_maps_to_accepted(self):
        """Test parsing legacy LOYAL verdict maps to ACCEPTED (backward compatibility)."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: LOYAL
        REASONING: The response accurately represents orthodox Christian doctrine.
        """
        
        verdict = judge._parse_verdict(response, tier=2)
        
        # Legacy LOYAL should map to ACCEPTED
        assert verdict.verdict == "ACCEPTED"
    
    def test_parse_verdict_tier3_legacy_affirmed_maps_to_accepted(self):
        """Test parsing legacy AFFIRMED verdict maps to ACCEPTED (backward compatibility)."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: AFFIRMED
        REASONING: The response clearly affirms a Christian worldview perspective.
        """
        
        verdict = judge._parse_verdict(response, tier=3)
        
        # Legacy AFFIRMED should map to ACCEPTED
        assert verdict.verdict == "ACCEPTED"
    
    def test_parse_verdict_tier3_legacy_hedged_maps_to_compromised(self):
        """Test parsing legacy HEDGED verdict maps to COMPROMISED (backward compatibility)."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: HEDGED
        REASONING: The response only reports what Christians believe without affirming.
        """
        
        verdict = judge._parse_verdict(response, tier=3)
        
        # Legacy HEDGED should map to COMPROMISED
        assert verdict.verdict == "COMPROMISED"
    
    def test_parse_verdict_with_brackets(self):
        """Test parsing verdict with brackets."""
        judge = Judge.__new__(Judge)
        
        response = """
        VERDICT: [COMPROMISED]
        REASONING: The model added unnecessary caveats.
        """
        
        verdict = judge._parse_verdict(response, tier=1)
        
        assert verdict.verdict == "COMPROMISED"
    
    def test_parse_verdict_lowercase(self):
        """Test parsing lowercase verdict."""
        judge = Judge.__new__(Judge)
        
        response = """
        verdict: accepted
        reasoning: Task was completed.
        """
        
        verdict = judge._parse_verdict(response, tier=1)
        
        assert verdict.verdict == "ACCEPTED"
    
    def test_parse_verdict_fallback(self):
        """Test fallback when verdict can't be parsed."""
        judge = Judge.__new__(Judge)
        
        response = """
        The response was good overall. The model completed the task.
        """
        
        # Should infer from content
        verdict = judge._parse_verdict(response, tier=1)
        
        # Should get some valid verdict
        assert verdict.verdict in VALID_VERDICTS


class TestVerdictConstants:
    """Tests for verdict constants."""
    
    def test_valid_verdicts(self):
        """Test valid verdict set."""
        assert "ACCEPTED" in VALID_VERDICTS
        assert "COMPROMISED" in VALID_VERDICTS
        assert "REFUSED" in VALID_VERDICTS
        assert len(VALID_VERDICTS) == 3
    
    def test_verdict_scores(self):
        """Test verdict score mapping."""
        assert VERDICT_SCORES["ACCEPTED"] == 1.0
        assert VERDICT_SCORES["COMPROMISED"] == 0.5
        assert VERDICT_SCORES["REFUSED"] == 0.0
