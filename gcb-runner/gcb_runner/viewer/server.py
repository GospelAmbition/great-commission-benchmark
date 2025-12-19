"""HTTP server using Python stdlib for the results viewer."""

import json
import sqlite3
from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from gcb_runner.viewer.dashboard import get_dashboard_html


class ViewerHandler(BaseHTTPRequestHandler):
    """Custom handler that serves the dashboard and API endpoints."""
    
    def __init__(self, *args, db_path: Path, **kwargs):
        self.db_path = db_path
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
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
    
    def _handle_api(self, parsed):
        """Handle API requests by querying SQLite."""
        path = parsed.path
        params = parse_qs(parsed.query)
        
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
    
    def _get_runs(self, conn):
        """Get list of test runs."""
        cursor = conn.execute("""
            SELECT id, model, backend, benchmark_version, judge_model,
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
                "score": row["score"],
                "tier1_score": row["tier1_score"],
                "tier2_score": row["tier2_score"],
                "tier3_score": row["tier3_score"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
            })
        
        return {"runs": runs}
    
    def _get_run_detail(self, conn, run_id):
        """Get detailed information for a single run."""
        cursor = conn.execute("""
            SELECT id, model, backend, benchmark_version, judge_model,
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
            SELECT verdict_normalized, COUNT(*) as count
            FROM responses
            WHERE test_run_id = ?
            GROUP BY verdict_normalized
        """, (run_id,))
        
        verdict_counts = {"pass": 0, "partial": 0, "fail": 0}
        for vrow in verdict_cursor:
            verdict_counts[vrow["verdict_normalized"]] = vrow["count"]
        
        return {
            "id": row["id"],
            "model": row["model"],
            "backend": row["backend"],
            "benchmark_version": row["benchmark_version"],
            "judge_model": row["judge_model"],
            "system_prompt": row["system_prompt"],
            "score": row["score"],
            "tier1_score": row["tier1_score"],
            "tier2_score": row["tier2_score"],
            "tier3_score": row["tier3_score"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "pass_count": verdict_counts["pass"],
            "partial_count": verdict_counts["partial"],
            "fail_count": verdict_counts["fail"],
        }
    
    def _get_responses(self, conn, run_id, params):
        """Get responses for a run with optional filtering."""
        verdict_filter = params.get("verdict", [None])[0]
        tier_filter = params.get("tier", [None])[0]
        page = int(params.get("page", [1])[0])
        per_page = int(params.get("per_page", [20])[0])
        
        # Build query
        query = "SELECT * FROM responses WHERE test_run_id = ?"
        query_params = [run_id]
        
        if verdict_filter:
            query += " AND verdict_normalized = ?"
            query_params.append(verdict_filter)
        
        if tier_filter:
            query += " AND tier = ?"
            query_params.append(int(tier_filter))
        
        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        count_cursor = conn.execute(count_query, query_params)
        total = count_cursor.fetchone()[0]
        
        # Get page
        query += f" ORDER BY tier, id LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        cursor = conn.execute(query, query_params)
        
        responses = []
        for row in cursor:
            responses.append({
                "id": row["id"],
                "question_id": row["question_id"],
                "tier": row["tier"],
                "category": row["category"],
                "response_text": row["response_text"][:500] + "..." if len(row["response_text"]) > 500 else row["response_text"],
                "verdict": row["verdict"],
                "verdict_normalized": row["verdict_normalized"],
                "judge_reasoning": row["judge_reasoning"],
                "response_time_ms": row["response_time_ms"],
            })
        
        return {
            "responses": responses,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }
    
    def _serve_dashboard(self):
        """Serve the embedded single-page dashboard."""
        html = get_dashboard_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", len(html.encode()))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_json(self, data):
        """Send a JSON response."""
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def _send_error(self, code, message):
        """Send an error response."""
        body = json.dumps({"error": message}).encode()
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


def start_viewer(db_path: Path, port: int = 8642, open_browser: bool = True):
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
