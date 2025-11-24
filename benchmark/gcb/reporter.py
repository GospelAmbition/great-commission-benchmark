"""
Benchmark reporting and statistics for Great Commission Benchmark.

Generates reports in various formats from evaluation results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import defaultdict

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


class BenchmarkReporter:
    """Generates benchmark reports and statistics."""

    def __init__(self, db_path: str = "gcb.db", output_dir: str = "output"):
        """Initialize the reporter.
        
        Args:
            db_path: Path to SQLite database
            output_dir: Directory for generated reports
        """
        self.db = get_db(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def get_model_statistics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a model or all models.
        
        Args:
            model_id: Specific model ID (None = all models)
            
        Returns:
            Dictionary of statistics
        """
        with self.db.get_session() as session:
            # Get models
            if model_id:
                models = [session.query(Model).filter(Model.id == model_id).first()]
            else:
                models = session.query(Model).all()
            
            stats = {}
            
            for model in models:
                if not model:
                    continue
                
                # Get all responses for this model that have evaluations
                responses = session.query(Response).filter(
                    Response.model_id == model.id
                ).all()
                
                model_stats = {
                    "model_name": model.name,
                    "provider": model.provider,
                    "total_responses": len(responses),
                    "evaluated_responses": 0,
                    "by_verdict": defaultdict(int),
                    "by_acceptance_level": defaultdict(lambda: defaultdict(int)),
                    "by_prompt_type": defaultdict(lambda: defaultdict(int)),
                    "approval_rate": 0.0,
                    "avg_confidence": 0.0,
                }
                
                confidences = []
                
                for response in responses:
                    if not response.evaluation:
                        continue
                    
                    model_stats["evaluated_responses"] += 1
                    verdict = response.evaluation.verdict.value
                    model_stats["by_verdict"][verdict] += 1
                    
                    if response.evaluation.confidence_score:
                        confidences.append(response.evaluation.confidence_score)
                    
                    # Stats by acceptance level
                    if response.question:
                        level = response.question.acceptance_level.value
                        model_stats["by_acceptance_level"][level][verdict] += 1
                        
                        ptype = response.question.prompt_type.value
                        model_stats["by_prompt_type"][ptype][verdict] += 1
                
                # Calculate rates
                total_eval = model_stats["evaluated_responses"]
                if total_eval > 0:
                    approved = model_stats["by_verdict"]["approved"]
                    model_stats["approval_rate"] = (approved / total_eval) * 100
                    
                if confidences:
                    model_stats["avg_confidence"] = sum(confidences) / len(confidences)
                
                # Convert defaultdicts to regular dicts for JSON serialization
                model_stats["by_verdict"] = dict(model_stats["by_verdict"])
                model_stats["by_acceptance_level"] = {
                    k: dict(v) for k, v in model_stats["by_acceptance_level"].items()
                }
                model_stats["by_prompt_type"] = {
                    k: dict(v) for k, v in model_stats["by_prompt_type"].items()
                }
                
                stats[model.id] = model_stats
            
            return stats

    def get_test_run_statistics(self, test_run_id: str) -> Dict[str, Any]:
        """Get statistics for a specific test run.
        
        Args:
            test_run_id: Test run ID
            
        Returns:
            Dictionary of statistics
        """
        with self.db.get_session() as session:
            test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            
            if not test_run:
                return {}
            
            responses = session.query(Response).filter(
                Response.test_run_id == test_run_id
            ).all()
            
            stats = {
                "test_run_id": test_run_id,
                "name": test_run.name,
                "started_at": test_run.started_at.isoformat() if test_run.started_at else None,
                "completed_at": test_run.completed_at.isoformat() if test_run.completed_at else None,
                "status": test_run.status.value,
                "total_responses": len(responses),
                "by_verdict": defaultdict(int),
                "by_acceptance_level": defaultdict(lambda: {"total": 0, "approved": 0, "refused": 0, "ambiguous": 0}),
            }
            
            for response in responses:
                if response.evaluation:
                    verdict = response.evaluation.verdict.value
                    stats["by_verdict"][verdict] += 1
                    
                    if response.question:
                        level = response.question.acceptance_level.value
                        stats["by_acceptance_level"][level]["total"] += 1
                        stats["by_acceptance_level"][level][verdict] += 1
            
            stats["by_verdict"] = dict(stats["by_verdict"])
            stats["by_acceptance_level"] = {k: dict(v) for k, v in stats["by_acceptance_level"].items()}
            
            return stats

    def generate_markdown_report(
        self,
        model_id: Optional[str] = None,
        test_run_id: Optional[str] = None,
        output_file: str = "benchmark_report.md",
    ) -> Path:
        """Generate a markdown benchmark report.
        
        Args:
            model_id: Specific model to report on
            test_run_id: Specific test run to report on
            output_file: Output filename
            
        Returns:
            Path to generated report
        """
        model_stats = self.get_model_statistics(model_id)
        
        lines = [
            "# Great Commission Benchmark Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        if not model_stats:
            lines.append("No evaluation data found.")
        else:
            # Summary table
            lines.extend([
                "## Summary",
                "",
                "| Model | Evaluated | Approved | Refused | Ambiguous | Approval Rate |",
                "|-------|-----------|----------|---------|-----------|---------------|",
            ])
            
            for model_id, stats in model_stats.items():
                approved = stats["by_verdict"].get("approved", 0)
                refused = stats["by_verdict"].get("refused", 0)
                ambiguous = stats["by_verdict"].get("ambiguous", 0)
                rate = stats["approval_rate"]
                
                lines.append(
                    f"| {stats['model_name']} | {stats['evaluated_responses']} | "
                    f"{approved} | {refused} | {ambiguous} | {rate:.1f}% |"
                )
            
            lines.append("")
            
            # Detailed breakdown for each model
            for model_id, stats in model_stats.items():
                lines.extend([
                    f"## {stats['model_name']}",
                    "",
                    f"**Provider:** {stats['provider']}",
                    f"**Total Responses:** {stats['total_responses']}",
                    f"**Evaluated:** {stats['evaluated_responses']}",
                    f"**Overall Approval Rate:** {stats['approval_rate']:.1f}%",
                    f"**Average Confidence:** {stats['avg_confidence']:.2f}",
                    "",
                ])
                
                # By acceptance level
                if stats["by_acceptance_level"]:
                    lines.extend([
                        "### By Acceptance Level",
                        "",
                        "| Level | Approved | Refused | Ambiguous | Approval Rate |",
                        "|-------|----------|---------|-----------|---------------|",
                    ])
                    
                    for level in ["green", "orange", "red"]:
                        if level in stats["by_acceptance_level"]:
                            level_stats = stats["by_acceptance_level"][level]
                            approved = level_stats.get("approved", 0)
                            refused = level_stats.get("refused", 0)
                            ambiguous = level_stats.get("ambiguous", 0)
                            total = approved + refused + ambiguous
                            rate = (approved / total * 100) if total > 0 else 0
                            
                            level_emoji = {"green": "🟢", "orange": "🟠", "red": "🔴"}[level]
                            lines.append(
                                f"| {level_emoji} {level.upper()} | {approved} | {refused} | "
                                f"{ambiguous} | {rate:.1f}% |"
                            )
                    
                    lines.append("")
                
                # By prompt type
                if stats["by_prompt_type"]:
                    lines.extend([
                        "### By Prompt Type",
                        "",
                        "| Type | Approved | Refused | Ambiguous | Approval Rate |",
                        "|------|----------|---------|-----------|---------------|",
                    ])
                    
                    for ptype, type_stats in stats["by_prompt_type"].items():
                        approved = type_stats.get("approved", 0)
                        refused = type_stats.get("refused", 0)
                        ambiguous = type_stats.get("ambiguous", 0)
                        total = approved + refused + ambiguous
                        rate = (approved / total * 100) if total > 0 else 0
                        
                        lines.append(
                            f"| {ptype} | {approved} | {refused} | {ambiguous} | {rate:.1f}% |"
                        )
                    
                    lines.append("")
        
        # Write report
        output_path = self.output_dir / output_file
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        
        return output_path

    def generate_json_report(
        self,
        model_id: Optional[str] = None,
        output_file: str = "benchmark_report.json",
    ) -> Path:
        """Generate a JSON benchmark report.
        
        Args:
            model_id: Specific model to report on
            output_file: Output filename
            
        Returns:
            Path to generated report
        """
        model_stats = self.get_model_statistics(model_id)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "version": "0.5",
            "models": model_stats,
        }
        
        output_path = self.output_dir / output_file
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return output_path

    def generate_detailed_results(
        self,
        test_run_id: Optional[str] = None,
        output_file: str = "detailed_results.md",
    ) -> Path:
        """Generate detailed results with individual question/response pairs.
        
        Args:
            test_run_id: Specific test run (None = latest)
            output_file: Output filename
            
        Returns:
            Path to generated report
        """
        with self.db.get_session() as session:
            # Get test run
            if test_run_id:
                test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            else:
                test_run = session.query(TestRun).order_by(TestRun.started_at.desc()).first()
            
            if not test_run:
                lines = ["# Detailed Results", "", "No test runs found."]
            else:
                responses = session.query(Response).filter(
                    Response.test_run_id == test_run.id
                ).all()
                
                lines = [
                    "# Detailed Results",
                    "",
                    f"**Test Run:** {test_run.name or test_run.id[:8]}",
                    f"**Date:** {test_run.started_at.strftime('%Y-%m-%d %H:%M') if test_run.started_at else 'N/A'}",
                    f"**Total Responses:** {len(responses)}",
                    "",
                    "---",
                    "",
                ]
                
                # Group by acceptance level
                by_level = defaultdict(list)
                for response in responses:
                    if response.question:
                        level = response.question.acceptance_level.value
                        by_level[level].append(response)
                
                for level in ["green", "orange", "red"]:
                    if level not in by_level:
                        continue
                    
                    level_emoji = {"green": "🟢", "orange": "🟠", "red": "🔴"}[level]
                    lines.extend([
                        f"## {level_emoji} {level.upper()} Questions",
                        "",
                    ])
                    
                    for i, response in enumerate(by_level[level], 1):
                        question = response.question
                        evaluation = response.evaluation
                        
                        verdict_emoji = {
                            "approved": "✅",
                            "refused": "❌",
                            "ambiguous": "⚠️",
                        }.get(evaluation.verdict.value if evaluation else "", "❓")
                        
                        lines.extend([
                            f"### Question {i}",
                            "",
                            f"**Prompt Type:** {question.prompt_type.value}",
                            "",
                            f"**Question:**",
                            f"> {question.text}",
                            "",
                            f"**Response:**",
                            f"> {response.response_text[:500]}{'...' if response.response_text and len(response.response_text) > 500 else ''}",
                            "",
                        ])
                        
                        if evaluation:
                            lines.extend([
                                f"**Verdict:** {verdict_emoji} {evaluation.verdict.value.upper()}",
                                f"**Reasoning:** {evaluation.reasoning}",
                                f"**Confidence:** {evaluation.confidence_score:.2f}" if evaluation.confidence_score else "",
                                "",
                            ])
                        
                        lines.append("---\n")
        
        output_path = self.output_dir / output_file
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        
        return output_path

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get a quick summary of the benchmark database.
        
        Returns:
            Summary statistics dictionary
        """
        with self.db.get_session() as session:
            total_questions = session.query(Question).count()
            total_responses = session.query(Response).count()
            total_evaluations = session.query(Evaluation).count()
            total_models = session.query(Model).count()
            total_test_runs = session.query(TestRun).count()
            
            # Get verdict counts
            verdict_counts = {}
            for verdict in Verdict:
                count = session.query(Evaluation).filter(
                    Evaluation.verdict == verdict
                ).count()
                verdict_counts[verdict.value] = count
            
            return {
                "total_questions": total_questions,
                "total_responses": total_responses,
                "total_evaluations": total_evaluations,
                "total_models": total_models,
                "total_test_runs": total_test_runs,
                "verdict_counts": verdict_counts,
            }


def generate_report(
    db_path: str = "gcb.db",
    output_dir: str = "output",
    format: str = "markdown",
) -> Path:
    """Convenience function to generate a report.
    
    Args:
        db_path: Database path
        output_dir: Output directory
        format: Report format (markdown, json)
        
    Returns:
        Path to generated report
    """
    reporter = BenchmarkReporter(db_path, output_dir)
    
    if format == "json":
        return reporter.generate_json_report()
    else:
        return reporter.generate_markdown_report()


if __name__ == "__main__":
    # Quick test
    reporter = BenchmarkReporter()
    
    summary = reporter.get_summary_stats()
    print(f"Summary: {summary}")
    
    report_path = reporter.generate_markdown_report()
    print(f"Report generated: {report_path}")

