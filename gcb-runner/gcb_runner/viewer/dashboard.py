"""Embedded HTML/JS dashboard for the results viewer."""


def get_dashboard_html() -> str:
    """Return the complete dashboard HTML."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCB Results Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        header h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        header p {
            color: var(--text-muted);
            font-size: 0.875rem;
        }
        
        .card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        
        .card h2, .card h3 {
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .score-big {
            font-size: 4rem;
            font-weight: bold;
            color: var(--primary);
            line-height: 1;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        th {
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        
        tr:hover {
            background: var(--bg);
        }
        
        tr.clickable {
            cursor: pointer;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .badge-pass { background: #dcfce7; color: #166534; }
        .badge-partial { background: #fef3c7; color: #92400e; }
        .badge-fail { background: #fee2e2; color: #991b1b; }
        
        .btn {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: background 0.2s;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        
        .btn-secondary {
            background: var(--border);
            color: var(--text);
        }
        
        .btn-secondary:hover {
            background: #cbd5e1;
        }
        
        .chart-container {
            position: relative;
            height: 200px;
        }
        
        .meta {
            color: var(--text-muted);
            font-size: 0.875rem;
        }
        
        .response-card {
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .response-card .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .response-text {
            background: var(--bg);
            padding: 0.75rem;
            border-radius: 4px;
            font-size: 0.875rem;
            margin-top: 0.5rem;
            white-space: pre-wrap;
            overflow: hidden;
            position: relative;
        }
        
        .response-text.collapsed {
            max-height: 150px;
        }
        
        .response-text.collapsed.has-overflow::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 50px;
            background: linear-gradient(transparent, var(--bg));
            pointer-events: none;
        }
        
        .response-text.expanded {
            max-height: none;
        }
        
        .expand-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            margin-top: 0.5rem;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            color: var(--primary);
            background: transparent;
            border: 1px solid var(--primary);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .expand-btn:hover {
            background: var(--primary);
            color: white;
        }
        
        .expand-btn .icon {
            transition: transform 0.2s;
        }
        
        .expand-btn.expanded .icon {
            transform: rotate(180deg);
        }
        
        .pagination {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            margin-top: 1rem;
        }
        
        .pagination button {
            padding: 0.5rem 1rem;
            border: 1px solid var(--border);
            background: white;
            border-radius: 4px;
            cursor: pointer;
        }
        
        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .pagination button.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }
        
        .filters {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }
        
        .filters select {
            padding: 0.5rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 0.875rem;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
        }
        
        .elevated-access-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: #dbeafe;
            color: #1e40af;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-left: 0.5rem;
        }
        
        .question-text-section {
            background: #fffbeb;
            border-left: 3px solid #f59e0b;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Great Commission Benchmark</h1>
                <p>Results Viewer <span id="elevated-badge" style="display: none;" class="elevated-access-badge">Developer Access</span></p>
            </div>
        </header>
        
        <div id="app">
            <div class="loading">Loading...</div>
        </div>
    </div>
    
    <script>
        const App = {
            state: {
                runs: [],
                currentRun: null,
                responses: [],
                responsesPage: 1,
                responsesTotal: 0,
                responsesPagesTotal: 1,
                verdictFilter: '',
                tierFilter: '',
                // User access level info
                hasElevatedAccess: false,
                userRole: null,
            },
            
            async init() {
                // Load user info first to determine access level
                await this.loadUserInfo();
                await this.loadRuns();
                
                // Check URL for run param
                const params = new URLSearchParams(window.location.search);
                const runId = params.get('run');
                if (runId) {
                    await this.loadRunDetail(parseInt(runId));
                }
                
                this.render();
            },
            
            async loadUserInfo() {
                try {
                    // Force refresh on initial load to get latest permissions
                    const res = await fetch('/api/user-info?refresh=true');
                    const data = await res.json();
                    this.state.hasElevatedAccess = data.is_admin || data.is_benchmark_developer || false;
                    this.state.userRole = data.role || null;
                } catch (e) {
                    // If user info fails, default to no elevated access
                    this.state.hasElevatedAccess = false;
                    this.state.userRole = null;
                }
            },
            
            async loadRuns() {
                const res = await fetch('/api/runs');
                const data = await res.json();
                this.state.runs = data.runs || [];
            },
            
            async loadRunDetail(runId) {
                const res = await fetch(`/api/runs/${runId}`);
                this.state.currentRun = await res.json();
                await this.loadResponses(runId);
                this.render();
            },
            
            async loadResponses(runId, page = 1) {
                const params = new URLSearchParams({
                    run_id: runId,
                    page: page,
                    per_page: 20,
                });
                if (this.state.verdictFilter) params.set('verdict', this.state.verdictFilter);
                if (this.state.tierFilter) params.set('tier', this.state.tierFilter);
                
                const res = await fetch(`/api/responses?${params}`);
                const data = await res.json();
                this.state.responses = data.responses || [];
                this.state.responsesPage = data.page;
                this.state.responsesTotal = data.total;
                this.state.responsesPagesTotal = data.pages;
                // Update elevated access from response (server-side check)
                if (data.has_elevated_access !== undefined) {
                    this.state.hasElevatedAccess = data.has_elevated_access;
                }
            },
            
            goBack() {
                this.state.currentRun = null;
                this.state.responses = [];
                this.state.verdictFilter = '';
                this.state.tierFilter = '';
                window.history.pushState({}, '', '/');
                this.render();
            },
            
            async filterChanged() {
                this.state.verdictFilter = document.getElementById('verdict-filter')?.value || '';
                this.state.tierFilter = document.getElementById('tier-filter')?.value || '';
                this.state.responsesPage = 1;
                await this.loadResponses(this.state.currentRun.id);
                this.render();
            },
            
            async changePage(page) {
                await this.loadResponses(this.state.currentRun.id, page);
                this.render();
            },
            
            render() {
                const app = document.getElementById('app');
                
                // Show/hide elevated access badge
                const badge = document.getElementById('elevated-badge');
                if (badge) {
                    badge.style.display = this.state.hasElevatedAccess ? 'inline-block' : 'none';
                }
                
                if (this.state.currentRun) {
                    app.innerHTML = this.renderRunDetail();
                    this.renderCharts();
                    // Check for overflow after DOM is updated
                    requestAnimationFrame(() => this.checkOverflows());
                } else {
                    app.innerHTML = this.renderRunList();
                }
            },
            
            renderRunList() {
                if (this.state.runs.length === 0) {
                    return `
                        <div class="card">
                            <p class="meta">No test runs found. Run 'gcb-runner test' to get started.</p>
                        </div>
                    `;
                }
                
                return `
                    <div class="card">
                        <h2>Test Runs</h2>
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Model</th>
                                    <th>Version</th>
                                    <th>Score</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${this.state.runs.map(r => `
                                    <tr class="clickable" onclick="App.loadRunDetail(${r.id})">
                                        <td>${r.id}</td>
                                        <td>${r.model}</td>
                                        <td>${r.benchmark_version}</td>
                                        <td><strong>${r.score ? r.score.toFixed(1) : '-'}</strong></td>
                                        <td>${r.completed_at ? new Date(r.completed_at).toLocaleDateString() : '-'}</td>
                                        <td>${r.completed_at ? '<span class="badge badge-pass">Done</span>' : '<span class="badge badge-partial">Running</span>'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            },
            
            renderRunDetail() {
                const run = this.state.currentRun;
                return `
                    <button class="btn btn-secondary" onclick="App.goBack()">← Back to Runs</button>
                    
                    <div class="grid" style="margin-top: 1rem;">
                        <div class="card">
                            <h2>${run.model}</h2>
                            <div class="score-big">${run.score ? run.score.toFixed(1) : '-'}</div>
                            <p class="meta" style="margin-top: 0.5rem;">
                                Benchmark v${run.benchmark_version} • 
                                ${run.completed_at ? new Date(run.completed_at).toLocaleString() : 'In Progress'}
                            </p>
                            <p class="meta">Backend: ${run.backend} • Judge: ${run.judge_model}${run.judge_backend ? ` (via ${run.judge_backend})` : ''}</p>
                        </div>
                        
                        <div class="card">
                            <h3>Verdict Distribution</h3>
                            <div class="chart-container">
                                <canvas id="verdictChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Score Breakdown by Tier</h3>
                        <div class="chart-container" style="height: 150px;">
                            <canvas id="tierChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Responses</h3>
                        
                        <div class="filters">
                            <select id="verdict-filter" onchange="App.filterChanged()">
                                <option value="">All Verdicts</option>
                                <option value="ACCEPTED" ${this.state.verdictFilter === 'ACCEPTED' ? 'selected' : ''}>Accepted</option>
                                <option value="COMPROMISED" ${this.state.verdictFilter === 'COMPROMISED' ? 'selected' : ''}>Compromised</option>
                                <option value="REFUSED" ${this.state.verdictFilter === 'REFUSED' ? 'selected' : ''}>Refused</option>
                            </select>
                            <select id="tier-filter" onchange="App.filterChanged()">
                                <option value="">All Tiers</option>
                                <option value="1" ${this.state.tierFilter === '1' ? 'selected' : ''}>Tier 1 - Tasks</option>
                                <option value="2" ${this.state.tierFilter === '2' ? 'selected' : ''}>Tier 2 - Doctrine</option>
                                <option value="3" ${this.state.tierFilter === '3' ? 'selected' : ''}>Tier 3 - Worldview</option>
                            </select>
                            <span class="meta" style="align-self: center;">
                                Showing ${this.state.responses.length} of ${this.state.responsesTotal} responses
                            </span>
                        </div>
                        
                        ${this.state.responses.map((r, idx) => `
                            <div class="response-card">
                                <div class="header">
                                    <div>
                                        <strong>Q${r.question_id}</strong>
                                        <span class="meta" style="margin-left: 0.5rem;">
                                            Tier ${r.tier}${r.category ? ' • ' + r.category : ''}
                                        </span>
                                    </div>
                                    <span class="badge ${r.verdict === 'ACCEPTED' ? 'badge-pass' : r.verdict === 'COMPROMISED' ? 'badge-partial' : 'badge-fail'}">${r.verdict}</span>
                                </div>
                                ${r.question_text ? `
                                    <div class="meta" style="font-weight: 500; margin-top: 0.5rem;">Question:</div>
                                    <div class="response-text question-text-section collapsed" id="question-${idx}" data-full-height="0">${this.escapeHtml(r.question_text)}</div>
                                    <button class="expand-btn" id="expand-question-btn-${idx}" onclick="App.toggleExpand('question-${idx}', 'expand-question-btn-${idx}')" style="display: none;">
                                        <span class="icon">▼</span> <span class="label">Show full question</span>
                                    </button>
                                ` : ''}
                                <div class="meta" style="font-weight: 500; margin-top: 0.5rem;">Model Response:</div>
                                <div class="response-text collapsed" id="response-${idx}" data-full-height="0">${this.escapeHtml(r.response_text)}</div>
                                <button class="expand-btn" id="expand-btn-${idx}" onclick="App.toggleExpand('response-${idx}', 'expand-btn-${idx}')" style="display: none;">
                                    <span class="icon">▼</span> <span class="label">Show full response</span>
                                </button>
                                ${r.judge_reasoning ? `
                                    <div class="meta" style="margin-top: 0.75rem; font-weight: 500;">Judge Reasoning:</div>
                                    <div class="response-text collapsed" id="reasoning-${idx}" data-full-height="0">${this.escapeHtml(r.judge_reasoning)}</div>
                                    <button class="expand-btn" id="expand-reasoning-btn-${idx}" onclick="App.toggleExpand('reasoning-${idx}', 'expand-reasoning-btn-${idx}')" style="display: none;">
                                        <span class="icon">▼</span> <span class="label">Show full reasoning</span>
                                    </button>
                                ` : ''}
                                ${r.thought_process ? `
                                    <div class="meta" style="margin-top: 0.75rem; font-weight: 500;">Thought Process:</div>
                                    <div class="response-text collapsed" id="thought-${idx}" data-full-height="0">${this.escapeHtml(r.thought_process)}</div>
                                    <button class="expand-btn" id="expand-thought-btn-${idx}" onclick="App.toggleExpand('thought-${idx}', 'expand-thought-btn-${idx}')" style="display: none;">
                                        <span class="icon">▼</span> <span class="label">Show full thought process</span>
                                    </button>
                                ` : ''}
                            </div>
                        `).join('')}
                        
                        ${this.state.responsesPagesTotal > 1 ? `
                            <div class="pagination">
                                <button onclick="App.changePage(${this.state.responsesPage - 1})" 
                                        ${this.state.responsesPage <= 1 ? 'disabled' : ''}>
                                    Previous
                                </button>
                                <span class="meta" style="align-self: center; margin: 0 1rem;">
                                    Page ${this.state.responsesPage} of ${this.state.responsesPagesTotal}
                                </span>
                                <button onclick="App.changePage(${this.state.responsesPage + 1})"
                                        ${this.state.responsesPage >= this.state.responsesPagesTotal ? 'disabled' : ''}>
                                    Next
                                </button>
                            </div>
                        ` : ''}
                    </div>
                `;
            },
            
            renderCharts() {
                const run = this.state.currentRun;
                
                // Verdict distribution pie chart
                new Chart(document.getElementById('verdictChart'), {
                    type: 'doughnut',
                    data: {
                        labels: ['Accepted', 'Compromised', 'Refused'],
                        datasets: [{
                            data: [run.accepted_count, run.compromised_count, run.refused_count],
                            backgroundColor: ['#16a34a', '#d97706', '#dc2626']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
                
                // Tier breakdown bar chart
                new Chart(document.getElementById('tierChart'), {
                    type: 'bar',
                    data: {
                        labels: ['Tier 1 (70%)', 'Tier 2 (20%)', 'Tier 3 (10%)'],
                        datasets: [{
                            label: 'Score %',
                            data: [run.tier1_score || 0, run.tier2_score || 0, run.tier3_score || 0],
                            backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        indexAxis: 'y',
                        scales: {
                            x: {
                                beginAtZero: true,
                                max: 100
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            },
            
            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            },
            
            toggleExpand(textId, btnId) {
                const textEl = document.getElementById(textId);
                const btnEl = document.getElementById(btnId);
                
                if (textEl.classList.contains('collapsed')) {
                    textEl.classList.remove('collapsed');
                    textEl.classList.add('expanded');
                    btnEl.classList.add('expanded');
                    btnEl.querySelector('.label').textContent = 'Show less';
                } else {
                    textEl.classList.remove('expanded');
                    textEl.classList.add('collapsed');
                    btnEl.classList.remove('expanded');
                    // Determine the correct label based on the text element type
                    let label = 'Show full response';
                    if (textId.includes('reasoning')) {
                        label = 'Show full reasoning';
                    } else if (textId.includes('question')) {
                        label = 'Show full question';
                    }
                    btnEl.querySelector('.label').textContent = label;
                }
            },
            
            checkOverflows() {
                // Check all response-text elements for overflow
                document.querySelectorAll('.response-text.collapsed').forEach(el => {
                    const id = el.id;
                    let btnId;
                    if (id.includes('reasoning')) {
                        btnId = 'expand-reasoning-btn-' + id.split('-').pop();
                    } else if (id.includes('question')) {
                        btnId = 'expand-question-btn-' + id.split('-').pop();
                    } else {
                        btnId = 'expand-btn-' + id.split('-').pop();
                    }
                    const btn = document.getElementById(btnId);
                    
                    // Check if content overflows
                    if (el.scrollHeight > 150) {
                        el.classList.add('has-overflow');
                        if (btn) btn.style.display = 'inline-flex';
                    } else {
                        el.classList.remove('has-overflow');
                        if (btn) btn.style.display = 'none';
                    }
                });
            }
        };
        
        App.init();
    </script>
</body>
</html>'''
