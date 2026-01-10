"""Static HTML report generator."""

import json
import sqlite3
from pathlib import Path
from typing import Any


def generate_report(
    db_path: Path,
    run_id: int,
    output: Path,
    compare_run_id: int | None = None,
) -> Path:
    """Generate a static HTML report for a test run."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get run data
        run = _get_run_detail(conn, run_id)
        responses = _get_all_responses(conn, run_id)
        
        # Get comparison data if requested
        compare_run = None
        compare_responses = None
        if compare_run_id:
            compare_run = _get_run_detail(conn, compare_run_id)
            compare_responses = _get_all_responses(conn, compare_run_id)
        
        # Generate HTML
        html = _get_report_template(run, responses, compare_run, compare_responses)
        
        output.write_text(html)
        return output
    finally:
        conn.close()


def _get_run_detail(conn: sqlite3.Connection, run_id: int) -> dict[str, Any]:
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
        raise ValueError(f"Run {run_id} not found")
    
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
        "judge_backend": row.get("judge_backend"),
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


def _get_all_responses(conn: sqlite3.Connection, run_id: int) -> list[dict[str, Any]]:
    """Get all responses for a run."""
    cursor = conn.execute("""
        SELECT id, question_id, tier, category, response_text,
               verdict, judge_reasoning, thought_process, response_time_ms
        FROM responses
        WHERE test_run_id = ?
        ORDER BY tier, id
    """, (run_id,))
    
    responses = []
    for row in cursor:
        responses.append({
            "id": row["id"],
            "question_id": row["question_id"],
            "tier": row["tier"],
            "category": row["category"],
            "response_text": row["response_text"],
            "verdict": row["verdict"],
            "judge_reasoning": row["judge_reasoning"],
            "thought_process": row["thought_process"],
            "response_time_ms": row["response_time_ms"],
        })
    
    return responses


def _get_report_template(
    run: dict[str, Any],
    responses: list[dict[str, Any]],
    compare_run: dict[str, Any] | None = None,
    compare_responses: list[dict[str, Any]] | None = None,
) -> str:
    """Generate the report HTML."""
    
    # Format score values for display
    score_display = f"{run['score']:.1f}" if run.get("score") is not None else "-"
    tier1_display = f"{run['tier1_score']:.1f}" if run.get("tier1_score") is not None else "-"
    tier2_display = f"{run['tier2_score']:.1f}" if run.get("tier2_score") is not None else "-"
    tier3_display = f"{run['tier3_score']:.1f}" if run.get("tier3_score") is not None else "-"
    
    # Escape function for JSON embedding
    run_json = json.dumps(run)
    responses_json = json.dumps(responses)
    
    # Comparison data is prepared but not yet used in the template
    # This is reserved for future comparison feature implementation
    # For now, we only use run and responses in the template
    compare_run_json = json.dumps(compare_run) if compare_run else "null"
    compare_responses_json = json.dumps(compare_responses) if compare_responses else "null"
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCB Report - {run["model"]}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }}
        
        .container {{ max-width: 1000px; margin: 0 auto; padding: 2rem; }}
        
        header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border);
        }}
        
        header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        header .meta {{ color: var(--text-muted); }}
        
        .card {{
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        
        .card h2 {{ margin-bottom: 1rem; font-size: 1.25rem; }}
        
        .score-hero {{
            text-align: center;
            padding: 2rem;
        }}
        
        .score-big {{
            font-size: 5rem;
            font-weight: bold;
            color: var(--primary);
            line-height: 1;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }}
        
        .stat-box {{
            text-align: center;
            padding: 1rem;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        
        .stat-label {{
            color: var(--text-muted);
            font-size: 0.875rem;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .badge-pass {{ background: #dcfce7; color: #166534; }}
        .badge-partial {{ background: #fef3c7; color: #92400e; }}
        .badge-fail {{ background: #fee2e2; color: #991b1b; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }}
        
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.75rem;
            text-transform: uppercase;
        }}
        
        .response-text {{
            background: var(--bg);
            padding: 0.75rem;
            border-radius: 4px;
            font-size: 0.875rem;
            white-space: pre-wrap;
        }}
        
        .response-text.collapsed {{
            max-height: 100px;
            overflow: hidden;
            position: relative;
        }}
        
        .response-text.collapsed::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 40px;
            background: linear-gradient(transparent, var(--bg));
            pointer-events: none;
        }}
        
        .toggle-btn {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            cursor: pointer;
            margin-top: 0.5rem;
        }}
        
        .toggle-btn:hover {{
            opacity: 0.9;
        }}
        
        .chart-container {{
            height: 200px;
            position: relative;
        }}
        
        .filters {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        
        .filters select {{
            padding: 0.5rem;
            border: 1px solid var(--border);
            border-radius: 4px;
        }}
        
        .tier-section {{
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
        }}
        
        .tier-section h3 {{
            margin-bottom: 1rem;
        }}
        
        @media print {{
            body {{ background: white; }}
            .card {{ box-shadow: none; border: 1px solid var(--border); }}
            .filters {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Great Commission Benchmark Report</h1>
            <p class="meta">Generated from GCB Runner</p>
        </header>
        
        <div class="card score-hero">
            <div class="score-big" id="score">{score_display}</div>
            <h2 style="margin-top: 0.5rem;">{run["model"]}</h2>
            <p class="meta">
                Benchmark v{run["benchmark_version"]} • 
                {run["completed_at"][:10] if run["completed_at"] else "In Progress"}
            </p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Verdict Distribution</h2>
                <div class="chart-container">
                    <canvas id="verdictChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>Tier Breakdown</h2>
                <div class="chart-container">
                    <canvas id="tierChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Test Details</h2>
            <div class="grid">
                <div class="stat-box">
                    <div class="stat-value">{run["accepted_count"]}</div>
                    <div class="stat-label">Accepted</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{run["compromised_count"]}</div>
                    <div class="stat-label">Compromised</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{run["refused_count"]}</div>
                    <div class="stat-label">Refused</div>
                </div>
            </div>
            <table style="margin-top: 1rem;">
                <tr><td><strong>Backend</strong></td><td>{run["backend"]}</td></tr>
                <tr><td><strong>Judge Model</strong></td><td>{run["judge_model"]}</td></tr>
                {run.get("judge_backend") and f'<tr><td><strong>Judge Backend</strong></td><td>{run["judge_backend"]}</td></tr>' or ''}
                <tr><td><strong>Tier 1 Score</strong></td><td>{tier1_display}%</td></tr>
                <tr><td><strong>Tier 2 Score</strong></td><td>{tier2_display}%</td></tr>
                <tr><td><strong>Tier 3 Score</strong></td><td>{tier3_display}%</td></tr>
            </table>
        </div>
        
        <div class="card">
            <h2>All Responses</h2>
            <div class="filters">
                <select id="verdict-filter" onchange="filterResponses()">
                    <option value="">All Verdicts</option>
                    <option value="ACCEPTED">Accepted</option>
                    <option value="COMPROMISED">Compromised</option>
                    <option value="REFUSED">Refused</option>
                </select>
                <select id="tier-filter" onchange="filterResponses()">
                    <option value="">All Tiers</option>
                    <option value="1">Tier 1</option>
                    <option value="2">Tier 2</option>
                    <option value="3">Tier 3</option>
                </select>
            </div>
            <div id="responses-container"></div>
        </div>
        
        <footer style="text-align: center; margin-top: 2rem; color: var(--text-muted);">
            <p>Generated by GCB Runner • greatcommissionbenchmark.ai</p>
        </footer>
    </div>
    
    <script>
        const RUN = {run_json};
        const RESPONSES = {responses_json};
        
        // Initialize charts
        new Chart(document.getElementById('verdictChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Accepted', 'Compromised', 'Refused'],
                datasets: [{{
                    data: [RUN.accepted_count, RUN.compromised_count, RUN.refused_count],
                    backgroundColor: ['#16a34a', '#d97706', '#dc2626']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom' }} }}
            }}
        }});
        
        new Chart(document.getElementById('tierChart'), {{
            type: 'bar',
            data: {{
                labels: ['Tier 1 (70%)', 'Tier 2 (20%)', 'Tier 3 (10%)'],
                datasets: [{{
                    label: 'Score %',
                    data: [RUN.tier1_score || 0, RUN.tier2_score || 0, RUN.tier3_score || 0],
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {{ x: {{ beginAtZero: true, max: 100 }} }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text || '';
            return div.innerHTML;
        }}
        
        function filterResponses() {{
            const verdict = document.getElementById('verdict-filter').value;
            const tier = document.getElementById('tier-filter').value;
            
            let filtered = RESPONSES;
            if (verdict) filtered = filtered.filter(r => r.verdict === verdict);
            if (tier) filtered = filtered.filter(r => r.tier === parseInt(tier));
            
            renderResponses(filtered);
        }}
        
        function renderResponses(responses) {{
            const container = document.getElementById('responses-container');
            
            if (responses.length === 0) {{
                container.innerHTML = '<p class="meta">No responses match the filter.</p>';
                return;
            }}
            
            let html = '<table><thead><tr><th>Q#</th><th>Tier</th><th>Verdict</th><th>Response</th></tr></thead><tbody>';
            
            responses.forEach((r, idx) => {{
                const badgeClass = r.verdict === 'ACCEPTED' ? 'badge-pass' : 
                                   r.verdict === 'COMPROMISED' ? 'badge-partial' : 'badge-fail';
                const isLong = r.response_text.length > 200;
                const collapsedClass = isLong ? 'collapsed' : '';
                const toggleBtn = isLong ? `<button class="toggle-btn" onclick="toggleResponse(${{idx}})">Show more</button>` : '';
                
                let thoughtProcessHtml = '';
                if (r.thought_process) {{
                    const isThoughtLong = r.thought_process.length > 200;
                    const thoughtCollapsedClass = isThoughtLong ? 'collapsed' : '';
                    const thoughtToggleBtn = isThoughtLong ? `<button class="toggle-btn" onclick="toggleThought(${{idx}})">Show more</button>` : '';
                    thoughtProcessHtml = `
                        <div style="margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border);">
                            <div style="font-weight: 600; margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.75rem;">THOUGHT PROCESS:</div>
                            <div class="response-text ${{thoughtCollapsedClass}}" id="thought-${{idx}}">${{escapeHtml(r.thought_process)}}</div>
                            ${{thoughtToggleBtn}}
                        </div>
                    `;
                }}
                
                html += `<tr>
                    <td>Q${{r.question_id}}</td>
                    <td>${{r.tier}}</td>
                    <td><span class="badge ${{badgeClass}}">${{r.verdict}}</span></td>
                    <td>
                        <div class="response-text ${{collapsedClass}}" id="response-${{idx}}">${{escapeHtml(r.response_text)}}</div>
                        ${{toggleBtn}}
                        ${{thoughtProcessHtml}}
                    </td>
                </tr>`;
            }});
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }}
        
        function toggleResponse(idx) {{
            const el = document.getElementById('response-' + idx);
            const btn = el.nextElementSibling;
            if (el.classList.contains('collapsed')) {{
                el.classList.remove('collapsed');
                btn.textContent = 'Show less';
            }} else {{
                el.classList.add('collapsed');
                btn.textContent = 'Show more';
            }}
        }}
        
        function toggleThought(idx) {{
            const el = document.getElementById('thought-' + idx);
            const btn = el.nextElementSibling;
            if (el.classList.contains('collapsed')) {{
                el.classList.remove('collapsed');
                btn.textContent = 'Show less';
            }} else {{
                el.classList.add('collapsed');
                btn.textContent = 'Show more';
            }}
        }}
        
        // Initial render
        filterResponses();
    </script>
</body>
</html>'''
