"""HTTP server using Python stdlib for the results viewer."""

import json
import sqlite3
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import ParseResult, parse_qs, urlparse

from gcb_runner.viewer.dashboard import get_dashboard_html


# Module-level cache for user info and questions (shared across requests)
_user_info_cache: dict[str, Any] | None = None
_cached_api_key: str | None = None  # Track which API key was used for cache
_questions_cache: dict[str, str] = {}  # question_id -> content


def _clear_user_info_cache() -> None:
    """Clear the user info cache to force refresh on next request."""
    global _user_info_cache, _cached_api_key
    _user_info_cache = None
    _cached_api_key = None


def _load_user_info(force_refresh: bool = False) -> dict[str, Any]:
    """Load user info from Platform API (cached, but invalidates on API key change).
    
    Args:
        force_refresh: If True, bypass cache and fetch fresh data
    """
    global _user_info_cache, _cached_api_key
    
    try:
        from gcb_runner.config import Config
        from gcb_runner.api.client import get_user_info_sync
        
        config = Config.load()
        api_key = config.platform.api_key
        base_url = config.platform.url
        
        # Force refresh if requested
        if force_refresh:
            _user_info_cache = None
            _cached_api_key = None
        
        # Invalidate cache if API key changed
        if _user_info_cache is not None and _cached_api_key != api_key:
            _user_info_cache = None
            _cached_api_key = None
        
        # Return cached value if available and API key matches
        if _user_info_cache is not None and _cached_api_key == api_key and not force_refresh:
            return _user_info_cache
        
        # Default non-admin response
        default_info = {
            "role": None,
            "is_admin": False,
            "is_benchmark_developer": False,
            "is_moderator": False,
        }
        
        if not api_key:
            _user_info_cache = default_info
            _cached_api_key = None
            return _user_info_cache
        
        result = get_user_info_sync(api_key, base_url)
        if result:
            _user_info_cache = result
            _cached_api_key = api_key
        else:
            _user_info_cache = default_info
            _cached_api_key = None
            
    except Exception:
        default_info = {
            "role": None,
            "is_admin": False,
            "is_benchmark_developer": False,
            "is_moderator": False,
        }
        _user_info_cache = default_info
        _cached_api_key = None
    
    return _user_info_cache


def _load_questions_for_version(version: str) -> dict[str, str]:
    """Load questions from cache for a specific version.
    
    Returns a mapping of question_id -> question content.
    """
    global _questions_cache
    
    try:
        from gcb_runner.api.cache import QuestionCache
        
        cache = QuestionCache()
        data = cache.get(version)
        
        if data and "questions" in data:
            for q in data["questions"]:
                q_id = q.get("id", "")
                q_content = q.get("content", "")
                if q_id and q_content:
                    _questions_cache[q_id] = q_content
                    
    except Exception:
        pass
    
    return _questions_cache


def _fetch_questions_from_api(version: str | None = None) -> dict[str, str]:
    """Fetch questions from the Platform API for elevated users (synchronous).
    
    Returns a mapping of question_id -> question content.
    """
    try:
        import httpx
        from gcb_runner.config import Config
        
        config = Config.load()
        api_key = config.platform.api_key
        base_url = config.platform.url
        
        if not api_key:
            return {}
        
        # Build URL
        url_path = "/api/runner/questions"
        if version and version != "current":
            url_path += f"?version={version}"
        
        # Make synchronous request
        with httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={
                "X-API-Key": api_key,
                "User-Agent": "gcb-runner/0.1.1",
            },
            timeout=30.0,
            verify=False,  # Allow SSL issues for Railway
        ) as client:
            response = client.get(url_path)
            
            if response.status_code == 200:
                questions_data = response.json()
                questions = questions_data.get("questions", [])
                result = {}
                for q in questions:
                    q_id = q.get("id", "")
                    q_content = q.get("content", "")
                    if q_id and q_content:
                        result[q_id] = q_content
                return result
    except Exception:
        # Silently fail - questions will just not be shown
        pass
    
    return {}


def _get_question_text(question_id: str, version: str | None = None, fetch_from_api: bool = False) -> str | None:
    """Get question text for a question ID.
    
    Tries to find the question in the cache. If not found and version is provided,
    loads questions for that version first. If still not found and fetch_from_api is True,
    attempts to fetch from the Platform API.
    """
    # Check if already in cache
    if question_id in _questions_cache:
        return _questions_cache[question_id]
    
    # Try to load from version cache
    if version:
        _load_questions_for_version(version)
        if question_id in _questions_cache:
            return _questions_cache[question_id]
    
    # If still not found and API fetch is requested, try fetching from API
    if fetch_from_api and version:
        api_questions = _fetch_questions_from_api(version)
        # Update cache with fetched questions
        _questions_cache.update(api_questions)
        return api_questions.get(question_id)
    
    return None


class ViewerHandler(BaseHTTPRequestHandler):
    """Custom handler that serves the dashboard and API endpoints."""
    
    def __init__(self, *args: Any, db_path: Path, **kwargs: Any) -> None:
        self.db_path = db_path
        super().__init__(*args, **kwargs)
    
    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed = urlparse(self.path)
        
        # API endpoints
        if parsed.path.startswith("/api/"):
            self._handle_api(parsed)
        # Dashboard
        elif parsed.path == "/" or parsed.path == "/index.html":
            self._serve_dashboard()
        else:
            self._send_error(404, "Not found")
    
    def _handle_api(self, parsed: ParseResult) -> None:
        """Handle API requests by querying SQLite."""
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # User info endpoint doesn't need database
        if path == "/api/user-info":
            # Check for force refresh parameter
            force_refresh = params.get("refresh", [None])[0] == "true"
            user_info = _load_user_info(force_refresh=force_refresh)
            self._send_json(user_info)
            return
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            if path == "/api/runs":
                data = self._get_runs(conn)
            elif path.startswith("/api/runs/"):
                try:
                    run_id = int(path.split("/")[-1])
                    data = self._get_run_detail(conn, run_id)
                except ValueError:
                    self._send_error(400, "Invalid run ID")
                    return
            elif path == "/api/responses":
                run_id = int(params.get("run_id", [0])[0])
                data = self._get_responses(conn, run_id, params)
            else:
                self._send_error(404, "Not found")
                return
            
            self._send_json(data)
        finally:
            conn.close()
    
    def _get_runs(self, conn: sqlite3.Connection) -> dict[str, Any]:
        """Get list of test runs."""
        cursor = conn.execute("""
            SELECT id, model, backend, benchmark_version, judge_model, judge_backend,
                   score, tier1_score, tier2_score, tier3_score,
                   started_at, completed_at
            FROM test_runs
            ORDER BY started_at DESC
            LIMIT 100
        """)
        
        runs = []
        for row in cursor:
            runs.append({
                "id": row["id"],
                "model": row["model"],
                "backend": row["backend"],
                "benchmark_version": row["benchmark_version"],
                "judge_model": row["judge_model"],
                "judge_backend": row["judge_backend"] if "judge_backend" in row.keys() else None,
                "score": row["score"],
                "tier1_score": row["tier1_score"],
                "tier2_score": row["tier2_score"],
                "tier3_score": row["tier3_score"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
            })
        
        return {"runs": runs}
    
    def _get_run_detail(self, conn: sqlite3.Connection, run_id: int) -> dict[str, Any]:
        """Get detailed information for a single run."""
        cursor = conn.execute("""
            SELECT id, model, backend, benchmark_version, judge_model, judge_backend,
                   system_prompt, score, tier1_score, tier2_score, tier3_score,
                   started_at, completed_at
            FROM test_runs
            WHERE id = ?
        """, (run_id,))
        
        row = cursor.fetchone()
        if not row:
            return {"error": "Run not found"}
        
        # Get verdict counts
        verdict_cursor = conn.execute("""
            SELECT verdict, COUNT(*) as count
            FROM responses
            WHERE test_run_id = ?
            GROUP BY verdict
        """, (run_id,))
        
        verdict_counts = {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0}
        for vrow in verdict_cursor:
            # Map legacy/ERROR verdicts to REFUSED
            verdict = vrow["verdict"] if vrow["verdict"] in verdict_counts else "REFUSED"
            verdict_counts[verdict] += vrow["count"]
        
        return {
            "id": row["id"],
            "model": row["model"],
            "backend": row["backend"],
            "benchmark_version": row["benchmark_version"],
            "judge_model": row["judge_model"],
            "judge_backend": row["judge_backend"] if "judge_backend" in row.keys() else None,
            "score": row["score"],
            "tier1_score": row["tier1_score"],
            "tier2_score": row["tier2_score"],
            "tier3_score": row["tier3_score"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "accepted_count": verdict_counts["ACCEPTED"],
            "compromised_count": verdict_counts["COMPROMISED"],
            "refused_count": verdict_counts["REFUSED"],
        }
    
    def _get_responses(
        self, conn: sqlite3.Connection, run_id: int, params: dict[str, list[str]]
    ) -> dict[str, Any]:
        """Get responses for a run with optional filtering."""
        verdict_filter = params.get("verdict", [None])[0]
        tier_filter = params.get("tier", [None])[0]
        page = int(params.get("page", [1])[0])
        per_page = int(params.get("per_page", [20])[0])
        
        # Check if user has elevated access (admin or benchmark_developer)
        user_info = _load_user_info()
        has_elevated_access = user_info.get("is_admin", False) or user_info.get("is_benchmark_developer", False)
        
        # Get benchmark version for this run to load correct questions
        version_cursor = conn.execute(
            "SELECT benchmark_version FROM test_runs WHERE id = ?", (run_id,)
        )
        version_row = version_cursor.fetchone()
        benchmark_version = version_row["benchmark_version"] if version_row else None
        
        # For elevated users, ensure questions are loaded for this version
        if has_elevated_access and benchmark_version:
            # Try loading from cache first
            _load_questions_for_version(benchmark_version)
            # Always try to fetch from API for elevated users to ensure we have questions
            # This ensures questions are available even if cache is empty or incomplete
            api_questions = _fetch_questions_from_api(benchmark_version)
            if api_questions:
                _questions_cache.update(api_questions)
        
        # Build query
        query = "SELECT * FROM responses WHERE test_run_id = ?"
        query_params: list[Any] = [run_id]
        
        if verdict_filter:
            query += " AND verdict = ?"
            query_params.append(verdict_filter)
        
        if tier_filter:
            query += " AND tier = ?"
            query_params.append(int(tier_filter))
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        count_cursor = conn.execute(count_query, query_params)
        total: int = count_cursor.fetchone()[0]
        
        # Get page
        query += f" ORDER BY tier, id LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        cursor = conn.execute(query, query_params)
        
        responses = []
        for row in cursor:
            response_text = row["response_text"]
            question_id = row["question_id"]
            
            # Build response object
            response_obj: dict[str, Any] = {
                "id": row["id"],
                "question_id": question_id,
                "tier": row["tier"],
                "category": row["category"],
                "verdict": row["verdict"],
                "judge_reasoning": row["judge_reasoning"],
                "thought_process": row["thought_process"] if "thought_process" in row.keys() else None,
                "response_time_ms": row["response_time_ms"],
            }
            
            if has_elevated_access:
                # Admin/benchmark_developer: show full response and question text
                response_obj["response_text"] = response_text
                # Questions should already be loaded in cache from above, but allow API fetch as fallback
                question_text = _get_question_text(question_id, benchmark_version, fetch_from_api=True)
                if question_text:
                    response_obj["question_text"] = question_text
            else:
                # Regular user: truncate response, no question text
                response_obj["response_text"] = (
                    response_text[:500] + "..." if len(response_text) > 500 else response_text
                )
            
            responses.append(response_obj)
        
        return {
            "responses": responses,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "has_elevated_access": has_elevated_access,
        }
    
    def _serve_dashboard(self) -> None:
        """Serve the embedded single-page dashboard."""
        html = get_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(html.encode())))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_json(self, data: dict[str, Any]) -> None:
        """Send a JSON response."""
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def _send_error(self, code: int, message: str) -> None:
        """Send an error response."""
        body = json.dumps({"error": message}).encode()
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_viewer(db_path: Path, port: int = 8642, open_browser: bool = True) -> None:
    """Start the results viewer server."""
    handler = partial(ViewerHandler, db_path=db_path)
    server = HTTPServer(("localhost", port), handler)
    
    if open_browser:
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
