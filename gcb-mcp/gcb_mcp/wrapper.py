"""
Background job wrapper for gcb-runner benchmark tests.

Invoked as a detached subprocess:
    python -m gcb_mcp.wrapper <job_id> <model_id>

Runs gcb-runner, writes progress heartbeats to SQLite, then marks the job
succeeded (with score) or failed.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Locate gcb-runner
# ---------------------------------------------------------------------------


def _find_gcb_runner() -> str:
    """Return path to the gcb-runner executable."""
    import shutil

    # 1. Explicit env override
    explicit = os.environ.get("GCB_RUNNER_PATH", "").strip()
    if explicit and Path(explicit).is_file():
        return explicit

    # 2. On PATH
    on_path = shutil.which("gcb-runner")
    if on_path:
        return on_path

    # 3. Same Python env
    runner_in_env = Path(sys.executable).parent / "gcb-runner"
    if runner_in_env.exists():
        return str(runner_in_env)

    raise RuntimeError(
        "gcb-runner not found. Install it or set GCB_RUNNER_PATH env var."
    )


# ---------------------------------------------------------------------------
# Progress parsing
# ---------------------------------------------------------------------------


# Patterns to match gcb-runner rich output lines
_TIER_PATTERN = re.compile(
    r"Tier\s+(\d+)[^\[]*\[?(\d+)\s+questions\]?", re.IGNORECASE
)
_PROGRESS_PATTERN = re.compile(r"(\d+)/(\d+)")
_SCORE_PATTERN = re.compile(r"GCB\s+Score[:\s]+(\d+\.?\d*)", re.IGNORECASE)
_TIER_SCORE_PATTERN = re.compile(r"Tier\s+(\d+).*?(\d+\.?\d+)%.*?×", re.IGNORECASE)


def _runner_supports_test_option(gcb_runner: str, option: str) -> bool:
    """Return True if `gcb-runner test --help` includes the given option."""
    try:
        result = subprocess.run(
            [gcb_runner, "test", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ},
            check=False,
        )
    except Exception:
        # Be conservative on probe failures: skip optional flags.
        return False

    help_text = f"{result.stdout}\n{result.stderr}"
    return option in help_text


def _parse_progress(line: str, state: dict) -> dict | None:
    """
    Attempt to extract progress information from a gcb-runner output line.
    Returns an updated progress dict or None if nothing parseable.
    """
    # Detect tier transition
    m = _TIER_PATTERN.search(line)
    if m:
        state["tier"] = int(m.group(1))
        state["tier_total"] = int(m.group(2))

    # Extract final score
    m_score = _SCORE_PATTERN.search(line)
    if m_score:
        state["score"] = float(m_score.group(1))
        return state.copy()

    # Extract question progress
    m_prog = _PROGRESS_PATTERN.search(line)
    if m_prog:
        done = int(m_prog.group(1))
        total = int(m_prog.group(2))
        if total > 0 and done <= total:
            state["questions_done"] = done
            state["questions_total"] = total
            return state.copy()

    return None


# ---------------------------------------------------------------------------
# Main runner logic
# ---------------------------------------------------------------------------


def _gcb_runner_config_key(key_path: list[str]) -> str:
    """Read a nested key from ~/.gcb-runner/config.json."""
    try:
        config_path = Path.home() / ".gcb-runner" / "config.json"
        data = json.loads(config_path.read_text())
        val = data
        for k in key_path:
            val = val[k]
        return str(val)
    except Exception:
        return ""


def run_job(job_id: str, model_id: str) -> None:
    """Execute the benchmark test and update the job record throughout."""
    # Lazy import so the DB path is resolved correctly
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from gcb_mcp.jobs import JobManager  # noqa: PLC0415

    jm = JobManager()
    job = jm.get_job(job_id)
    if job is None:
        print(f"[wrapper] ERROR: job {job_id} not found in database", flush=True)
        sys.exit(1)

    log_path = Path(job.log_path) if job.log_path else (
        Path.home() / ".gcb-runner" / "data" / "jobs" / f"{job_id}.log"
    )
    export_path = Path(job.export_path) if job.export_path else (
        Path.home() / ".gcb-runner" / "data" / "jobs" / f"{job_id}-export.json"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    gcb_runner = _find_gcb_runner()

    cmd = [
        gcb_runner,
        "test",
        "--model", model_id,
        "--backend", "openrouter",
        "--judge-backend", "lmstudio",
        "--judge-model", "openai/gpt-oss-20b",
        "--output", str(export_path),
    ]
    if _runner_supports_test_option(gcb_runner, "--no-update-check"):
        cmd.append("--no-update-check")

    start_ts = datetime.now(timezone.utc).isoformat()

    with open(log_path, "w", buffering=1) as log_file:
        log_file.write(f"[{start_ts}] Starting job {job_id}\n")
        log_file.write(f"[{start_ts}] Model: {model_id}\n")
        log_file.write(f"[{start_ts}] Command: {' '.join(cmd)}\n\n")
        log_file.flush()

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={**os.environ},
            )
        except Exception as exc:
            jm.fail_job(job_id, f"Failed to launch gcb-runner: {exc}")
            log_file.write(f"\n[ERROR] Failed to launch gcb-runner: {exc}\n")
            return

        # Record the PID of the gcb-runner process
        jm.update_pid(job_id, proc.pid)

        progress_state: dict = {"tier": 0, "questions_done": 0, "questions_total": 0}
        last_heartbeat = time.time()
        final_score: float | None = None

        assert proc.stdout is not None
        for raw_line in proc.stdout:
            # Strip ANSI escape codes for clean log output
            clean = re.sub(r"\x1b\[[0-9;]*[mGKHF]", "", raw_line).rstrip()
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            log_file.write(f"[{ts}] {clean}\n")

            progress = _parse_progress(clean, progress_state)
            if progress is not None:
                if "score" in progress:
                    final_score = progress["score"]
                # Write heartbeat at most every 10 seconds to reduce DB churn
                now = time.time()
                if now - last_heartbeat >= 10:
                    jm.update_progress(job_id, progress)
                    last_heartbeat = now

        proc.wait()
        end_ts = datetime.now(timezone.utc).isoformat()
        log_file.write(f"\n[{end_ts}] gcb-runner exited with code {proc.returncode}\n")

        # Exit code 2 from gcb-runner means the run completed but is
        # COMPLETE_INVALID (extraction failures). The export file is real
        # and worth inspecting, so we record it as succeeded — but the
        # upload gate in MCP (upload_json / upload_result) will refuse to
        # publish it without an explicit allow_invalid=True override.
        if proc.returncode in (0, 2):
            if final_score is None and export_path.exists():
                try:
                    data = json.loads(export_path.read_text())
                    final_score = float(data.get("summary", {}).get("score", 0))
                except Exception:
                    pass

            jm.complete_job(
                job_id,
                score=final_score or 0.0,
                export_path=str(export_path) if export_path.exists() else None,
            )
            if proc.returncode == 0:
                log_file.write(f"[{end_ts}] Job {job_id} SUCCEEDED. Score: {final_score}\n")
            else:
                log_file.write(
                    f"[{end_ts}] Job {job_id} SUCCEEDED but marked "
                    "COMPLETE_INVALID by runner; upload will be refused "
                    "unless allow_invalid=True.\n"
                )
        else:
            log_file.flush()
            error_context = _tail_log(log_path, 20)
            error_msg = f"gcb-runner exited with code {proc.returncode}. Last output:\n{error_context}"
            jm.fail_job(job_id, error_msg)
            log_file.write(f"[{end_ts}] Job {job_id} FAILED.\n")


def _tail_log(path: Path, n: int) -> str:
    """Return last n lines of a log file as a string."""
    try:
        lines = path.read_text(errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python -m gcb_mcp.wrapper <job_id> <model_id>", file=sys.stderr)
        sys.exit(1)

    _job_id = sys.argv[1]
    _model_id = sys.argv[2]

    run_job(_job_id, _model_id)
