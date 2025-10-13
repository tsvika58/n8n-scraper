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

# Database connection - SUPABASE
DB_CONFIG = {
    'host': 'aws-1-eu-north-1.pooler.supabase.com',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres.skduopoakfeaurttcaip',
    'password': 'crg3pjm8ych4ctu@KXT'
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
        where_clause = "WHERE w.workflow_id ILIKE %s OR w.url ILIKE %s"
        search_pattern = f"%{search}%"
        params = [search_pattern, search_pattern]
    
    # Validate sort column to prevent SQL injection
    valid_sort_columns = {
        'workflow_id': 'w.workflow_id',
        'url': 'w.url',
        'quality_score': 'w.quality_score',
        'categories': 'wm.categories',
        'extracted_at': 'w.extracted_at',
        'status': 'CASE WHEN w.layer1_success AND w.layer2_success AND w.layer3_success THEN 3 WHEN w.layer1_success OR w.layer2_success OR w.layer3_success THEN 2 ELSE 1 END'
    }
    
    sort_column = valid_sort_columns.get(sort_by, 'w.extracted_at')
    sort_order = 'ASC' if sort_order.upper() == 'ASC' else 'DESC'
    
    query = f"""
        SELECT 
            w.workflow_id,
            w.url,
            w.quality_score,
            w.layer1_success,
            w.layer2_success,
            w.layer3_success,
            w.extracted_at,
            w.error_message,
            w.retry_count,
            wm.categories
        FROM workflows w
        LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
        {where_clause}
        ORDER BY {sort_column} {sort_order}
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    workflows = cursor.fetchall()
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM workflows w {where_clause}"
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
                CASE 
                    WHEN COUNT(*) = 0 THEN 0
                    ELSE (COUNT(*) FILTER (WHERE layer1_success = true OR layer2_success = true OR layer3_success = true) * 100.0 / COUNT(*))
                END AS DECIMAL(5,1)
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
        elif self.path.startswith('/workflow/'):
            self.handle_workflow_detail_page()
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
                        'categories': w['categories'] if w['categories'] else [],
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
    
    def handle_workflow_detail_page(self):
        """Handle workflow detail page request"""
        try:
            workflow_id = self.path.split('/')[-1]
            
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get workflow basic info
            cursor.execute("SELECT * FROM workflows WHERE workflow_id = %s", (workflow_id,))
            workflow = cursor.fetchone()
            
            if not workflow:
                self.send_error(404, "Workflow not found")
                cursor.close()
                conn.close()
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
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_workflow_detail_html(workflow, metadata, structure, content, transcript)
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Page Error: {str(e)}")
    
    def generate_workflow_detail_html(self, workflow, metadata, structure, content, transcript):
        """Generate workflow detail HTML page"""
        
        # Calculate status
        all_success = workflow['layer1_success'] and workflow['layer2_success'] and workflow['layer3_success']
        any_success = workflow['layer1_success'] or workflow['layer2_success'] or workflow['layer3_success']
        
        if all_success:
            status_badge = '<span class="badge badge-success">✅ Fully Scraped</span>'
        elif any_success:
            status_badge = '<span class="badge badge-warning">⚠️ Partially Scraped</span>'
        else:
            status_badge = '<span class="badge badge-error">❌ Not Scraped</span>'
        
        # Scraping layers status
        layers = []
        for i in range(1, 8):
            layer_key = f'layer{i}_success'
            if layer_key in workflow:
                status = '✅' if workflow[layer_key] else '❌'
                layers.append(f'<span class="layer-badge">Layer {i}: {status}</span>')
        
        layers_html = ' '.join(layers)
        
        # Metadata section
        metadata_html = ''
        if metadata:
            metadata_html = f'''
            <div class="detail-section">
                <h2>📋 Metadata</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Title:</span>
                        <span class="info-value">{metadata.get('title', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Author:</span>
                        <span class="info-value">{metadata.get('author_name', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Views:</span>
                        <span class="info-value">{(metadata.get('views') if metadata.get('views') is not None else 0):,}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Use Case:</span>
                        <span class="info-value">{metadata.get('use_case', 'N/A')}</span>
                    </div>
                    <div class="info-item full-width">
                        <span class="info-label">Description:</span>
                        <span class="info-value">{metadata.get('description', 'N/A')}</span>
                    </div>
                </div>
            </div>
            '''
        else:
            metadata_html = '<div class="detail-section"><h2>📋 Metadata</h2><p class="no-data">No metadata available yet</p></div>'
        
        # Structure section
        structure_html = ''
        if structure:
            structure_html = f'''
            <div class="detail-section">
                <h2>🏗️ Structure</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Nodes:</span>
                        <span class="info-value">{structure.get('node_count') if structure.get('node_count') is not None else 0}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Connections:</span>
                        <span class="info-value">{structure.get('connection_count') if structure.get('connection_count') is not None else 0}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Extraction Type:</span>
                        <span class="info-value">{structure.get('extraction_type', 'N/A')}</span>
                    </div>
                </div>
            </div>
            '''
        else:
            structure_html = '<div class="detail-section"><h2>🏗️ Structure</h2><p class="no-data">No structure data available yet</p></div>'
        
        # Content section
        content_html = ''
        if content:
            has_videos = content.get('has_videos', False)
            has_iframes = content.get('has_iframes', False)
            content_html = f'''
            <div class="detail-section">
                <h2>📄 Content</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Videos:</span>
                        <span class="info-value">{'✅ Yes' if has_videos else '❌ No'} ({content.get('video_count') if content.get('video_count') is not None else 0})</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Iframes:</span>
                        <span class="info-value">{'✅ Yes' if has_iframes else '❌ No'} ({content.get('iframe_count') if content.get('iframe_count') is not None else 0})</span>
                    </div>
                </div>
            </div>
            '''
        else:
            content_html = '<div class="detail-section"><h2>📄 Content</h2><p class="no-data">No content data available yet</p></div>'
        
        # Transcript section
        transcript_html = ''
        if transcript:
            transcript_text = transcript.get('transcript_text', '')
            preview = transcript_text[:500] + '...' if len(transcript_text) > 500 else transcript_text
            transcript_html = f'''
            <div class="detail-section">
                <h2>🎥 Video Transcript</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Duration:</span>
                        <span class="info-value">{transcript.get('duration') if transcript.get('duration') is not None else 0} seconds</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Language:</span>
                        <span class="info-value">{transcript.get('language', 'N/A')}</span>
                    </div>
                    <div class="info-item full-width">
                        <span class="info-label">Transcript Preview:</span>
                        <span class="info-value transcript-preview">{preview}</span>
                    </div>
                </div>
            </div>
            '''
        else:
            transcript_html = '<div class="detail-section"><h2>🎥 Video Transcript</h2><p class="no-data">No transcript available yet</p></div>'
        
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workflow {workflow['workflow_id']} - Detail View</title>
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
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .back-link {{
            display: inline-block;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }}
        
        .back-link:hover {{
            transform: translateY(-2px);
            background: white;
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
            font-size: 2em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .workflow-url {{
            color: #666;
            word-break: break-all;
            margin: 10px 0;
        }}
        
        .workflow-url a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .workflow-url a:hover {{
            text-decoration: underline;
        }}
        
        .status-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .layer-badge {{
            display: inline-block;
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            font-size: 0.85em;
            color: #666;
        }}
        
        .detail-section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .detail-section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .info-item {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .info-item.full-width {{
            grid-column: 1 / -1;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .info-value {{
            color: #333;
            font-size: 1.1em;
        }}
        
        .transcript-preview {{
            white-space: pre-wrap;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            line-height: 1.6;
        }}
        
        .no-data {{
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .stat-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-label {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        @media (max-width: 768px) {{
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.5em;
            }}
            
            .status-row {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Workflow List</a>
        
        <div class="header">
            <h1>🗄️ Workflow {workflow['workflow_id']}</h1>
            <div class="workflow-url">
                <strong>URL:</strong> <a href="{workflow['url']}" target="_blank">{workflow['url']}</a>
            </div>
            <div class="status-row">
                {status_badge}
                {layers_html}
            </div>
            
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-label">Quality Score</div>
                    <div class="stat-value">{(workflow['quality_score'] if workflow['quality_score'] is not None else 0):.1f}%</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Processing Time</div>
                    <div class="stat-value">{(workflow['processing_time'] if workflow['processing_time'] is not None else 0):.2f}s</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Extracted</div>
                    <div class="stat-value">{workflow['extracted_at'].strftime('%Y-%m-%d') if workflow['extracted_at'] else 'N/A'}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Retry Count</div>
                    <div class="stat-value">{workflow['retry_count']}</div>
                </div>
            </div>
        </div>
        
        {metadata_html}
        {structure_html}
        {content_html}
        {transcript_html}
    </div>
</body>
</html>
        '''
        
        return html
    
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
        
        .category-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: 500;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-right: 5px;
            white-space: nowrap;
        }}
        
        .category-more {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 0.75em;
            background: #e9ecef;
            color: #666;
            font-weight: 600;
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
                <div class="stat-number">{(stats['success_rate'] if stats['success_rate'] is not None else 0):.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{(stats['avg_quality_score'] if stats['avg_quality_score'] is not None else 0):.1f}%</div>
                <div class="stat-label">Avg Quality</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{(stats['avg_processing_time'] if stats['avg_processing_time'] is not None else 0):.1f}s</div>
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
                        <th>{sort_link('categories', 'Categories')}</th>
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
            
            # Format categories
            categories = workflow.get('categories', [])
            if categories and isinstance(categories, list):
                # Take first 2 categories and create badges
                category_badges = ' '.join([f'<span class="category-badge">{cat}</span>' for cat in categories[:2]])
                if len(categories) > 2:
                    category_badges += f' <span class="category-more">+{len(categories)-2}</span>'
                categories_html = category_badges
            else:
                categories_html = '<span style="color: #999;">Uncategorized</span>'
            
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
                        <td>{categories_html}</td>
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
