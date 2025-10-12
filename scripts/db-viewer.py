#!/usr/bin/env python3
"""
Simple Database Viewer - Guaranteed to work!
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Database connection
DB_CONFIG = {
    'host': 'n8n-scraper-database',
    'port': 5432,
    'database': 'n8n_scraper',
    'user': 'scraper_user',
    'password': 'scraper_pass'
}

def get_workflows(limit=50, offset=0, search=None, sort_by='workflow_id', sort_order='DESC'):
    """Get workflows from database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        where_clause = ""
        params = []
        
        if search:
            where_clause = """WHERE w.workflow_id ILIKE %s 
                OR w.url ILIKE %s 
                OR wm.title ILIKE %s 
                OR wm.author_name ILIKE %s"""
            search_pattern = f"%{search}%"
            params = [search_pattern, search_pattern, search_pattern, search_pattern]
        
        # Always add limit and offset parameters
        params.extend([limit, offset])
        
        # Validate sort column to prevent SQL injection
        valid_sort_columns = {
            'workflow_id': 'workflow_id',
            'title': 'title',
            'category': 'category',
            'author_name': 'author_name',
            'views': 'views',
            'quality_score': 'quality_score',
            'workflow_difficulty_score': 'workflow_difficulty_score',
            'workflow_industry': 'workflow_industry',
            'extracted_at': 'extracted_at'
        }
        
        sort_column = valid_sort_columns.get(sort_by, 'workflow_id')
        sort_order = 'ASC' if sort_order.upper() == 'ASC' else 'DESC'
        
        query = f"""
            SELECT 
                w.workflow_id,
                COALESCE(
                    wm.title,
                    CASE 
                        WHEN w.url LIKE '%%/%%' THEN 
                            TRIM(
                                REPLACE(
                                    REGEXP_REPLACE(
                                        SUBSTRING(w.url FROM '[^/]+$'), 
                                        '^[0-9]+[[:space:]]*', 
                                        ''
                                    ), 
                                    '-', ' '
                                )
                            )
                        ELSE w.url
                    END
                ) as title,
                CASE 
                    WHEN wm.categories IS NOT NULL AND jsonb_array_length(wm.categories) > 0 
                    THEN wm.categories->>0
                    ELSE 'Uncategorized'
                END as category,
                wm.author_name,
                wm.views,
                w.quality_score,
                wm.workflow_difficulty_score,
                wm.workflow_industry,
                w.layer1_success,
                w.layer2_success,
                w.layer3_success,
                w.layer4_success,
                w.layer5_success,
                w.layer6_success,
                w.layer7_success,
                CASE 
                    WHEN w.quality_score > 0 THEN 'Success'
                    WHEN w.layer1_success OR w.layer2_success OR w.layer3_success THEN 'Partial'
                    WHEN w.extracted_at IS NOT NULL THEN 'Failed'
                    ELSE 'Pending'
                END as status,
                w.extracted_at
            FROM workflows w
            LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
            {where_clause}
            ORDER BY {sort_column} {sort_order}
            LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, params)
        workflows = cursor.fetchall()
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM workflows w LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id {where_clause}"
        # For count query, we only need search parameters (not limit/offset)
        if where_clause:
            # Has search: params = [search1, search2, search3, search4, limit, offset]
            count_params = params[:-2]  # Remove last 2 (limit, offset)
        else:
            # No search: params = [limit, offset]
            count_params = []  # No parameters needed for count
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        return [
            {
                'workflow_id': w['workflow_id'],
                'title': w['title'],
                'category': w['category'],
                'author_name': w['author_name'],
                'views': w['views'],
                'quality_score': float(w['quality_score']) if w['quality_score'] else 0,
                'workflow_difficulty_score': float(w['workflow_difficulty_score']) if w['workflow_difficulty_score'] else None,
                'workflow_industry': w['workflow_industry'],
                'layer1_success': w['layer1_success'],
                'layer2_success': w['layer2_success'],
                'layer3_success': w['layer3_success'],
                'layer4_success': w['layer4_success'],
                'layer5_success': w['layer5_success'],
                'layer6_success': w['layer6_success'],
                'layer7_success': w['layer7_success'],
                'status': w['status'],
                'extracted_at': w['extracted_at'].isoformat() if w['extracted_at'] else None
            }
            for w in workflows
        ], total
        
    except Exception as e:
        print(f"Error getting workflows: {e}")
        return [], 0

def get_workflow_details(workflow_id):
    """Get detailed information for a specific workflow"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get main workflow data
        cursor.execute("""
            SELECT * FROM workflows WHERE workflow_id = %s;
        """, (workflow_id,))
        
        workflow = cursor.fetchone()
        if not workflow:
            cursor.close()
            conn.close()
            return None
        
        # Get related data from other tables
        cursor.execute("""
            SELECT * FROM workflow_metadata WHERE workflow_id = %s;
        """, (workflow_id,))
        metadata = cursor.fetchone()
        
        cursor.execute("""
            SELECT * FROM workflow_structure WHERE workflow_id = %s;
        """, (workflow_id,))
        structure = cursor.fetchone()
        
        cursor.execute("""
            SELECT * FROM workflow_content WHERE workflow_id = %s;
        """, (workflow_id,))
        content = cursor.fetchone()
        
        cursor.execute("""
            SELECT * FROM video_transcripts WHERE workflow_id = %s;
        """, (workflow_id,))
        transcript = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        def convert_datetime(obj):
            """Convert datetime objects to ISO strings for JSON serialization"""
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                if isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                else:
                    return [convert_datetime(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # datetime object
                return obj.isoformat()
            elif hasattr(obj, 'to_eng_string'):  # Decimal type
                return float(obj)
            else:
                return obj
        
        return {
            'workflow': {
                'id': workflow['id'],
                'workflow_id': workflow['workflow_id'],
                'url': workflow['url'],
                'quality_score': float(workflow['quality_score']) if workflow['quality_score'] else 0,
                'layer1_success': workflow['layer1_success'],
                'layer2_success': workflow['layer2_success'],
                'layer3_success': workflow['layer3_success'],
                'processing_time': float(workflow['processing_time']) if workflow['processing_time'] else 0,
                'extracted_at': workflow['extracted_at'].isoformat() if workflow['extracted_at'] else None,
                'updated_at': workflow['updated_at'].isoformat() if workflow['updated_at'] else None,
                'error_message': workflow['error_message'],
                'retry_count': workflow['retry_count']
            },
            'metadata': convert_datetime(dict(metadata)) if metadata else None,
            'structure': convert_datetime(dict(structure)) if structure else None,
            'content': convert_datetime(dict(content)) if content else None,
            'transcript': convert_datetime(dict(transcript)) if transcript else None
        }
        
    except Exception as e:
        print(f"Error getting workflow details: {e}")
        return None

def get_statistics():
    """Get database statistics"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                COUNT(*) as total_workflows,
                COUNT(*) FILTER (WHERE layer1_success AND layer2_success AND layer3_success) as fully_successful,
                COUNT(*) FILTER (WHERE NOT (layer1_success AND layer2_success AND layer3_success)) as partial_success,
                COUNT(*) FILTER (WHERE error_message IS NOT NULL) as with_errors,
                ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
                ROUND(AVG(processing_time)::numeric, 2) as avg_processing_time
            FROM workflows
        """
        
        cursor.execute(query)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'total_workflows': int(stats['total_workflows']),
            'fully_successful': int(stats['fully_successful']),
            'partial_success': int(stats['partial_success']),
            'with_errors': int(stats['with_errors']),
            'avg_quality_score': float(stats['avg_quality_score']) if stats['avg_quality_score'] else 0,
            'avg_processing_time': float(stats['avg_processing_time']) if stats['avg_processing_time'] else 0,
            'success_rate': round((stats['fully_successful'] / stats['total_workflows'] * 100), 1) if stats['total_workflows'] > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_workflows': 0,
            'fully_successful': 0,
            'partial_success': 0,
            'with_errors': 0,
            'avg_quality_score': 0,
            'avg_processing_time': 0,
            'success_rate': 0
        }

class DBViewerHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        """Handle HEAD requests"""
        self.do_GET()
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)
        
        if path == '/':
            self.serve_dashboard()
        elif path.startswith('/workflow/'):
            # Extract workflow ID from path
            workflow_id = path.split('/')[-1]
            self.serve_workflow_details(workflow_id)
        elif path == '/api/workflows':
            # Get parameters
            page = int(params.get('page', [1])[0])
            search = params.get('search', [None])[0]
            sort_by = params.get('sort', ['workflow_id'])[0]
            sort_order = params.get('order', ['desc'])[0]
            limit = int(params.get('limit', [50])[0])
            
            workflows, total = get_workflows(
                limit=limit,
                offset=(page-1)*limit,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            response = {
                'workflows': workflows,
                'total': total,
                'page': page,
                'total_pages': (total + limit - 1) // limit
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif path == '/api/stats':
            stats = get_statistics()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
        elif path.startswith('/api/workflow/'):
            # API endpoint for workflow details
            workflow_id = path.split('/')[-1]
            details = get_workflow_details(workflow_id)
            
            if details:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(details).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        elif path == '/favicon.ico':
            self.serve_favicon('🗄️', '#667eea')
        elif path == '/favicon-detail.ico':
            self.serve_favicon('🔍', '#764ba2')
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗄️ N8N Scraper Database Viewer</title>
    <link rel="icon" href="/favicon.ico">
    <link rel="shortcut icon" href="/favicon.ico">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .controls {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1em;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .btn {{
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
        }}
        
        .table-container {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            background: #f8f9fa;
        }}
        
        th.sortable {{
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
        }}
        
        th.sortable:hover {{
            background: #e9ecef;
        }}
        
        th.sortable.sort-active {{
            background: #007bff;
            color: white;
        }}
        
        .sort-arrow {{
            font-size: 0.8em;
            opacity: 0.5;
        }}
        
        th.sortable.sort-active .sort-arrow {{
            opacity: 1;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-partial {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .quality-bar {{
            background: #e9ecef;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .quality-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .category-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 8px;
            font-size: 0.8em;
            font-weight: 500;
            background: #f0f9ff;
            color: #0369a1;
            border: 1px solid #bae6fd;
        }}
        
        .pagination {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .page-btn {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }}
        
        .page-btn:hover {{
            background: #667eea;
            color: white;
        }}
        
        .page-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .url-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ N8N Scraper Database</h1>
            <p>Interactive workflow data viewer</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Workflows</div>
                <div class="value" id="total-workflows">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Success Rate</div>
                <div class="value" id="success-rate">0%</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Quality</div>
                <div class="value" id="avg-quality">0%</div>
            </div>
            <div class="stat-card">
                <div class="label">Processing Time</div>
                <div class="value" id="processing-time">0s</div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-box" id="search-input" placeholder="Search by workflow ID or URL...">
            <button class="btn" onclick="searchWorkflows()">Search</button>
            <button class="btn" onclick="clearSearch()">Clear</button>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th class="sortable" data-sort="workflow_id">ID <span class="sort-arrow">↕</span></th>
                        <th class="sortable" data-sort="title">Title <span class="sort-arrow">↕</span></th>
                        <th class="sortable" data-sort="category">Category <span class="sort-arrow">↕</span></th>
                        <th class="sortable" data-sort="quality_score">Quality <span class="sort-arrow">↕</span></th>
                        <th>Status</th>
                        <th>Layers</th>
                        <th class="sortable" data-sort="views">Views <span class="sort-arrow">↕</span></th>
                    </tr>
                </thead>
                <tbody id="workflows-table">
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 40px; color: #666;">
                            Loading workflows...
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div class="pagination" id="pagination">
                <!-- Pagination buttons will be added here -->
            </div>
        </div>
    </div>
    
    <script>
        let currentPage = 1;
        let currentSearch = '';
        let currentSort = 'workflow_id';
        let currentOrder = 'desc';
        
        async function loadStats() {{
            try {{
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('total-workflows').textContent = stats.total_workflows.toLocaleString();
                document.getElementById('success-rate').textContent = stats.success_rate + '%';
                document.getElementById('avg-quality').textContent = stats.avg_quality_score.toFixed(1) + '%';
                document.getElementById('processing-time').textContent = stats.avg_processing_time.toFixed(1) + 's';
            }} catch (error) {{
                console.error('Error loading stats:', error);
            }}
        }}
        
        async function loadWorkflows(page = 1, search = '', sort = currentSort, order = currentOrder) {{
            try {{
                const url = `/api/workflows?page=${{page}}${{search ? '&search=' + encodeURIComponent(search) : ''}}&sort=${{sort}}&order=${{order}}&t=${{Date.now()}}`;
                const response = await fetch(url);
                const data = await response.json();
                
                const tbody = document.getElementById('workflows-table');
                const pagination = document.getElementById('pagination');
                
                if (data.workflows.length === 0) {{
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: #666;">No workflows found</td></tr>';
                    pagination.innerHTML = '';
                    return;
                }}
                
                tbody.innerHTML = data.workflows.map(workflow => {{
                    // Create layer success indicators
                    const layers = [
                        workflow.layer1_success ? 'L1' : '',
                        workflow.layer2_success ? 'L2' : '',
                        workflow.layer3_success ? 'L3' : '',
                        workflow.layer4_success ? 'L4' : '',
                        workflow.layer5_success ? 'L5' : '',
                        workflow.layer6_success ? 'L6' : '',
                        workflow.layer7_success ? 'L7' : ''
                    ].filter(l => l).join(' ');
                    
                    // Status class based on workflow.status
                    const statusClass = workflow.status === 'Success' ? 'status-success' : 
                                      workflow.status === 'Partial' ? 'status-partial' : 
                                      workflow.status === 'Failed' ? 'status-failed' : 'status-pending';
                    
                    return `
                        <tr>
                            <td>
                                <a href="/workflow/${{workflow.workflow_id}}" class="url-link" style="font-weight: bold;">
                                    ${{workflow.workflow_id}}
                                </a>
                            </td>
                            <td>
                                <div style="font-weight: 500; color: #333;">
                                    ${{workflow.title || 'Untitled'}}
                                </div>
                                ${{workflow.workflow_industry ? `<div style="font-size: 0.8em; color: #666;">${{workflow.workflow_industry}}</div>` : ''}}
                            </td>
                            <td>
                                <span class="category-badge">${{workflow.category || 'Uncategorized'}}</span>
                            </td>
                            <td>
                                <div style="margin-bottom: 5px;">${{workflow.quality_score.toFixed(1)}}%</div>
                                <div class="quality-bar">
                                    <div class="quality-fill" style="width: ${{workflow.quality_score}}%"></div>
                                </div>
                            </td>
                            <td>
                                <span class="status-badge ${{statusClass}}">${{workflow.status}}</span>
                            </td>
                            <td>
                                <div style="font-size: 0.8em; color: #666;">${{layers || 'None'}}</div>
                            </td>
                            <td>
                                <div style="text-align: right;">${{workflow.views || 0}}</div>
                            </td>
                        </tr>
                    `;
                }}).join('');
                
                // Update pagination
                if (data.total_pages > 1) {{
                    let paginationHTML = '';
                    
                    if (page > 1) {{
                        paginationHTML += `<button class="page-btn" onclick="loadWorkflows(${{page-1}}, '${{search}}')">← Previous</button>`;
                    }}
                    
                    for (let i = Math.max(1, page - 2); i <= Math.min(data.total_pages, page + 2); i++) {{
                        const activeClass = i === page ? 'active' : '';
                        paginationHTML += `<button class="page-btn ${{activeClass}}" onclick="loadWorkflows(${{i}}, '${{search}}')">${{i}}</button>`;
                    }}
                    
                    if (page < data.total_pages) {{
                        paginationHTML += `<button class="page-btn" onclick="loadWorkflows(${{page+1}}, '${{search}}')">Next →</button>`;
                    }}
                    
                    pagination.innerHTML = paginationHTML;
                }} else {{
                    pagination.innerHTML = '';
                }}
                
            }} catch (error) {{
                console.error('Error loading workflows:', error);
                document.getElementById('workflows-table').innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #666;">Error loading workflows</td></tr>';
            }}
        }}
        
        function searchWorkflows() {{
            const search = document.getElementById('search-input').value;
            currentSearch = search;
            currentPage = 1;
            loadWorkflows(1, search);
        }}
        
        function clearSearch() {{
            document.getElementById('search-input').value = '';
            currentSearch = '';
            currentPage = 1;
            loadWorkflows(1);
        }}
        
        function sortBy(column) {{
            if (currentSort === column) {{
                // Toggle order if same column
                currentOrder = currentOrder === 'desc' ? 'asc' : 'desc';
            }} else {{
                // New column, default to descending
                currentSort = column;
                currentOrder = 'desc';
            }}
            
            // Update visual indicators
            document.querySelectorAll('th.sortable').forEach(th => {{
                th.classList.remove('sort-active');
                const arrow = th.querySelector('.sort-arrow');
                if (arrow) arrow.textContent = '↕';
            }});
            
            const activeTh = document.querySelector(`th[data-sort="${{column}}"]`);
            if (activeTh) {{
                activeTh.classList.add('sort-active');
                const arrow = activeTh.querySelector('.sort-arrow');
                if (arrow) arrow.textContent = currentOrder === 'desc' ? '↓' : '↑';
            }}
            
            // Reload with new sort
            currentPage = 1;
            loadWorkflows(1, currentSearch, currentSort, currentOrder);
        }}
        
        // Initial load
        loadStats();
        loadWorkflows();
        
        // Add sorting event listeners
        document.querySelectorAll('th.sortable').forEach(th => {{
            th.addEventListener('click', function() {{
                const column = this.getAttribute('data-sort');
                sortBy(column);
            }});
        }});
        
        // Handle Enter key in search
        document.getElementById('search-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                searchWorkflows();
            }}
        }});
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_workflow_details(self, workflow_id):
        """Serve detailed workflow information page"""
        details = get_workflow_details(workflow_id)
        
        if not details:
            self.send_error(404, "Workflow not found")
            return
        
        workflow = details['workflow']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 {workflow['workflow_id']} - Workflow Details</title>
    <link rel="icon" href="/favicon-detail.ico">
    <link rel="shortcut icon" href="/favicon-detail.ico">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .back-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        .back-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .section {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #495057;
        }}
        
        .info-value {{
            color: #333;
            text-align: right;
        }}
        
        .status-badges {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .status-badge {{
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .status-failure {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .quality-display {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .quality-score {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .quality-bar {{
            flex: 1;
            background: #e9ecef;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .quality-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 10px;
        }}
        
        .json-data {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }}
        
        .json-data pre {{
            margin: 0;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }}
        
        .url-link:hover {{
            text-decoration: underline;
        }}
        
        .error-message {{
            background: #fee2e2;
            color: #991b1b;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #dc2626;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }}
        
        .no-data {{
            text-align: center;
            color: #6c757d;
            font-style: italic;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-btn">← Back to Database Viewer</a>
        
        <div class="header">
            <h1>🔍 {workflow['workflow_id']}</h1>
            <p>Complete workflow information and analysis</p>
        </div>
        
        <div class="section">
            <h2>📊 Basic Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Workflow ID:</span>
                    <span class="info-value">{workflow['workflow_id']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Database ID:</span>
                    <span class="info-value">{workflow['id']}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Processing Time:</span>
                    <span class="info-value">{workflow['processing_time']:.2f} seconds</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Retry Count:</span>
                    <span class="info-value">{workflow['retry_count'] or 0}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Extracted At:</span>
                    <span class="info-value">{workflow['extracted_at'] or 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Last Updated:</span>
                    <span class="info-value">{workflow['updated_at'] or 'N/A'}</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔗 Source Information</h2>
            <div class="info-item">
                <span class="info-label">Workflow URL:</span>
                <span class="info-value">
                    <a href="{workflow['url']}" target="_blank" class="url-link">
                        {workflow['url']}
                    </a>
                </span>
            </div>
        </div>
        
        <div class="section">
            <h2>⭐ Quality Analysis</h2>
            <div class="quality-display">
                <div class="quality-score">{workflow['quality_score']:.1f}%</div>
                <div class="quality-bar">
                    <div class="quality-fill" style="width: {workflow['quality_score']}%"></div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>✅ Processing Status</h2>
            <div class="status-badges">
                <div class="status-badge {'status-success' if workflow['layer1_success'] else 'status-failure'}">
                    Layer 1: {'✅ Success' if workflow['layer1_success'] else '❌ Failed'}
                </div>
                <div class="status-badge {'status-success' if workflow['layer2_success'] else 'status-failure'}">
                    Layer 2: {'✅ Success' if workflow['layer2_success'] else '❌ Failed'}
                </div>
                <div class="status-badge {'status-success' if workflow['layer3_success'] else 'status-failure'}">
                    Layer 3: {'✅ Success' if workflow['layer3_success'] else '❌ Failed'}
                </div>
            </div>
            {'<div class="status-badges"><div class="status-badge status-success">🎉 Fully Successful</div></div>' if workflow['layer1_success'] and workflow['layer2_success'] and workflow['layer3_success'] else ''}
        </div>
        """
        
        # Add error message if present
        if workflow['error_message']:
            html += f"""
        <div class="section">
            <h2>❌ Error Information</h2>
            <div class="error-message">
                {workflow['error_message']}
            </div>
        </div>
            """
        
        # Add metadata section if available
        if details['metadata']:
            html += f"""
        <div class="section">
            <h2>📋 Metadata</h2>
            <div class="json-data">
                <pre>{json.dumps(details['metadata'], indent=2)}</pre>
            </div>
        </div>
            """
        
        # Add structure section if available
        if details['structure']:
            html += f"""
        <div class="section">
            <h2>🏗️ Workflow Structure</h2>
            <div class="json-data">
                <pre>{json.dumps(details['structure'], indent=2)}</pre>
            </div>
        </div>
            """
        
        # Add content section if available
        if details['content']:
            html += f"""
        <div class="section">
            <h2>📝 Content Information</h2>
            <div class="json-data">
                <pre>{json.dumps(details['content'], indent=2)}</pre>
            </div>
        </div>
            """
        
        # Add transcript section if available
        if details['transcript']:
            html += f"""
        <div class="section">
            <h2>🎥 Video Transcript</h2>
            <div class="json-data">
                <pre>{json.dumps(details['transcript'], indent=2)}</pre>
            </div>
        </div>
            """
        
        html += """
    </div>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_favicon(self, emoji, bg_color):
        """Serve a favicon with the specified emoji and background color"""
        # Create a simple SVG favicon
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
            <rect width="32" height="32" fill="{bg_color}" rx="4"/>
            <text y="24" font-size="20" text-anchor="middle" x="16" fill="white">{emoji}</text>
        </svg>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'image/svg+xml')
        self.send_header('Cache-Control', 'public, max-age=3600')  # Cache for 1 hour
        self.end_headers()
        self.wfile.write(svg_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    # Try different ports to find one that's available
    ports_to_try = [5004, 5005, 5006, 5007, 5008]
    
    for port in ports_to_try:
        try:
            server = HTTPServer(('0.0.0.0', port), DBViewerHandler)
            print("=" * 60)
            print("🗄️ N8N Scraper Database Viewer")
            print("=" * 60)
            print(f"\n✅ Server running at: http://localhost:{port}")
            print(f"✅ Database: {DB_CONFIG['database']}")
            print("\n📊 Features:")
            print("   • Interactive workflow table")
            print("   • Search and pagination")
            print("   • Quality score visualization")
            print("   • Real-time statistics")
            print("\n💡 Press Ctrl+C to stop the server")
            print("=" * 60)
            print()
            
            server.serve_forever()
            break
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"Port {port} is busy, trying next port...")
                continue
            else:
                raise
    
    print("No available ports found!")

if __name__ == '__main__':
    main()
