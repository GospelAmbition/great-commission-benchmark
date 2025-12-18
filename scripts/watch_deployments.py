#!/usr/bin/env python3
"""
Railway Deployment Monitor for Cursor Integration

This script monitors Railway deployments, detects failures, and extracts
error logs to a file that Cursor can read and use for iterative fixes.

Usage:
    python scripts/watch_deployments.py [--service SERVICE] [--watch] [--output FILE]
"""

import subprocess
import json
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class RailwayDeploymentMonitor:
    """Monitor Railway deployments and extract failure logs."""
    
    def __init__(self, service: Optional[str] = None, output_file: str = ".deployment-errors.md"):
        self.service = service
        self.output_file = Path(output_file)
        self.last_checked_deployment = None
        
    def run_railway_command(self, cmd: List[str]) -> Dict:
        """Run a Railway CLI command and return parsed JSON output."""
        try:
            result = subprocess.run(
                ["railway"] + cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Warning: Railway command failed: {' '.join(cmd)}", file=sys.stderr)
                print(f"Error: {result.stderr}", file=sys.stderr)
                return {}
                
            try:
                return json.loads(result.stdout) if result.stdout.strip() else {}
            except json.JSONDecodeError:
                # Some Railway commands don't return JSON
                return {"raw_output": result.stdout}
                
        except FileNotFoundError:
            print("Error: Railway CLI not found. Install with: npm install -g @railway/cli", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error running Railway command: {e}", file=sys.stderr)
            return {}
    
    def get_deployments(self, limit: int = 10) -> List[Dict]:
        """Get recent deployments for the service."""
        # Railway CLI commands vary - try multiple approaches
        cmd = ["status", "--json"]
        if self.service:
            cmd.extend(["--service", self.service])
            
        result = self.run_railway_command(cmd)
        
        # Try alternative: direct deployments command
        if not result or (isinstance(result, dict) and not result.get("deployments")):
            cmd = ["deployments", "list"]
            if self.service:
                cmd.extend(["--service", self.service])
            result = self.run_railway_command(cmd)
        
        # Railway CLI might return deployments in different formats
        if isinstance(result, list):
            return result[:limit] if limit else result
        elif isinstance(result, dict):
            # Try various possible keys
            deployments = (
                result.get("deployments") or 
                result.get("data") or 
                result.get("deployment") or
                []
            )
            if isinstance(deployments, list):
                return deployments[:limit] if limit else deployments
            elif deployments:
                return [deployments]
        
        # If JSON parsing failed, try to get raw output and parse manually
        return []
    
    def get_deployment_logs(self, deployment_id: str) -> str:
        """Get logs for a specific deployment."""
        # Try multiple approaches to get logs
        cmd = ["logs"]
        if deployment_id:
            cmd.extend(["--deployment", deployment_id])
        if self.service:
            cmd.extend(["--service", self.service])
        cmd.append("--json")
            
        result = self.run_railway_command(cmd)
        
        if isinstance(result, dict) and "logs" in result:
            logs = result["logs"]
            if isinstance(logs, list):
                return "\n".join(str(log) for log in logs)
            return str(logs)
        elif isinstance(result, dict) and "raw_output" in result:
            return result["raw_output"]
        else:
            # Fallback: try direct log streaming (non-JSON)
            try:
                cmd = ["logs"]
                if deployment_id:
                    cmd.extend(["--deployment", deployment_id])
                if self.service:
                    cmd.extend(["--service", self.service])
                    
                proc = subprocess.run(
                    ["railway"] + cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if proc.stdout:
                    return proc.stdout
                elif proc.stderr:
                    return proc.stderr
                return "No logs available"
            except Exception as e:
                return f"Error fetching logs: {e}"
    
    def is_deployment_failed(self, deployment: Dict) -> bool:
        """Check if a deployment failed."""
        status = deployment.get("status", "").lower()
        state = deployment.get("state", "").lower()
        
        return status in ["failed", "error", "crashed"] or state in ["failed", "error", "crashed"]
    
    def extract_error_summary(self, logs: str) -> Dict[str, any]:
        """Extract key error information from logs."""
        lines = logs.split("\n")
        error_lines = []
        error_context = []
        
        # Look for common error patterns
        error_keywords = ["error", "failed", "exception", "traceback", "fatal", "cannot", "unable"]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in error_keywords):
                error_lines.append((i + 1, line))
                # Include context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end])
                if context not in error_context:
                    error_context.append(context)
        
        return {
            "error_count": len(error_lines),
            "error_lines": error_lines[:20],  # Limit to first 20 errors
            "error_context": error_context[:10],  # Limit to first 10 contexts
            "full_logs": logs[-5000:] if len(logs) > 5000 else logs  # Last 5000 chars
        }
    
    def format_error_report(self, deployment: Dict, error_summary: Dict) -> str:
        """Format error information as a markdown report for Cursor."""
        timestamp = datetime.now().isoformat()
        deployment_id = deployment.get("id", "unknown")
        service_name = self.service or deployment.get("service", "unknown")
        status = deployment.get("status", "unknown")
        created_at = deployment.get("createdAt", deployment.get("created_at", "unknown"))
        
        report = f"""# Railway Deployment Failure Report

**Generated:** {timestamp}
**Deployment ID:** {deployment_id}
**Service:** {service_name}
**Status:** {status}
**Created At:** {created_at}

## Error Summary

Found {error_summary['error_count']} potential error lines in the deployment logs.

## Key Error Lines

"""
        
        for line_num, line in error_summary["error_lines"]:
            report += f"**Line {line_num}:** `{line.strip()}`\n\n"
        
        report += "\n## Error Context\n\n"
        
        for i, context in enumerate(error_summary["error_context"], 1):
            report += f"### Context {i}\n\n```\n{context}\n```\n\n"
        
        report += "\n## Full Logs (Last 5000 characters)\n\n"
        report += f"```\n{error_summary['full_logs']}\n```\n"
        
        report += f"\n---\n\n*Use this information to fix the deployment issues.*\n"
        
        return report
    
    def check_and_report_failures(self) -> bool:
        """Check for failed deployments and generate report."""
        print(f"Checking deployments for service: {self.service or 'all'}...")
        
        deployments = self.get_deployments(limit=5)
        
        if not deployments:
            print("No deployments found or unable to fetch deployments.")
            return False
        
        failed_deployments = [d for d in deployments if self.is_deployment_failed(d)]
        
        if not failed_deployments:
            print("No failed deployments found.")
            # Clear the error file if no failures
            if self.output_file.exists():
                self.output_file.write_text("# No Deployment Failures\n\nAll recent deployments are successful.\n")
            return False
        
        print(f"Found {len(failed_deployments)} failed deployment(s).")
        
        # Get the most recent failed deployment
        latest_failure = failed_deployments[0]
        deployment_id = latest_failure.get("id", "unknown")
        
        print(f"Fetching logs for deployment: {deployment_id}...")
        logs = self.get_deployment_logs(deployment_id)
        
        if not logs:
            print("Warning: Could not fetch logs for failed deployment.")
            return False
        
        error_summary = self.extract_error_summary(logs)
        report = self.format_error_report(latest_failure, error_summary)
        
        # Write report to file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(report)
        
        print(f"\n✅ Error report written to: {self.output_file}")
        print(f"\n📋 Summary:")
        print(f"   - Deployment ID: {deployment_id}")
        print(f"   - Error lines found: {error_summary['error_count']}")
        print(f"\n💡 Cursor can now read this file to help fix the issues!")
        
        return True
    
    def watch(self, interval: int = 30):
        """Continuously monitor deployments."""
        print(f"Watching deployments every {interval} seconds...")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                self.check_and_report_failures()
                print(f"\nWaiting {interval} seconds before next check...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Railway deployments and extract failure logs for Cursor"
    )
    parser.add_argument(
        "--service",
        help="Railway service name (e.g., 'next-frontend', 'fastapi-backend')"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously monitor deployments"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Watch interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--output",
        default=".deployment-errors.md",
        help="Output file for error reports (default: .deployment-errors.md)"
    )
    
    args = parser.parse_args()
    
    monitor = RailwayDeploymentMonitor(
        service=args.service,
        output_file=args.output
    )
    
    if args.watch:
        monitor.watch(interval=args.interval)
    else:
        monitor.check_and_report_failures()


if __name__ == "__main__":
    main()
