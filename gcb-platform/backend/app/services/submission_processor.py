"""
Submission processor service for creating TestRun records from community submissions.

This service consolidates the shared logic between review_community_submission
and reprocess_community_submission endpoints.
"""
from datetime import datetime
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.models.community_submission import CommunitySubmission
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.question import Question
from app.db.models.test_run import TestRun
from app.db.models.result import Result


class SubmissionProcessorService:
    """Service for processing community submissions into TestRun records."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_model(self, model_id_str: str, model_name: str) -> Model:
        """
        Get or create a Model record by model_id string.
        
        Args:
            model_id_str: The model identifier (e.g., "anthropic/claude-3")
            model_name: The display name for the model
            
        Returns:
            The Model record (existing or newly created)
        """
        model = self.db.query(Model).filter(Model.model_id == model_id_str).first()
        if not model:
            # Extract provider from model_id if possible
            provider = "Unknown"
            if "/" in model_id_str:
                provider = model_id_str.split("/")[0]
            model = Model(
                model_id=model_id_str,
                name=model_name,
                provider=provider,
                is_active=True
            )
            self.db.add(model)
            self.db.flush()
        return model
    
    def get_question_set(self, version: Optional[str] = None) -> Optional[QuestionSet]:
        """
        Get a QuestionSet by version, or fall back to the active one.
        
        Args:
            version: Semantic version string (optional)
            
        Returns:
            QuestionSet or None if not found
        """
        if version:
            question_set = self.db.query(QuestionSet).filter(
                QuestionSet.semantic_version == version
            ).first()
            if question_set:
                return question_set
        
        # Fall back to active question set
        return self.db.query(QuestionSet).filter(
            QuestionSet.status == "active"
        ).order_by(QuestionSet.created_at.desc()).first()
    
    def get_or_create_methodology_version(
        self, 
        question_set: QuestionSet,
        judge_prompt: Optional[str] = None
    ) -> MethodologyVersion:
        """
        Get or create a MethodologyVersion for a question set.
        
        Args:
            question_set: The QuestionSet to get methodology for
            judge_prompt: Optional judge prompt for new methodology versions
            
        Returns:
            MethodologyVersion record
        """
        methodology_version = self.db.query(MethodologyVersion).filter(
            MethodologyVersion.question_set_id == question_set.id
        ).first()
        
        if not methodology_version:
            methodology_version = MethodologyVersion(
                question_set_id=question_set.id,
                judge_prompt=judge_prompt,
                scoring_config={"tier1": 0.7, "tier2": 0.2, "tier3": 0.1},
                active_from=datetime.utcnow()
            )
            self.db.add(methodology_version)
            self.db.flush()
        
        return methodology_version
    
    def build_tier_category_lookup(self, question_set_id: UUID) -> Dict[Tuple[int, str], list]:
        """
        Build a lookup dict for matching questions by tier and category.
        
        This is used when question IDs don't match between the submission
        and the database (e.g., when questions were re-imported).
        
        Args:
            question_set_id: The QuestionSet UUID
            
        Returns:
            Dict mapping (tier, category) tuples to lists of Question objects
        """
        questions = self.db.query(Question).filter(
            Question.question_set_id == question_set_id
        ).all()
        
        tier_cat_to_questions: Dict[Tuple[int, str], list] = {}
        for q in questions:
            key = (q.tier, q.category)
            if key not in tier_cat_to_questions:
                tier_cat_to_questions[key] = []
            tier_cat_to_questions[key].append(q)
        
        return tier_cat_to_questions
    
    def find_question(
        self,
        response_data: dict,
        question_set_id: UUID,
        tier_cat_lookup: Dict[Tuple[int, str], list],
        used_question_ids: set
    ) -> Optional[Question]:
        """
        Find a matching Question for a response entry.
        
        First tries to match by question_id, then falls back to tier+category matching.
        
        Args:
            response_data: The response dict from results_package
            question_set_id: The QuestionSet UUID
            tier_cat_lookup: Pre-built tier+category lookup dict
            used_question_ids: Set of already-used question IDs (to avoid duplicates)
            
        Returns:
            Question object or None if not found
        """
        question_id_str = response_data.get("question_id")
        question = None
        
        # Try to find question by ID first
        if question_id_str:
            try:
                question = self.db.query(Question).filter(
                    Question.id == question_id_str,
                    Question.question_set_id == question_set_id
                ).first()
            except:
                pass
        
        # If not found by ID, match by tier+category
        if not question:
            tier = response_data.get("tier")
            category = response_data.get("category")
            if tier and category:
                candidates = tier_cat_lookup.get((tier, category), [])
                for candidate in candidates:
                    if candidate.id not in used_question_ids:
                        question = candidate
                        break
        
        return question
    
    def create_test_run_from_submission(
        self,
        submission: CommunitySubmission,
        judge_prompt: Optional[str] = None
    ) -> Tuple[TestRun, int]:
        """
        Create a TestRun and Result records from a community submission.
        
        This is the main method that consolidates the duplicate logic from
        review_community_submission and reprocess_community_submission.
        
        Args:
            submission: The CommunitySubmission to process
            judge_prompt: Optional judge prompt for methodology version
            
        Returns:
            Tuple of (TestRun, results_created_count)
            
        Raises:
            ValueError: If no question set is found
        """
        results_package = submission.results_package or {}
        test_run_data = results_package.get("test_run", {})
        model_id_str = test_run_data.get("model", submission.model_name)
        
        # Get or create the Model
        model = self.get_or_create_model(model_id_str, submission.model_name)
        
        # Get the QuestionSet
        question_set = self.get_question_set(submission.question_set_version)
        if not question_set:
            raise ValueError("No question set found for this submission")
        
        # Get or create methodology version
        methodology_version = self.get_or_create_methodology_version(
            question_set, 
            judge_prompt
        )
        
        # Parse completion time
        completed_at = datetime.utcnow()
        if test_run_data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(
                    test_run_data["completed_at"].replace("Z", "+00:00")
                )
            except:
                pass
        
        # Create the TestRun
        test_run = TestRun(
            user_id=submission.user_id,
            model_id=model.id,
            question_set_id=question_set.id,
            methodology_version_id=methodology_version.id,
            status="completed",
            trust_tier="community",
            completed_at=completed_at,
            started_at=completed_at,
        )
        self.db.add(test_run)
        self.db.flush()
        
        # Build lookup for question matching
        tier_cat_lookup = self.build_tier_category_lookup(question_set.id)
        
        # Create Result records
        responses = results_package.get("responses", [])
        results_created = 0
        used_question_ids: set = set()
        
        for response_data in responses:
            question = self.find_question(
                response_data,
                question_set.id,
                tier_cat_lookup,
                used_question_ids
            )
            
            if not question:
                continue
            
            used_question_ids.add(question.id)
            
            result = Result(
                test_run_id=test_run.id,
                question_id=question.id,
                response=response_data.get("response", ""),
                verdict=response_data.get("verdict", "UNKNOWN"),
                reasoning=response_data.get("judge_reasoning", ""),
                thought_process=response_data.get("thought_process"),
            )
            self.db.add(result)
            results_created += 1
        
        return test_run, results_created
    
    def check_existing_test_run(
        self,
        submission: CommunitySubmission
    ) -> Optional[TestRun]:
        """
        Check if a TestRun already exists for this submission.
        
        Args:
            submission: The CommunitySubmission to check
            
        Returns:
            Existing TestRun or None
        """
        results_package = submission.results_package or {}
        test_run_data = results_package.get("test_run", {})
        model_id_str = test_run_data.get("model", submission.model_name)
        
        existing_model = self.db.query(Model).filter(
            Model.model_id == model_id_str
        ).first()
        
        if existing_model:
            return self.db.query(TestRun).filter(
                TestRun.model_id == existing_model.id,
                TestRun.user_id == submission.user_id,
                TestRun.status == "completed"
            ).first()
        
        return None
