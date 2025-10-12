#!/usr/bin/env python3
"""
Simple HTML Database Viewer
Creates a live web page to view database contents
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

# Database connection
DB_CONFIG = {
    'host': 'n8n-scraper-database',
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
        'workflow_id': 'CAST(workflow_id AS INTEGER)',
        'url': 'url',
        'quality_score': 'quality_score',
        'processing_time': 'processing_time',
        'created_at': 'created_at',
        'extracted_at': 'extracted_at',
        'last_scraped_at': 'last_scraped_at',
        'scraping_status': 'CASE WHEN layer1_success AND layer2_success AND layer3_success THEN 4 WHEN layer1_success OR layer2_success OR layer3_success THEN 3 WHEN last_scraped_at IS NOT NULL THEN 2 ELSE 1 END'
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
                created_at,
                extracted_at,
                last_scraped_at,
                error_message,
                retry_count,
                CASE 
                    WHEN layer1_success AND layer2_success AND layer3_success THEN 'fully_scraped'
                    WHEN layer1_success OR layer2_success OR layer3_success THEN 'partially_scraped'
                    WHEN last_scraped_at IS NOT NULL THEN 'attempted'
                    ELSE 'not_scraped'
                END as scraping_status
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
            COUNT(*) FILTER (WHERE layer1_success AND layer2_success AND layer3_success) as fully_successful,
            COUNT(*) FILTER (WHERE (layer1_success OR layer2_success OR layer3_success) AND NOT (layer1_success AND layer2_success AND layer3_success)) as partial_success,
            COUNT(*) FILTER (WHERE last_scraped_at IS NOT NULL AND NOT (layer1_success OR layer2_success OR layer3_success)) as attempted,
            COUNT(*) FILTER (WHERE last_scraped_at IS NULL AND NOT (layer1_success OR layer2_success OR layer3_success)) as not_scraped,
            COUNT(*) FILTER (WHERE error_message IS NOT NULL) as with_errors,
            CAST(AVG(quality_score) AS DECIMAL(5,2)) as avg_quality,
            CAST(AVG(processing_time) AS DECIMAL(5,2)) as avg_processing_time,
            MIN(created_at) as first_created,
            MAX(last_scraped_at) as last_scraped
        FROM workflows
    """
    
    cursor.execute(query)
    stats = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return stats

def generate_html(workflows, stats, total, page=1, limit=50, search=None, sort_by='extracted_at', sort_order='desc'):
    """Generate HTML page"""
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    
    # Helper function to generate sort links
    def sort_link(column, display_name):
        current_order = 'asc' if sort_by == column and sort_order.lower() == 'desc' else 'desc'
        search_param = f"&search={urllib.parse.quote(search)}" if search else ""
        page_param = f"&page=1" if sort_by != column else f"&page={page}"
        
        active_class = "sort-active" if sort_by == column else ""
        arrow = "↑" if sort_by == column and sort_order.lower() == 'asc' else "↓" if sort_by == column and sort_order.lower() == 'desc' else ""
        
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
    <title>N8N Scraper Database Viewer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card .label {{
            color: #6c757d;
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
            padding: 20px 30px;
            background: white;
            display: flex;
            gap: 15px;
            align-items: center;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .search-box {{
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
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
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .btn:active {{
            transform: translateY(0);
        }}
        
        .table-container {{
            padding: 30px;
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
        }}
        
        .sort-link {{
            color: #495057;
            text-decoration: none;
            display: block;
            padding: 5px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}
        
        .sort-link:hover {{
            background: #e9ecef;
            color: #007bff;
        }}
        
        .sort-link.sort-active {{
            background: #007bff;
            color: white;
            font-weight: bold;
        }}
        
        .sort-link.sort-active:hover {{
            background: #0056b3;
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
        
        .status-attempted {{
            background: #fef3c7;
            color: #d97706;
        }}
        
        .status-not-scraped {{
            background: #f3f4f6;
            color: #6b7280;
        }}
        
        .quality-bar {{
            background: #e9ecef;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
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
            align-items: center;
        }}
        
        .page-btn {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .page-btn:hover {{
            background: #667eea;
            color: white;
        }}
        
        .page-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .page-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .url-link {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .url-link:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .workflow-id-link {{
            color: #007bff;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        .workflow-id-link:hover {{
            color: #0056b3;
            text-decoration: underline;
        }}
        
        .refresh-info {{
            text-align: center;
            padding: 15px;
            background: #e7f3ff;
            color: #004085;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ N8N Scraper Database</h1>
            <p>Real-time workflow monitoring and data exploration</p>
        </div>
        
        <div class="refresh-info">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • 
            <a href="/" style="color: #004085; font-weight: bold;">Refresh Page</a>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">Total Workflows</div>
                <div class="value">{stats['total_workflows'] or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Fully Successful</div>
                <div class="value">{stats['fully_successful'] or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Partially Scraped</div>
                <div class="value">{stats['partial_success'] or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Attempted</div>
                <div class="value">{stats['attempted'] or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Not Scraped</div>
                <div class="value">{stats['not_scraped'] or 0:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Quality</div>
                <div class="value">{stats['avg_quality'] or 0}</div>
            </div>
            <div class="stat-card">
                <div class="label">Avg Time (s)</div>
                <div class="value">{stats['avg_processing_time'] or 0}</div>
            </div>
        </div>
        
        <div class="controls">
            <form method="GET" style="display: flex; gap: 15px; flex: 1;">
                <input type="text" name="search" class="search-box" 
                       placeholder="Search by workflow ID or URL..." 
                       value="{search if search else ''}"
                       onchange="this.form.submit()">
                <button type="submit" class="btn">Search</button>
                {f'<a href="/" class="btn" style="text-decoration: none;">Clear</a>' if search else ''}
            </form>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>{sort_link('workflow_id', 'Workflow ID')}</th>
                        <th>{sort_link('url', 'URL')}</th>
                        <th>{sort_link('quality_score', 'Quality Score')}</th>
                        <th>{sort_link('scraping_status', 'Scraping Status')}</th>
                        <th>{sort_link('processing_time', 'Processing Time')}</th>
                        <th>{sort_link('created_at', 'Created At')}</th>
                        <th>{sort_link('extracted_at', 'Extracted At')}</th>
                        <th>{sort_link('last_scraped_at', 'Last Scraped')}</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for workflow in workflows:
        # Determine scraping status
        scraping_status = workflow.get('scraping_status', 'not_scraped')
        
        if scraping_status == 'fully_scraped':
            status_class = 'status-success'
            status_text = '✅ Fully Scraped'
        elif scraping_status == 'partially_scraped':
            status_class = 'status-partial'
            status_text = '⚠️ Partially Scraped'
        elif scraping_status == 'attempted':
            status_class = 'status-attempted'
            status_text = '🔄 Attempted'
        else:  # not_scraped
            status_class = 'status-not-scraped'
            status_text = '⏳ Not Scraped'
        
        quality = float(workflow['quality_score'] or 0)
        
        html += f"""
                    <tr>
                        <td>
                            <a href="/workflow/{workflow['workflow_id']}" class="workflow-id-link">
                                <strong>{workflow['workflow_id'] or 'N/A'}</strong>
                            </a>
                        </td>
                        <td>
                            <a href="{workflow['url'] or '#'}" target="_blank" class="url-link">
                                {(workflow['url'] or 'N/A')[:60]}{'...' if len(workflow['url'] or '') > 60 else ''}
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
                        <td>{float(workflow['processing_time'] or 0):.2f}s</td>
                        <td>{workflow['created_at'].strftime('%Y-%m-%d %H:%M') if workflow['created_at'] else 'N/A'}</td>
                        <td>{workflow['extracted_at'].strftime('%Y-%m-%d %H:%M') if workflow['extracted_at'] else 'N/A'}</td>
                        <td>{workflow['last_scraped_at'].strftime('%Y-%m-%d %H:%M') if workflow['last_scraped_at'] else 'N/A'}</td>
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
        
        prev_style = 'style="pointer-events: none; opacity: 0.5;"' if page == 1 else ""
        html += f'<a href="/?page={page-1}{search_param}" class="page-btn" {prev_style}>← Previous</a>'
        
        # Page numbers (show max 7 pages around current)
        start_page = max(1, page - 3)
        end_page = min(total_pages, page + 3)
        
        if start_page > 1:
            html += f'<a href="/?page=1{search_param}" class="page-btn">1</a>'
            if start_page > 2:
                html += '<span>...</span>'
        
        for p in range(start_page, end_page + 1):
            active_class = 'active' if p == page else ''
            html += f'<a href="/?page={p}{search_param}" class="page-btn {active_class}">{p}</a>'
        
        if end_page < total_pages:
            if end_page < total_pages - 1:
                html += '<span>...</span>'
            html += f'<a href="/?page={total_pages}{search_param}" class="page-btn">{total_pages}</a>'
        
        # Next button
        next_style = 'style="pointer-events: none; opacity: 0.5;"' if page == total_pages else ""
        html += f'<a href="/?page={page+1}{search_param}" class="page-btn" {next_style}>Next →</a>'
    
    html += f"""
        </div>
        
        <div class="refresh-info" style="border-top: 1px solid #dee2e6;">
            Showing {(page-1)*limit + 1} to {min(page*limit, total)} of {total:,} workflows • 
            Page {page} of {total_pages}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
    """
    
    return html

class DatabaseViewerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        # Handle workflow detail page
        if self.path.startswith('/workflow/'):
            workflow_id = self.path.split('/workflow/')[-1]
            self.handle_workflow_detail(workflow_id)
            return
        
        # Get parameters
        page = int(params.get('page', [1])[0])
        search = params.get('search', [None])[0]
        sort_by = params.get('sort', ['extracted_at'])[0]
        sort_order = params.get('order', ['desc'])[0]
        limit = 50
        
        try:
            # Get data
            stats = get_statistics()
            workflows, total = get_workflows(
                limit=limit,
                offset=(page-1)*limit,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            # Generate HTML
            html = generate_html(workflows, stats, total, page, limit, search, sort_by, sort_order)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
            <html>
                <body>
                    <h1>Error</h1>
                    <p>{str(e)}</p>
                    <p>Make sure the database is running and accessible.</p>
                </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def handle_workflow_detail(self, workflow_id):
        """Handle workflow detail page"""
        try:
            # Get workflow details from database
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get basic workflow info
            cursor.execute("""
                SELECT * FROM workflows WHERE workflow_id = %s
            """, (workflow_id,))
            workflow = cursor.fetchone()
            
            if not workflow:
                # Workflow not found
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = f"""
                <html>
                    <head><title>Workflow Not Found</title></head>
                    <body>
                        <h1>Workflow Not Found</h1>
                        <p>Workflow ID {workflow_id} was not found in the database.</p>
                        <a href="/">← Back to Database Viewer</a>
                    </body>
                </html>
                """
                self.wfile.write(error_html.encode())
                return
            
            # Get related data from other tables if they exist
            # (This would be expanded based on your actual database schema)
            
            cursor.close()
            conn.close()
            
            # Generate HTML for workflow detail page
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Workflow {workflow_id} Details</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                    .content {{ padding: 30px; }}
                    .back-link {{ color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }}
                    .back-link:hover {{ text-decoration: underline; }}
                    .detail-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }}
                    .detail-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; border-left: 4px solid #007bff; }}
                    .detail-label {{ font-weight: bold; color: #495057; margin-bottom: 5px; }}
                    .detail-value {{ color: #212529; }}
                    .status-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
                    .status-success {{ background: #d4edda; color: #155724; }}
                    .status-partial {{ background: #fff3cd; color: #856404; }}
                    .status-attempted {{ background: #f8d7da; color: #721c24; }}
                    .status-not-scraped {{ background: #e2e3e5; color: #383d41; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Workflow {workflow_id}</h1>
                        <p>Complete workflow details and processing information</p>
                    </div>
                    <div class="content">
                        <a href="/" class="back-link">← Back to Database Viewer</a>
                        
                        <div class="detail-grid">
                            <div class="detail-card">
                                <div class="detail-label">Workflow ID</div>
                                <div class="detail-value">{workflow['workflow_id']}</div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">URL</div>
                                <div class="detail-value">
                                    <a href="{workflow['url']}" target="_blank">{workflow['url']}</a>
                                </div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Quality Score</div>
                                <div class="detail-value">{float(workflow['quality_score'] or 0):.1f}%</div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Processing Time</div>
                                <div class="detail-value">{float(workflow['processing_time'] or 0):.2f} seconds</div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Created At</div>
                                <div class="detail-value">{workflow['created_at'].strftime('%Y-%m-%d %H:%M:%S') if workflow['created_at'] else 'N/A'}</div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Last Scraped</div>
                                <div class="detail-value">{workflow['last_scraped_at'].strftime('%Y-%m-%d %H:%M:%S') if workflow['last_scraped_at'] else 'Never'}</div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Scraping Status</div>
                                <div class="detail-value">
                                    <span class="status-badge {'status-success' if workflow['layer1_success'] and workflow['layer2_success'] and workflow['layer3_success'] else 'status-partial' if workflow['layer1_success'] or workflow['layer2_success'] or workflow['layer3_success'] else 'status-attempted' if workflow['last_scraped_at'] else 'status-not-scraped'}">
                                        {'✅ Fully Scraped' if workflow['layer1_success'] and workflow['layer2_success'] and workflow['layer3_success'] else '⚠️ Partially Scraped' if workflow['layer1_success'] or workflow['layer2_success'] or workflow['layer3_success'] else '🔄 Attempted' if workflow['last_scraped_at'] else '⏳ Not Scraped'}
                                    </span>
                                </div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Layer Status</div>
                                <div class="detail-value">
                                    Layer 1: {'✅' if workflow['layer1_success'] else '❌'}<br>
                                    Layer 2: {'✅' if workflow['layer2_success'] else '❌'}<br>
                                    Layer 3: {'✅' if workflow['layer3_success'] else '❌'}
                                </div>
                            </div>
                            
                            <div class="detail-card">
                                <div class="detail-label">Retry Count</div>
                                <div class="detail-value">{workflow['retry_count'] or 0}</div>
                            </div>
                            
                            {f'<div class="detail-card"><div class="detail-label">Error Message</div><div class="detail-value">{workflow["error_message"]}</div></div>' if workflow['error_message'] else ''}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
            <html>
                <body>
                    <h1>Error</h1>
                    <p>Error loading workflow details: {str(e)}</p>
                    <a href="/">← Back to Database Viewer</a>
                </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    port = 5004
    server = HTTPServer(('0.0.0.0', port), DatabaseViewerHandler)
    
    print("=" * 60)
    print("🚀 N8N Scraper Database Viewer")
    print("=" * 60)
    print(f"\n✅ Server running at: http://localhost:{port}")
    print(f"✅ Database: {DB_CONFIG['database']}")
    print(f"✅ Auto-refresh: Every 30 seconds")
    print("\n📊 Features:")
    print("   • Real-time statistics dashboard")
    print("   • Searchable workflow data")
    print("   • Quality score visualization")
    print("   • Pagination for large datasets")
    print("   • Auto-refresh every 30 seconds")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        server.shutdown()
        print("✅ Server stopped")

if __name__ == '__main__':
    main()

