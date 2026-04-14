"""Job tracking database for fire-and-forget GCB test runs."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator


def _get_jobs_db_path() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home())) if os.name == "nt" else Path.home()
    data_dir = base / ".gcb-runner" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "jobs.db"


def _get_jobs_dir() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home())) if os.name == "nt" else Path.home()
    jobs_dir = base / ".gcb-runner" / "data" / "jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    return jobs_dir


_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS gcb_jobs (
    id           TEXT PRIMARY KEY,
    model_id     TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'running',
    pid          INTEGER,
    log_path     TEXT,
    export_path  TEXT,
    started_at   TEXT NOT NULL,
    completed_at TEXT,
    progress     TEXT,
    error_message TEXT,
    score        REAL
);
"""


@dataclass
class Job:
    id: str
    model_id: str
    status: str
    pid: int | None
    log_path: str | None
    export_path: str | None
    started_at: str
    completed_at: str | None
    progress: dict | None
    error_message: str | None
    score: float | None

    def to_dict(self) -> dict:
        return {
            "job_id": self.id,
            "model_id": self.model_id,
            "status": self.status,
            "pid": self.pid,
            "log_path": self.log_path,
            "export_path": self.export_path,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "error_message": self.error_message,
            "score": self.score,
        }


def _row_to_job(row: tuple) -> Job:
    (
        job_id, model_id, status, pid, log_path, export_path,
        started_at, completed_at, progress_json, error_message, score,
    ) = row
    progress = None
    if progress_json:
        try:
            progress = json.loads(progress_json)
        except json.JSONDecodeError:
            pass
    return Job(
        id=job_id,
        model_id=model_id,
        status=status,
        pid=pid,
        log_path=log_path,
        export_path=export_path,
        started_at=started_at,
        completed_at=completed_at,
        progress=progress,
        error_message=error_message,
        score=score,
    )


class JobManager:
    """CRUD operations for GCB background test jobs."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or _get_jobs_db_path()
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE_SQL)
            conn.commit()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self._db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_job(self, job_id: str, model_id: str, pid: int | None = None) -> Job:
        jobs_dir = _get_jobs_dir()
        log_path = str(jobs_dir / f"{job_id}.log")
        export_path = str(jobs_dir / f"{job_id}-export.json")
        started_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO gcb_jobs
                    (id, model_id, status, pid, log_path, export_path, started_at)
                VALUES (?, ?, 'running', ?, ?, ?, ?)
                """,
                (job_id, model_id, pid, log_path, export_path, started_at),
            )
            conn.commit()

        return Job(
            id=job_id,
            model_id=model_id,
            status="running",
            pid=pid,
            log_path=log_path,
            export_path=export_path,
            started_at=started_at,
            completed_at=None,
            progress=None,
            error_message=None,
            score=None,
        )

    def get_job(self, job_id: str) -> Job | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM gcb_jobs WHERE id = ?", (job_id,)
            ).fetchone()
        if row is None:
            return None
        return _row_to_job(tuple(row))

    def list_jobs(self, status: str | None = None, limit: int = 100) -> list[Job]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM gcb_jobs WHERE status = ? ORDER BY started_at DESC LIMIT ?",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM gcb_jobs ORDER BY started_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [_row_to_job(tuple(r)) for r in rows]

    def update_progress(self, job_id: str, progress: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE gcb_jobs SET progress = ? WHERE id = ?",
                (json.dumps(progress), job_id),
            )
            conn.commit()

    def update_pid(self, job_id: str, pid: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE gcb_jobs SET pid = ? WHERE id = ?",
                (pid, job_id),
            )
            conn.commit()

    def complete_job(self, job_id: str, score: float, export_path: str | None = None) -> None:
        completed_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE gcb_jobs
                SET status = 'succeeded', score = ?, completed_at = ?,
                    export_path = COALESCE(?, export_path)
                WHERE id = ?
                """,
                (score, completed_at, export_path, job_id),
            )
            conn.commit()

    def fail_job(self, job_id: str, error_message: str) -> None:
        completed_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE gcb_jobs
                SET status = 'failed', error_message = ?, completed_at = ?
                WHERE id = ?
                """,
                (error_message, completed_at, job_id),
            )
            conn.commit()

    def cancel_job(self, job_id: str) -> None:
        completed_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE gcb_jobs
                SET status = 'cancelled', completed_at = ?
                WHERE id = ?
                """,
                (completed_at, job_id),
            )
            conn.commit()

    def reap_stale_jobs(self, max_hours: float = 3.0) -> list[str]:
        """Mark jobs running longer than max_hours as failed. Returns reaped job IDs."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, started_at FROM gcb_jobs WHERE status = 'running'"
            ).fetchall()

        reaped: list[str] = []
        now = datetime.now(timezone.utc)
        for row in rows:
            try:
                started = datetime.fromisoformat(row[1])
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                elapsed = (now - started).total_seconds() / 3600
                if elapsed > max_hours:
                    self.fail_job(row[0], f"Timed out after {elapsed:.1f} hours")
                    reaped.append(row[0])
            except Exception:
                pass
        return reaped
