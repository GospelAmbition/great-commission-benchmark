#!/usr/bin/env python3
"""
Railway Build Monitor for Cursor Integration

This script monitors Railway builds, detects failures, and extracts
build error logs to a file that Cursor can read and use for iterative fixes.

Usage:
    python scripts/watch_builds.py [--service SERVICE] [--watch] [--output FILE]
"""

import subprocess
import json
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class RailwayBuildMonitor:
    """Monitor Railway builds and extract failure logs."""
    
    def __init__(self, service: Optional[str] = None, output_file: str = ".build-errors.md"):
        self.service = service
        self.output_file = Path(output_file)
        self.last_checked_build = None
        
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
    
    def get_builds(self, limit: int = 10) -> List[Dict]:
        """Get recent builds for the service."""
        # Railway CLI commands vary - try multiple approaches
        # First try status command which includes build info
        cmd = ["status", "--json"]
        if self.service:
            cmd.extend(["--service", self.service])
            
        result = self.run_railway_command(cmd)
        
        # Try alternative: get deployments and extract build info
        if not result or (isinstance(result, dict) and not result.get("builds")):
            cmd = ["deployments", "list", "--json"]
            if self.service:
                cmd.extend(["--service", self.service])
            result = self.run_railway_command(cmd)
        
        # Railway CLI might return builds/deployments in different formats
        if isinstance(result, list):
            return result[:limit] if limit else result
        elif isinstance(result, dict):
            # Try various possible keys for builds
            builds = (
                result.get("builds") or 
                result.get("deployments") or  # Deployments contain build info
                result.get("data") or 
                result.get("build") or
                []
            )
            if isinstance(builds, list):
                return builds[:limit] if limit else builds
            elif builds:
                return [builds]
        
        # If JSON parsing failed, try to get raw output
        return []
    
    def get_build_logs(self, build_id: Optional[str] = None, deployment_id: Optional[str] = None) -> str:
        """Get logs for a specific build."""
        # Railway logs include build logs when you specify a deployment
        # Try multiple approaches to get build logs
        cmd = ["logs"]
        
        if deployment_id:
            cmd.extend(["--deployment", deployment_id])
        elif build_id:
            # Some Railway versions support --build flag
            cmd.extend(["--build", build_id])
        
        if self.service:
            cmd.extend(["--service", self.service])
        
        # Try with JSON first
        cmd_json = cmd + ["--json"]
        result = self.run_railway_command(cmd_json)
        
        if isinstance(result, dict) and "logs" in result:
            logs = result["logs"]
            if isinstance(logs, list):
                return "\n".join(str(log) for log in logs)
            return str(logs)
        elif isinstance(result, dict) and "raw_output" in result:
            return result["raw_output"]
        else:
            # Fallback: try direct log streaming (non-JSON)
            # This will get both build and runtime logs, but we'll filter for build errors
            try:
                proc = subprocess.run(
                    ["railway"] + cmd,
                    capture_output=True,
                    text=True,
                    timeout=60  # Builds can take longer
                )
                if proc.stdout:
                    return proc.stdout
                elif proc.stderr:
                    return proc.stderr
                return "No logs available"
            except Exception as e:
                return f"Error fetching logs: {e}"
    
    def is_build_failed(self, build_or_deployment: Dict) -> bool:
        """Check if a build failed."""
        # Check build-specific status
        build_status = build_or_deployment.get("buildStatus", "").lower()
        status = build_or_deployment.get("status", "").lower()
        state = build_or_deployment.get("state", "").lower()
        
        # Railway deployments include build status
        failed_statuses = ["failed", "error", "crashed", "build_failed", "build_error"]
        
        return (
            build_status in failed_statuses or
            status in failed_statuses or
            state in failed_statuses
        )
    
    def extract_build_error_summary(self, logs: str) -> Dict[str, any]:
        """Extract key build error information from logs."""
        lines = logs.split("\n")
        error_lines = []
        error_context = []
        
        # Build-specific error patterns
        build_error_keywords = [
            "error", "failed", "exception", "traceback", "fatal", 
            "cannot", "unable", "npm err", "build failed", "compilation error",
            "syntax error", "module not found", "cannot find module",
            "type error", "reference error", "import error", "export error",
            "eslint error", "typescript error", "ts error", "tsc error",
            "webpack error", "next build error", "build error",
            "install failed", "dependency error", "peer dependency",
            "version conflict", "out of memory", "killed", "signal",
            "exit code", "non-zero exit", "command failed"
        ]
        
        # Track if we're in a build phase (vs runtime)
        in_build_phase = False
        build_indicators = ["building", "installing", "compiling", "npm run build", "npm ci", "npm install"]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Detect build phase
            if any(indicator in line_lower for indicator in build_indicators):
                in_build_phase = True
            
            # Look for build errors
            if any(keyword in line_lower for keyword in build_error_keywords):
                error_lines.append((i + 1, line))
                # Include context (3 lines before and after for build errors)
                start = max(0, i - 3)
                end = min(len(lines), i + 4)
                context = "\n".join(lines[start:end])
                if context not in error_context:
                    error_context.append(context)
        
        # Filter to focus on build errors (not runtime)
        # If we found build indicators, prioritize those contexts
        build_error_context = []
        runtime_error_context = []
        
        for ctx in error_context:
            ctx_lower = ctx.lower()
            if any(indicator in ctx_lower for indicator in build_indicators + ["npm", "build", "compile", "install"]):
                build_error_context.append(ctx)
            else:
                runtime_error_context.append(ctx)
        
        # Prefer build errors, but include runtime if no build errors found
        final_context = build_error_context if build_error_context else error_context[:10]
        
        return {
            "error_count": len(error_lines),
            "error_lines": error_lines[:30],  # More errors for builds
            "error_context": final_context[:15],  # More context for builds
            "build_errors": len(build_error_context),
            "full_logs": logs[-10000:] if len(logs) > 10000 else logs  # More logs for builds
        }
    
    def format_error_report(self, build_info: Dict, error_summary: Dict) -> str:
        """Format build error information as a markdown report for Cursor."""
        timestamp = datetime.now().isoformat()
        build_id = build_info.get("buildId") or build_info.get("id") or "unknown"
        deployment_id = build_info.get("id") or build_info.get("deploymentId") or "unknown"
        service_name = self.service or build_info.get("service") or "unknown"
        status = build_info.get("buildStatus") or build_info.get("status") or "unknown"
        created_at = build_info.get("createdAt") or build_info.get("created_at") or "unknown"
        
        report = f"""# Railway Build Failure Report

**Generated:** {timestamp}
**Build ID:** {build_id}
**Deployment ID:** {deployment_id}
**Service:** {service_name}
**Build Status:** {status}
**Created At:** {created_at}

## Error Summary

Found {error_summary['error_count']} potential error lines in the build logs.
{error_summary['build_errors']} of these appear to be build-phase errors.

## Key Error Lines

"""
        
        for line_num, line in error_summary["error_lines"]:
            # Truncate very long lines
            display_line = line.strip()[:200] + "..." if len(line.strip()) > 200 else line.strip()
            report += f"**Line {line_num}:** `{display_line}`\n\n"
        
        report += "\n## Error Context\n\n"
        
        for i, context in enumerate(error_summary["error_context"], 1):
            report += f"### Context {i}\n\n```\n{context}\n```\n\n"
        
        report += "\n## Full Build Logs (Last 10000 characters)\n\n"
        report += f"```\n{error_summary['full_logs']}\n```\n"
        
        report += f"\n---\n\n*Use this information to fix the build issues.*\n"
        report += f"\n**Common Build Fixes:**\n"
        report += f"- Check for missing dependencies in package.json\n"
        report += f"- Verify Node.js/Python version compatibility\n"
        report += f"- Check for syntax errors in source files\n"
        report += f"- Review environment variable configuration\n"
        report += f"- Check for memory/resource limits\n"
        
        return report
    
    def check_and_report_failures(self) -> bool:
        """Check for failed builds and generate report."""
        print(f"Checking builds for service: {self.service or 'all'}...")
        
        builds_or_deployments = self.get_builds(limit=5)
        
        if not builds_or_deployments:
            print("No builds found or unable to fetch build information.")
            print("Note: Railway may combine build and deployment info. Trying alternative method...")
            # Try getting logs directly which might show build failures
            return self.check_logs_for_build_errors()
        
        failed_builds = [b for b in builds_or_deployments if self.is_build_failed(b)]
        
        if not failed_builds:
            print("No failed builds found in recent deployments.")
            # Still check logs in case build failed but status isn't set correctly
            return self.check_logs_for_build_errors()
        
        print(f"Found {len(failed_builds)} failed build(s).")
        
        # Get the most recent failed build
        latest_failure = failed_builds[0]
        build_id = latest_failure.get("buildId") or latest_failure.get("id")
        deployment_id = latest_failure.get("id")
        
        print(f"Fetching build logs (Build ID: {build_id}, Deployment ID: {deployment_id})...")
        logs = self.get_build_logs(build_id=build_id, deployment_id=deployment_id)
        
        if not logs or logs == "No logs available":
            print("Warning: Could not fetch logs for failed build.")
            return False
        
        error_summary = self.extract_build_error_summary(logs)
        report = self.format_error_report(latest_failure, error_summary)
        
        # Write report to file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(report)
        
        print(f"\n✅ Build error report written to: {self.output_file}")
        print(f"\n📋 Summary:")
        print(f"   - Build ID: {build_id}")
        print(f"   - Deployment ID: {deployment_id}")
        print(f"   - Error lines found: {error_summary['error_count']}")
        print(f"   - Build-phase errors: {error_summary['build_errors']}")
        print(f"\n💡 Cursor can now read this file to help fix the build issues!")
        
        return True
    
    def check_logs_for_build_errors(self) -> bool:
        """Fallback: Check recent logs directly for build errors."""
        print("Checking recent logs for build errors...")
        
        cmd = ["logs"]
        if self.service:
            cmd.extend(["--service", self.service])
        
        try:
            proc = subprocess.run(
                ["railway"] + cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if proc.stdout:
                logs = proc.stdout
                error_summary = self.extract_build_error_summary(logs)
                
                if error_summary['build_errors'] > 0 or error_summary['error_count'] > 5:
                    # Create a report from logs
                    build_info = {
                        "id": "unknown",
                        "service": self.service or "unknown",
                        "status": "build_error_detected",
                        "createdAt": datetime.now().isoformat()
                    }
                    report = self.format_error_report(build_info, error_summary)
                    
                    self.output_file.parent.mkdir(parents=True, exist_ok=True)
                    self.output_file.write_text(report)
                    
                    print(f"\n✅ Build errors detected in logs. Report written to: {self.output_file}")
                    return True
            
            print("No build errors detected in recent logs.")
            if self.output_file.exists():
                self.output_file.write_text("# No Build Failures\n\nAll recent builds appear successful.\n")
            return False
            
        except Exception as e:
            print(f"Error checking logs: {e}")
            return False
    
    def watch(self, interval: int = 30):
        """Continuously monitor builds."""
        print(f"Watching builds every {interval} seconds...")
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
        description="Monitor Railway builds and extract failure logs for Cursor"
    )
    parser.add_argument(
        "--service",
        help="Railway service name (e.g., 'next-frontend', 'fastapi-backend')"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously monitor builds"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Watch interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--output",
        default=".build-errors.md",
        help="Output file for error reports (default: .build-errors.md)"
    )
    
    args = parser.parse_args()
    
    monitor = RailwayBuildMonitor(
        service=args.service,
        output_file=args.output
    )
    
    if args.watch:
        monitor.watch(interval=args.interval)
    else:
        monitor.check_and_report_failures()


if __name__ == "__main__":
    main()
