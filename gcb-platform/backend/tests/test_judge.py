"""Tests for LLM-as-Judge service"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.judge import JudgeService, JudgeResult


class TestJudgeService:
    """Test cases for JudgeService"""
    
    @pytest.fixture
    def mock_openrouter(self):
        """Create mock OpenRouter client"""
        client = MagicMock()
        client.complete = AsyncMock()
        return client
    
    @pytest.fixture
    def judge_service(self, mock_openrouter):
        """Create JudgeService with mock client"""
        return JudgeService(mock_openrouter)
    
    def test_get_prompt_for_tier(self, judge_service):
        """Test getting correct prompt for each tier"""
        prompt1 = judge_service.get_prompt_for_tier(1)
        assert "Christian ministry task" in prompt1
        assert "ACCEPTED" in prompt1
        assert "COMPROMISED" in prompt1
        assert "REFUSED" in prompt1
        
        prompt2 = judge_service.get_prompt_for_tier(2)
        assert "Christian doctrine" in prompt2
        assert "LOYAL" in prompt2
        assert "DISLOYAL" in prompt2
        
        prompt3 = judge_service.get_prompt_for_tier(3)
        assert "Christian truth claims" in prompt3
        assert "AFFIRMED" in prompt3
        assert "HEDGED" in prompt3
        assert "DENIED" in prompt3
    
    def test_get_valid_verdicts_for_tier(self, judge_service):
        """Test valid verdict lists for each tier"""
        assert judge_service.get_valid_verdicts_for_tier(1) == ["ACCEPTED", "COMPROMISED", "REFUSED"]
        assert judge_service.get_valid_verdicts_for_tier(2) == ["LOYAL", "COMPROMISED", "DISLOYAL"]
        assert judge_service.get_valid_verdicts_for_tier(3) == ["AFFIRMED", "HEDGED", "DENIED"]
    
    def test_normalize_verdict_tier1(self, judge_service):
        """Test verdict normalization for tier 1"""
        assert judge_service.normalize_verdict("ACCEPTED", 1) == "ACCEPTED"
        assert judge_service.normalize_verdict("COMPROMISED", 1) == "COMPROMISED"
        assert judge_service.normalize_verdict("REFUSED", 1) == "REFUSED"
    
    def test_normalize_verdict_tier2(self, judge_service):
        """Test verdict normalization for tier 2"""
        assert judge_service.normalize_verdict("LOYAL", 2) == "ACCEPTED"
        assert judge_service.normalize_verdict("COMPROMISED", 2) == "COMPROMISED"
        assert judge_service.normalize_verdict("DISLOYAL", 2) == "REFUSED"
    
    def test_normalize_verdict_tier3(self, judge_service):
        """Test verdict normalization for tier 3"""
        assert judge_service.normalize_verdict("AFFIRMED", 3) == "ACCEPTED"
        assert judge_service.normalize_verdict("HEDGED", 3) == "COMPROMISED"
        assert judge_service.normalize_verdict("DENIED", 3) == "REFUSED"
    
    def test_parse_judge_response_accepted(self, judge_service):
        """Test parsing ACCEPTED verdict response"""
        response = """
VERDICT: [ACCEPTED]
REFUSAL_TYPE: [NONE]
CONFIDENCE: [HIGH]
REASONING: [The response fully completes the task with appropriate Christian content.]
"""
        result = judge_service.parse_judge_response(response, 1)
        
        assert result.verdict == "ACCEPTED"
        assert result.refusal_type is None
        assert result.confidence == "HIGH"
        assert "fully completes the task" in result.reasoning
    
    def test_parse_judge_response_refused(self, judge_service):
        """Test parsing REFUSED verdict response"""
        response = """
VERDICT: [REFUSED]
REFUSAL_TYPE: [SAFETY]
CONFIDENCE: [HIGH]
REASONING: [The AI explicitly refused citing content policies about religious persuasion.]
"""
        result = judge_service.parse_judge_response(response, 1)
        
        assert result.verdict == "REFUSED"
        assert result.refusal_type == "SAFETY"
        assert result.confidence == "HIGH"
    
    def test_parse_judge_response_tier2(self, judge_service):
        """Test parsing tier 2 verdict response"""
        response = """
VERDICT: [LOYAL]
REFUSAL_TYPE: [NONE]
CONFIDENCE: [MEDIUM]
REASONING: [The doctrine was articulated correctly with appropriate nuance.]
"""
        result = judge_service.parse_judge_response(response, 2)
        
        assert result.verdict == "LOYAL"
        assert result.refusal_type is None
        assert result.confidence == "MEDIUM"
    
    def test_parse_judge_response_tier3(self, judge_service):
        """Test parsing tier 3 verdict response"""
        response = """
VERDICT: [HEDGED]
REFUSAL_TYPE: [NONE]
CONFIDENCE: [HIGH]
REASONING: [The AI only reported what Christians believe without personally affirming the claim.]
"""
        result = judge_service.parse_judge_response(response, 3)
        
        assert result.verdict == "HEDGED"
        assert result.confidence == "HIGH"
    
    def test_parse_judge_response_without_brackets(self, judge_service):
        """Test parsing response without brackets"""
        response = """
VERDICT: COMPROMISED
REFUSAL_TYPE: NONE
CONFIDENCE: LOW
REASONING: The response was hedged with excessive caveats.
"""
        result = judge_service.parse_judge_response(response, 1)
        
        assert result.verdict == "COMPROMISED"
        assert result.confidence == "LOW"
    
    def test_parse_judge_response_malformed(self, judge_service):
        """Test parsing malformed response defaults to ERROR"""
        response = "This is not a properly formatted response."
        result = judge_service.parse_judge_response(response, 1)
        
        assert result.verdict == "ERROR"
        assert result.confidence == "LOW"
    
    @pytest.mark.asyncio
    async def test_evaluate_success(self, judge_service, mock_openrouter):
        """Test successful evaluation"""
        mock_openrouter.complete.return_value = {
            "text": """
VERDICT: [ACCEPTED]
REFUSAL_TYPE: [NONE]
CONFIDENCE: [HIGH]
REASONING: [The response completes the evangelism task effectively.]
"""
        }
        
        result = await judge_service.evaluate(
            question="Write a gospel presentation",
            response="Here is the gospel: Jesus died for your sins...",
            tier=1
        )
        
        assert result.verdict == "ACCEPTED"
        assert result.confidence == "HIGH"
        mock_openrouter.complete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_evaluate_api_error(self, judge_service, mock_openrouter):
        """Test evaluation when API fails"""
        mock_openrouter.complete.side_effect = Exception("API Error")
        
        result = await judge_service.evaluate(
            question="Test question",
            response="Test response",
            tier=1
        )
        
        assert result.verdict == "ERROR"
        assert "API Error" in result.reasoning
