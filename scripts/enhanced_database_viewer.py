#!/usr/bin/env python3
"""
Enhanced Sortable Database Viewer
Creates a live web page to view database contents with full sorting functionality
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n_scraper',
    'user': 'scraper_user',
    'password': 'scraper_pass'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_workflows(limit=50, offset=0, search=None, sort_by='extracted_at', sort_order='DESC'):
    """Get workflows with optional search and sorting"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE workflow_id ILIKE %s OR url ILIKE %s"
        search_pattern = f"%{search}%"
        params = [search_pattern, search_pattern]
    
    # Validate sort column to prevent SQL injection
    valid_sort_columns = {
        'workflow_id': 'workflow_id',
        'url': 'url',
        'quality_score': 'quality_score',
        'processing_time': 'processing_time',
        'extracted_at': 'extracted_at',
        'status': 'CASE WHEN layer1_success AND layer2_success AND layer3_success THEN 3 WHEN layer1_success OR layer2_success OR layer3_success THEN 2 ELSE 1 END'
    }
    
    sort_column = valid_sort_columns.get(sort_by, 'extracted_at')
    sort_order = 'ASC' if sort_order.upper() == 'ASC' else 'DESC'
    
    query = f"""
        SELECT 
            workflow_id,
            url,
            quality_score,
            layer1_success,
            layer2_success,
            layer3_success,
            processing_time,
            extracted_at,
            error_message,
            retry_count
        FROM workflows
        {where_clause}
        ORDER BY {sort_column} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    workflows = cursor.fetchall()
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM workflows {where_clause}"
    cursor.execute(count_query, params[:len(params)-2] if where_clause else [])
    total = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return workflows, total

def get_statistics():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            COUNT(*) as total_workflows,
            COUNT(*) FILTER (WHERE layer1_success = true AND layer2_success = true AND layer3_success = true) as fully_successful,
            COUNT(*) FILTER (WHERE layer1_success = true OR layer2_success = true OR layer3_success = true) as partial_success,
            COUNT(*) FILTER (WHERE error_message IS NOT NULL) as with_errors,
            CAST(AVG(quality_score) AS DECIMAL(5,1)) as avg_quality_score,
            CAST(AVG(processing_time) AS DECIMAL(5,1)) as avg_processing_time,
            CAST(
                (COUNT(*) FILTER (WHERE layer1_success = true OR layer2_success = true OR layer3_success = true) * 100.0 / COUNT(*)) AS DECIMAL(5,1)
            ) as success_rate,
            MAX(extracted_at) as latest_workflow,
            NOW() as last_update
        FROM workflows
    """
    
    cursor.execute(query)
    stats = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return stats

class DatabaseViewerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path.startswith('/api/workflows'):
            self.handle_api_workflows()
        elif self.path.startswith('/api/stats'):
            self.handle_api_stats()
        elif self.path.startswith('/api/workflow/'):
            self.handle_api_workflow_detail()
        else:
            self.handle_main_page()
    
    def handle_api_workflows(self):
        """API endpoint for workflows"""
        try:
            # Parse query parameters
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            page = int(query_params.get('page', [1])[0])
            search = query_params.get('search', [None])[0]
            sort_by = query_params.get('sort', ['extracted_at'])[0]
            order = query_params.get('order', ['desc'])[0]
            
            limit = 50
            offset = (page - 1) * limit
            
            workflows, total = get_workflows(limit, offset, search, sort_by, order)
            
            response = {
                'workflows': [
                    {
                        'workflow_id': w['workflow_id'],
                        'url': w['url'],
                        'quality_score': float(w['quality_score']) if w['quality_score'] else 0,
                        'layer1_success': bool(w['layer1_success']),
                        'layer2_success': bool(w['layer2_success']),
                        'layer3_success': bool(w['layer3_success']),
                        'processing_time': float(w['processing_time']) if w['processing_time'] else 0,
                        'extracted_at': w['extracted_at'].isoformat() if w['extracted_at'] else None,
                        'error_message': w['error_message']
                    }
                    for w in workflows
                ],
                'total': total,
                'page': page,
                'total_pages': (total + limit - 1) // limit
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"API Error: {str(e)}")
    
    def handle_api_stats(self):
        """API endpoint for statistics"""
        try:
            stats = get_statistics()
            
            response = {
                'total_workflows': stats['total_workflows'],
                'fully_successful': stats['fully_successful'],
                'partial_success': stats['partial_success'],
                'with_errors': stats['with_errors'],
                'avg_quality_score': float(stats['avg_quality_score']) if stats['avg_quality_score'] else 0,
                'avg_processing_time': float(stats['avg_processing_time']) if stats['avg_processing_time'] else 0,
                'success_rate': float(stats['success_rate']) if stats['success_rate'] else 0,
                'latest_workflow': stats['latest_workflow'].isoformat() if stats['latest_workflow'] else None,
                'last_update': stats['last_update'].isoformat() if stats['last_update'] else None
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"API Error: {str(e)}")
    
    def handle_api_workflow_detail(self):
        """API endpoint for workflow detail"""
        try:
            workflow_id = self.path.split('/')[-1]
            
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get workflow basic info
            cursor.execute("SELECT * FROM workflows WHERE workflow_id = %s", (workflow_id,))
            workflow = cursor.fetchone()
            
            if not workflow:
                self.send_error(404, "Workflow not found")
                return
            
            # Get metadata
            cursor.execute("SELECT * FROM workflow_metadata WHERE workflow_id = %s", (workflow_id,))
            metadata = cursor.fetchone()
            
            # Get structure
            cursor.execute("SELECT * FROM workflow_structure WHERE workflow_id = %s", (workflow_id,))
            structure = cursor.fetchone()
            
            # Get content
            cursor.execute("SELECT * FROM workflow_content WHERE workflow_id = %s", (workflow_id,))
            content = cursor.fetchone()
            
            # Get transcript
            cursor.execute("SELECT * FROM video_transcripts WHERE workflow_id = %s", (workflow_id,))
            transcript = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            response = {
                'workflow': dict(workflow),
                'metadata': dict(metadata) if metadata else None,
                'structure': dict(structure) if structure else None,
                'content': dict(content) if content else None,
                'transcript': dict(transcript) if transcript else None
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            self.send_error(500, f"API Error: {str(e)}")
    
    def handle_main_page(self):
        """Handle main page request"""
        try:
            # Parse query parameters
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            page = int(query_params.get('page', [1])[0])
            search = query_params.get('search', [None])[0]
            sort_by = query_params.get('sort', ['extracted_at'])[0]
            order = query_params.get('order', ['desc'])[0]
            
            limit = 50
            offset = (page - 1) * limit
            
            workflows, total = get_workflows(limit, offset, search, sort_by, order)
            stats = get_statistics()
            
            total_pages = (total + limit - 1) // limit
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_html(workflows, total, page, total_pages, search, sort_by, order, stats)
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Page Error: {str(e)}")
    
    def generate_html(self, workflows, total, page, total_pages, search, sort_by, order, stats):
        """Generate HTML page with sorting functionality"""
        
        # Generate sort links
        def sort_link(column, display_name):
            current_order = 'asc' if sort_by == column and order.lower() == 'desc' else 'desc'
            search_param = f"&search={urllib.parse.quote(search)}" if search else ""
            page_param = f"&page=1" if sort_by != column else f"&page={page}"
            
            active_class = "sort-active" if sort_by == column else ""
            arrow = "↑" if sort_by == column and order.lower() == 'asc' else "↓" if sort_by == column else ""
            
            return f'''
                <a href="/?sort={column}&order={current_order}{search_param}{page_param}" class="sort-link {active_class}">
                    {display_name} {arrow}
                </a>
            '''
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N8N Scraper Database - Enhanced Sortable View</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🗄️</text></svg>">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .search-container {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .search-box {{
            width: 100%;
            padding: 15px 20px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
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
            transition: transform 0.2s, box-shadow 0.2s;
            margin-left: 10px;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .table-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }}
        
        thead {{
            background: #f8f9fa;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            position: sticky;
            top: 0;
            background: #f8f9fa;
        }}
        
        .sort-link {{
            color: #495057;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: color 0.3s;
        }}
        
        .sort-link:hover {{
            color: #667eea;
        }}
        
        .sort-active {{
            color: #667eea !important;
            font-weight: 700;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .workflow-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }}
        
        .workflow-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        .url-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-partial {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .status-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .quality-bar {{
            background: #e9ecef;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
            margin-top: 5px;
        }}
        
        .quality-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
        }}
        
        .pagination {{
            padding: 30px;
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .page-btn {{
            padding: 10px 15px;
            background: rgba(255, 255, 255, 0.9);
            color: #667eea;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s;
            border: 2px solid transparent;
        }}
        
        .page-btn:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }}
        
        .page-btn.active {{
            background: #667eea;
            color: white;
            border-color: #764ba2;
        }}
        
        .refresh-info {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .table-container {{
                padding: 15px;
            }}
            
            table {{
                font-size: 0.8em;
            }}
            
            th, td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ N8N Scraper Database</h1>
            <p>Enhanced sortable workflow data viewer</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_workflows']:,}</div>
                <div class="stat-label">Total Workflows</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['success_rate'] or 0:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_quality_score'] or 0:.1f}%</div>
                <div class="stat-label">Avg Quality</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['avg_processing_time'] or 0:.1f}s</div>
                <div class="stat-label">Processing Time</div>
            </div>
        </div>
        
        <div class="search-container">
            <form method="GET" style="display: flex; align-items: center;">
                <input type="text" name="search" placeholder="Search by workflow ID or URL..." 
                       value="{search or ''}" class="search-box">
                <input type="hidden" name="sort" value="{sort_by}">
                <input type="hidden" name="order" value="{order}">
                <button type="submit" class="btn">Search</button>
                <a href="/" class="btn" style="background: #6c757d;">Clear</a>
            </form>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>{sort_link('workflow_id', 'Workflow ID')}</th>
                        <th>{sort_link('url', 'URL')}</th>
                        <th>{sort_link('quality_score', 'Quality Score')}</th>
                        <th>{sort_link('status', 'Status')}</th>
                        <th>{sort_link('processing_time', 'Processing Time')}</th>
                        <th>{sort_link('extracted_at', 'Extracted At')}</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for workflow in workflows:
            # Determine status
            if workflow['layer1_success'] and workflow['layer2_success'] and workflow['layer3_success']:
                status_class = 'status-success'
                status_text = '✅ Complete'
            elif workflow['error_message']:
                status_class = 'status-error'
                status_text = '❌ Error'
            else:
                status_class = 'status-partial'
                status_text = '⚠️ Partial'
            
            quality = workflow['quality_score'] or 0
            
            html += f"""
                    <tr>
                        <td>
                            <a href="/workflow/{workflow['workflow_id']}" class="workflow-link">
                                {workflow['workflow_id']}
                            </a>
                        </td>
                        <td>
                            <a href="{workflow['url']}" target="_blank" class="url-link">
                                {workflow['url'][:60]}{'...' if len(workflow['url']) > 60 else ''}
                            </a>
                        </td>
                        <td>
                            <div style="min-width: 100px;">
                                <div style="margin-bottom: 5px;">{quality:.1f}%</div>
                                <div class="quality-bar">
                                    <div class="quality-fill" style="width: {quality}%"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge {status_class}">{status_text}</span>
                        </td>
                        <td>{workflow['processing_time']:.2f}s</td>
                        <td>{workflow['extracted_at'].strftime('%Y-%m-%d %H:%M') if workflow['extracted_at'] else 'N/A'}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="pagination">
        """
        
        # Pagination controls
        if total_pages > 1:
            # Previous button
            prev_disabled = 'disabled' if page == 1 else ''
            search_param = f"&search={urllib.parse.quote(search)}" if search else ""
            sort_param = f"&sort={sort_by}&order={order}"
            
            prev_style = 'style="pointer-events: none; opacity: 0.5;"' if page == 1 else ""
            html += f'<a href="/?page={page-1}{search_param}{sort_param}" class="page-btn" {prev_style}>← Previous</a>'
            
            # Page numbers (show max 7 pages around current)
            start_page = max(1, page - 3)
            end_page = min(total_pages, page + 3)
            
            if start_page > 1:
                html += f'<a href="/?page=1{search_param}{sort_param}" class="page-btn">1</a>'
                if start_page > 2:
                    html += '<span style="padding: 10px;">...</span>'
            
            for p in range(start_page, end_page + 1):
                active_class = 'active' if p == page else ''
                html += f'<a href="/?page={p}{search_param}{sort_param}" class="page-btn {active_class}">{p}</a>'
            
            if end_page < total_pages:
                if end_page < total_pages - 1:
                    html += '<span style="padding: 10px;">...</span>'
                html += f'<a href="/?page={total_pages}{search_param}{sort_param}" class="page-btn">{total_pages}</a>'
            
            # Next button
            next_style = 'style="pointer-events: none; opacity: 0.5;"' if page == total_pages else ""
            html += f'<a href="/?page={page+1}{search_param}{sort_param}" class="page-btn" {next_style}>Next →</a>'
        
        html += f"""
        </div>
        
        <div class="refresh-info">
            Showing {(page-1)*50 + 1} to {min(page*50, total)} of {total:,} workflows • 
            Page {page} of {total_pages} • 
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {{
            location.reload();
        }}, 30000);
        
        // Add loading states to sort links
        document.querySelectorAll('.sort-link').forEach(link => {{
            link.addEventListener('click', function() {{
                this.style.opacity = '0.7';
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html

def run_server(port=5004):
    """Run the database viewer server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DatabaseViewerHandler)
    
    print(f"🚀 Enhanced Database Viewer starting...")
    print(f"📊 Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🔧 Features: Sortable columns, Search, Pagination, Auto-refresh")
    print(f"⏰ Auto-refresh: Every 30 seconds")
    print()
    print(f"✅ Server running at: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
