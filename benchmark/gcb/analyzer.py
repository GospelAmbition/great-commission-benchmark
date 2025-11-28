"""
Response database analysis and query tools for Great Commission Benchmark.

Provides comprehensive analysis capabilities for exploring response data,
comparing models, analyzing trends, and exporting results.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from gcb.database import (
    get_db,
    DatabaseManager,
    Question,
    Model,
    TestRun,
    Response,
    Evaluation,
    AcceptanceLevel,
    PromptType,
    Verdict,
    TestRunStatus,
)


@dataclass
class ResponseFilter:
    """Filter criteria for querying responses."""
    model_ids: Optional[List[str]] = None
    test_run_ids: Optional[List[str]] = None
    acceptance_levels: Optional[List[AcceptanceLevel]] = None
    prompt_types: Optional[List[PromptType]] = None
    verdicts: Optional[List[Verdict]] = None
    has_evaluation: Optional[bool] = None
    has_error: Optional[bool] = None
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ResponseAnalyzer:
    """Comprehensive analysis tool for response database."""

    def __init__(
        self,
        questions_db_path: str = "questions.db",
        responses_db_path: str = "responses.db",
    ):
        """Initialize the analyzer.
        
        Args:
            questions_db_path: Path to questions database
            responses_db_path: Path to responses database
        """
        self.db = get_db(questions_db_path, responses_db_path)

    def query_responses(
        self,
        filter: Optional[ResponseFilter] = None,
        limit: Optional[int] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> List[Response]:
        """Query responses with flexible filtering.
        
        Args:
            filter: ResponseFilter object with filter criteria
            limit: Maximum number of responses to return
            order_by: Field to order by (created_at, latency_ms, token_count)
            order_desc: Whether to order descending
            
        Returns:
            List of Response objects matching the criteria
        """
        with self.db.get_session() as session:
            query = session.query(Response)
            
            if filter:
                if filter.model_ids:
                    query = query.filter(Response.model_id.in_(filter.model_ids))
                
                if filter.test_run_ids:
                    query = query.filter(Response.test_run_id.in_(filter.test_run_ids))
                
                if filter.acceptance_levels:
                    query = query.filter(Response.acceptance_level.in_([al.value for al in filter.acceptance_levels]))
                
                if filter.prompt_types:
                    query = query.filter(Response.prompt_type.in_([pt.value for pt in filter.prompt_types]))
                
                if filter.verdicts:
                    # Join with evaluations table
                    query = query.join(Evaluation).filter(
                        Evaluation.verdict.in_([v.value for v in filter.verdicts])
                    )
                
                if filter.has_evaluation is not None:
                    if filter.has_evaluation:
                        query = query.join(Evaluation)
                    else:
                        query = query.outerjoin(Evaluation).filter(Evaluation.id.is_(None))
                
                if filter.has_error is not None:
                    if filter.has_error:
                        query = query.filter(Response.error.isnot(None))
                    else:
                        query = query.filter(Response.error.is_(None))
                
                if filter.min_confidence is not None or filter.max_confidence is not None:
                    query = query.join(Evaluation)
                    if filter.min_confidence is not None:
                        query = query.filter(Evaluation.confidence_score >= filter.min_confidence)
                    if filter.max_confidence is not None:
                        query = query.filter(Evaluation.confidence_score <= filter.max_confidence)
                
                if filter.date_from:
                    query = query.filter(Response.created_at >= filter.date_from)
                
                if filter.date_to:
                    query = query.filter(Response.created_at <= filter.date_to)
            
            # Ordering
            order_field = getattr(Response, order_by, Response.created_at)
            if order_desc:
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()

    def get_model_comparison(
        self,
        model_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Compare statistics across multiple models.
        
        Args:
            model_ids: List of model IDs to compare (None = all models)
            
        Returns:
            Dictionary with comparison statistics
        """
        with self.db.get_session() as session:
            if model_ids:
                models = session.query(Model).filter(Model.id.in_(model_ids)).all()
            else:
                models = session.query(Model).all()
            
            comparison = {
                "models": {},
                "summary": {
                    "total_models": len(models),
                    "total_responses": 0,
                    "total_evaluations": 0,
                },
            }
            
            for model in models:
                responses = session.query(Response).filter(Response.model_id == model.id).all()
                evaluations = session.query(Evaluation).join(Response).filter(
                    Response.model_id == model.id
                ).all()
                
                model_stats = {
                    "model_id": model.id,
                    "model_name": model.name,
                    "provider": model.provider,
                    "total_responses": len(responses),
                    "evaluated_responses": len(evaluations),
                    "by_acceptance_level": defaultdict(lambda: defaultdict(int)),
                    "by_prompt_type": defaultdict(lambda: defaultdict(int)),
                    "by_verdict": defaultdict(int),
                    "avg_latency_ms": 0.0,
                    "avg_token_count": 0.0,
                    "avg_confidence": 0.0,
                    "error_rate": 0.0,
                }
                
                latencies = []
                token_counts = []
                confidences = []
                errors = 0
                
                for response in responses:
                    if response.latency_ms:
                        latencies.append(response.latency_ms)
                    if response.token_count:
                        token_counts.append(response.token_count)
                    if response.error:
                        errors += 1
                    
                    if response.evaluation:
                        verdict = response.evaluation.verdict.value
                        model_stats["by_verdict"][verdict] += 1
                        
                        if response.evaluation.confidence_score:
                            confidences.append(response.evaluation.confidence_score)
                        
                        level_obj = response.get_acceptance_level()
                        if level_obj:
                            level = level_obj.value
                            model_stats["by_acceptance_level"][level][verdict] += 1
                        
                        ptype_obj = response.get_prompt_type()
                        if ptype_obj:
                            ptype = ptype_obj.value
                            model_stats["by_prompt_type"][ptype][verdict] += 1
                
                if latencies:
                    model_stats["avg_latency_ms"] = sum(latencies) / len(latencies)
                if token_counts:
                    model_stats["avg_token_count"] = sum(token_counts) / len(token_counts)
                if confidences:
                    model_stats["avg_confidence"] = sum(confidences) / len(confidences)
                if responses:
                    model_stats["error_rate"] = (errors / len(responses)) * 100
                
                # Convert defaultdicts to regular dicts
                model_stats["by_verdict"] = dict(model_stats["by_verdict"])
                model_stats["by_acceptance_level"] = {
                    k: dict(v) for k, v in model_stats["by_acceptance_level"].items()
                }
                model_stats["by_prompt_type"] = {
                    k: dict(v) for k, v in model_stats["by_prompt_type"].items()
                }
                
                comparison["models"][model.id] = model_stats
                comparison["summary"]["total_responses"] += len(responses)
                comparison["summary"]["total_evaluations"] += len(evaluations)
            
            return comparison

    def get_trend_analysis(
        self,
        model_id: Optional[str] = None,
        group_by: str = "day",
    ) -> Dict[str, Any]:
        """Analyze trends over time.
        
        Args:
            model_id: Specific model ID (None = all models)
            group_by: Grouping period ("day", "week", "month")
            
        Returns:
            Dictionary with trend data
        """
        with self.db.get_session() as session:
            query = session.query(Response)
            
            if model_id:
                query = query.filter(Response.model_id == model_id)
            
            responses = query.order_by(Response.created_at).all()
            
            trends = defaultdict(lambda: {
                "total": 0,
                "evaluated": 0,
                "by_verdict": defaultdict(int),
                "by_acceptance_level": defaultdict(int),
            })
            
            for response in responses:
                date = response.created_at.date()
                
                # Group by period
                if group_by == "day":
                    key = date.isoformat()
                elif group_by == "week":
                    # Get ISO week
                    year, week, _ = date.isocalendar()
                    key = f"{year}-W{week:02d}"
                elif group_by == "month":
                    key = date.strftime("%Y-%m")
                else:
                    key = date.isoformat()
                
                trends[key]["total"] += 1
                
                if response.evaluation:
                    trends[key]["evaluated"] += 1
                    trends[key]["by_verdict"][response.evaluation.verdict.value] += 1
                    
                    level_obj = response.get_acceptance_level()
                    if level_obj:
                        trends[key]["by_acceptance_level"][level_obj.value] += 1
            
            # Convert to regular dicts
            result = {}
            for key, data in trends.items():
                result[key] = {
                    "total": data["total"],
                    "evaluated": data["evaluated"],
                    "by_verdict": dict(data["by_verdict"]),
                    "by_acceptance_level": dict(data["by_acceptance_level"]),
                }
            
            return {
                "group_by": group_by,
                "trends": result,
            }

    def get_detailed_breakdown(
        self,
        model_id: Optional[str] = None,
        acceptance_level: Optional[AcceptanceLevel] = None,
        prompt_type: Optional[PromptType] = None,
    ) -> Dict[str, Any]:
        """Get detailed breakdown with individual response data.
        
        Args:
            model_id: Specific model ID (None = all models)
            acceptance_level: Filter by acceptance level
            prompt_type: Filter by prompt type
            
        Returns:
            Dictionary with detailed breakdown
        """
        filter = ResponseFilter()
        if model_id:
            filter.model_ids = [model_id]
        if acceptance_level:
            filter.acceptance_levels = [acceptance_level]
        if prompt_type:
            filter.prompt_types = [prompt_type]
        
        responses = self.query_responses(filter=filter)
        
        breakdown = {
            "total_responses": len(responses),
            "responses": [],
        }
        
        for response in responses:
            response_data = {
                "response_id": response.id,
                "model_id": response.model_id,
                "test_run_id": response.test_run_id,
                "question_text": response.get_question_text(),
                "acceptance_level": response.get_acceptance_level().value if response.get_acceptance_level() else None,
                "prompt_type": response.get_prompt_type().value if response.get_prompt_type() else None,
                "response_text": response.response_text[:500] + "..." if response.response_text and len(response.response_text) > 500 else response.response_text,
                "latency_ms": response.latency_ms,
                "token_count": response.token_count,
                "error": response.error,
                "created_at": response.created_at.isoformat() if response.created_at else None,
            }
            
            if response.evaluation:
                response_data["evaluation"] = {
                    "verdict": response.evaluation.verdict.value,
                    "reasoning": response.evaluation.reasoning,
                    "confidence_score": response.evaluation.confidence_score,
                    "evaluator_model": response.evaluation.evaluator_model,
                }
            
            breakdown["responses"].append(response_data)
        
        return breakdown

    def export_to_csv(
        self,
        output_path: str,
        filter: Optional[ResponseFilter] = None,
        include_evaluation: bool = True,
        include_response_text: bool = True,
    ) -> Path:
        """Export responses to CSV file.
        
        Args:
            output_path: Path to output CSV file
            filter: ResponseFilter object with filter criteria
            include_evaluation: Whether to include evaluation data
            include_response_text: Whether to include full response text
            
        Returns:
            Path to created CSV file
        """
        responses = self.query_responses(filter=filter)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "response_id",
                "model_id",
                "model_name",
                "test_run_id",
                "question_id",
                "question_text",
                "acceptance_level",
                "prompt_type",
                "latency_ms",
                "token_count",
                "error",
                "created_at",
            ]
            
            if include_evaluation:
                fieldnames.extend([
                    "verdict",
                    "reasoning",
                    "confidence_score",
                    "evaluator_model",
                ])
            
            if include_response_text:
                fieldnames.append("response_text")
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            with self.db.get_session() as session:
                for response in responses:
                    # Get model name
                    model = session.query(Model).filter(Model.id == response.model_id).first()
                    model_name = model.name if model else "Unknown"
                    
                    row = {
                        "response_id": response.id,
                        "model_id": response.model_id,
                        "model_name": model_name,
                        "test_run_id": response.test_run_id,
                        "question_id": response.question_id,
                        "question_text": response.get_question_text(),
                        "acceptance_level": response.get_acceptance_level().value if response.get_acceptance_level() else None,
                        "prompt_type": response.get_prompt_type().value if response.get_prompt_type() else None,
                        "latency_ms": response.latency_ms,
                        "token_count": response.token_count,
                        "error": response.error,
                        "created_at": response.created_at.isoformat() if response.created_at else None,
                    }
                    
                    if include_evaluation and response.evaluation:
                        row.update({
                            "verdict": response.evaluation.verdict.value,
                            "reasoning": response.evaluation.reasoning,
                            "confidence_score": response.evaluation.confidence_score,
                            "evaluator_model": response.evaluation.evaluator_model,
                        })
                    elif include_evaluation:
                        row.update({
                            "verdict": None,
                            "reasoning": None,
                            "confidence_score": None,
                            "evaluator_model": None,
                        })
                    
                    if include_response_text:
                        row["response_text"] = response.response_text
                    
                    writer.writerow(row)
        
        return output_file

    def export_to_json(
        self,
        output_path: str,
        filter: Optional[ResponseFilter] = None,
    ) -> Path:
        """Export responses to JSON file.
        
        Args:
            output_path: Path to output JSON file
            filter: ResponseFilter object with filter criteria
            
        Returns:
            Path to created JSON file
        """
        responses = self.query_responses(filter=filter)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_responses": len(responses),
            "responses": [],
        }
        
        with self.db.get_session() as session:
            for response in responses:
                model = session.query(Model).filter(Model.id == response.model_id).first()
                
                response_data = {
                    "response_id": response.id,
                    "model": {
                        "id": response.model_id,
                        "name": model.name if model else "Unknown",
                        "provider": model.provider if model else None,
                    },
                    "test_run_id": response.test_run_id,
                    "question": {
                        "id": response.question_id,
                        "text": response.get_question_text(),
                        "acceptance_level": response.get_acceptance_level().value if response.get_acceptance_level() else None,
                        "prompt_type": response.get_prompt_type().value if response.get_prompt_type() else None,
                    },
                    "response": {
                        "text": response.response_text,
                        "latency_ms": response.latency_ms,
                        "token_count": response.token_count,
                        "error": response.error,
                    },
                    "created_at": response.created_at.isoformat() if response.created_at else None,
                }
                
                if response.evaluation:
                    response_data["evaluation"] = {
                        "verdict": response.evaluation.verdict.value,
                        "reasoning": response.evaluation.reasoning,
                        "confidence_score": response.evaluation.confidence_score,
                        "evaluator_model": response.evaluation.evaluator_model,
                        "created_at": response.evaluation.created_at.isoformat() if response.evaluation.created_at else None,
                    }
                
                data["responses"].append(response_data)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_file

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistics summary.
        
        Returns:
            Dictionary with comprehensive statistics
        """
        with self.db.get_session() as session:
            total_responses = session.query(Response).count()
            total_evaluations = session.query(Evaluation).count()
            total_models = session.query(Model).count()
            total_test_runs = session.query(TestRun).count()
            
            # Verdict distribution
            verdict_counts = {}
            for verdict in Verdict:
                count = session.query(Evaluation).filter(
                    Evaluation.verdict == verdict
                ).count()
                verdict_counts[verdict.value] = count
            
            # Acceptance level distribution
            level_counts = {}
            for level in AcceptanceLevel:
                count = session.query(Response).filter(
                    Response.acceptance_level == level.value
                ).count()
                level_counts[level.value] = count
            
            # Prompt type distribution
            type_counts = {}
            for ptype in PromptType:
                count = session.query(Response).filter(
                    Response.prompt_type == ptype.value
                ).count()
                type_counts[ptype.value] = count
            
            # Error rate
            error_count = session.query(Response).filter(
                Response.error.isnot(None)
            ).count()
            error_rate = (error_count / total_responses * 100) if total_responses > 0 else 0
            
            # Average metrics
            avg_latency = session.query(func.avg(Response.latency_ms)).filter(
                Response.latency_ms.isnot(None)
            ).scalar() or 0.0
            
            avg_tokens = session.query(func.avg(Response.token_count)).filter(
                Response.token_count.isnot(None)
            ).scalar() or 0.0
            
            avg_confidence = session.query(func.avg(Evaluation.confidence_score)).filter(
                Evaluation.confidence_score.isnot(None)
            ).scalar() or 0.0
        
        return {
            "totals": {
                "responses": total_responses,
                "evaluations": total_evaluations,
                "models": total_models,
                "test_runs": total_test_runs,
            },
            "distributions": {
                "verdicts": verdict_counts,
                "acceptance_levels": level_counts,
                "prompt_types": type_counts,
            },
            "metrics": {
                "error_rate": round(error_rate, 2),
                "avg_latency_ms": round(avg_latency, 2) if avg_latency else 0.0,
                "avg_token_count": round(avg_tokens, 2) if avg_tokens else 0.0,
                "avg_confidence": round(avg_confidence, 3) if avg_confidence else 0.0,
            },
        }


if __name__ == "__main__":
    # Quick test
    analyzer = ResponseAnalyzer()
    
    summary = analyzer.get_statistics_summary()
    print("Statistics Summary:")
    print(json.dumps(summary, indent=2))
    
    comparison = analyzer.get_model_comparison()
    print("\nModel Comparison:")
    print(json.dumps(comparison, indent=2, default=str))
