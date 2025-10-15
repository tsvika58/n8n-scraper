#!/usr/bin/env python3
"""
Enhanced Sortable Database Viewer with Dynamic Search
Fixed SQL issues and added real-time search functionality
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import time

# Database connection - SUPABASE
# Project: n8n-workflow-scraper (skduopoakfeaurttcaip)
# Region: eu-north-1
# CRITICAL: connect_timeout is REQUIRED to avoid connection failures!
DB_CONFIG = {
    'host': 'aws-1-eu-north-1.pooler.supabase.com',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres.skduopoakfeaurttcaip',
    'password': 'crg3pjm8ych4ctu@KXT',
    'connect_timeout': 10  # REQUIRED for reliable connections!
}

def get_db_connection():
    """Get database connection with timeout"""
    return psycopg2.connect(**DB_CONFIG)

def get_workflows(limit=50, offset=0, search=None, sort_by='extracted_at', sort_order='DESC', category_filter=None, status_filter=None):
    """Get workflows with optional search, sorting, and filtering"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("(w.workflow_id ILIKE %s OR w.url ILIKE %s OR COALESCE(wm.title, '') ILIKE %s)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    if category_filter:
        where_conditions.append("wm.categories::text ILIKE %s")
        params.append(f"%{category_filter}%")
    
    if status_filter:
        if status_filter == 'fully_successful':
            where_conditions.append("(w.layer1_success = true AND w.layer2_success = true AND w.layer3_success = true)")
        elif status_filter == 'partial_success':
            where_conditions.append("(w.layer1_success = true OR w.layer2_success = true OR w.layer3_success = true) AND NOT (w.layer1_success = true AND w.layer2_success = true AND w.layer3_success = true)")
        elif status_filter == 'failed':
            where_conditions.append("w.error_message IS NOT NULL AND w.error_message NOT LIKE '%404%' AND w.error_message NOT LIKE '%no iframe%' AND w.error_message NOT LIKE '%no content%'")
        elif status_filter == 'invalid':
            where_conditions.append("(w.error_message IS NOT NULL AND (w.error_message LIKE '%404%' OR w.error_message LIKE '%no iframe%' OR w.error_message LIKE '%no content%' OR w.error_message LIKE '%empty%' OR w.quality_score = 0))")
        elif status_filter == 'pending':
            where_conditions.append("(w.extracted_at IS NULL OR (w.layer1_success = false AND w.layer2_success = false AND w.layer3_success = false AND w.error_message IS NULL))")
    
    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    
    # Validate sort column to prevent SQL injection
    valid_sort_columns = {
        'workflow_id': 'CAST(w.workflow_id AS INTEGER)',
        'title': 'COALESCE(wm.title, w.url)',
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
            wm.categories,
            wm.title
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
    count_query = f"""
        SELECT COUNT(*) 
        FROM workflows w
        LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
        {where_clause}
    """
    cursor.execute(count_query, params[:len(params)-2] if where_clause else [])
    total = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return workflows, total

def get_categories():
    """Get all available categories for filtering"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT DISTINCT categories::text as categories 
        FROM workflow_metadata 
        WHERE categories IS NOT NULL 
        AND categories::text != '' 
        AND categories::text != '[]'
        AND categories::text != 'null'
        ORDER BY categories::text
    """
    
    cursor.execute(query)
    raw_categories = [row['categories'] for row in cursor.fetchall()]
    
    # Handle both string and JSON array formats
    categories = []
    for cat in raw_categories:
        if isinstance(cat, str):
            try:
                import json
                parsed = json.loads(cat)
                if isinstance(parsed, list):
                    categories.extend(parsed)
                else:
                    categories.append(cat)
            except:
                categories.append(cat)
        else:
            categories.append(cat)
    
    # Remove duplicates and sort
    categories = sorted(list(set(categories)))
    
    cursor.close()
    conn.close()
    
    return categories

def get_statistics():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            COUNT(w.*) as total_workflows,
            COUNT(*) FILTER (WHERE wm.description IS NOT NULL AND wm.description != '') as layer1_complete,
            COUNT(*) FILTER (WHERE ws.workflow_json IS NOT NULL) as layer2_complete,
            COUNT(*) FILTER (WHERE w.layer3_success = true) as layer3_complete,
            COUNT(*) FILTER (WHERE w.error_message IS NOT NULL) as with_errors,
            CAST(AVG(w.quality_score) AS DECIMAL(5,1)) as avg_quality_score,
            CAST(AVG(w.processing_time) AS DECIMAL(5,1)) as avg_processing_time,
            CAST(
                CASE 
                    WHEN COUNT(w.*) = 0 THEN 0
                    ELSE (COUNT(*) FILTER (WHERE wm.description IS NOT NULL AND wm.description != '') * 100.0 / COUNT(w.*))
                END AS DECIMAL(5,1)
            ) as success_rate,
            MAX(w.extracted_at) as latest_workflow,
            NOW() as last_update
        FROM workflows w
        LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
        LEFT JOIN workflow_structure ws ON w.workflow_id = ws.workflow_id
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
            category_filter = query_params.get('category', [None])[0]
            status_filter = query_params.get('status', [None])[0]
            
            limit = 500  # Load more workflows for better client-side filtering
            offset = (page - 1) * limit
            
            workflows, total = get_workflows(limit, offset, search, sort_by, order, category_filter, status_filter)
            
            response = {
                'workflows': [
                    {
                        'workflow_id': w['workflow_id'],
                        'url': w['url'],
                        'title': w.get('title', 'Untitled Workflow'),
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
            
            # OPTIMIZED: Single query with all JOINs instead of 9 separate queries
            cursor.execute("""
                SELECT 
                    w.*,
                    json_build_object(
                        'title', wm.title,
                        'description', wm.description,
                        'use_case', wm.use_case,
                        'author_name', wm.author_name,
                        'author_url', wm.author_url,
                        'views', wm.views,
                        'shares', wm.shares,
                        'categories', wm.categories,
                        'tags', wm.tags,
                        'workflow_skill_level', wm.workflow_skill_level,
                        'workflow_industry', wm.workflow_industry
                    ) as metadata,
                    json_build_object(
                        'node_count', ws.node_count,
                        'connection_count', ws.connection_count,
                        'node_types', ws.node_types,
                        'workflow_json', ws.workflow_json
                    ) as structure,
                    json_build_object(
                        'explainer_text', wc.explainer_text,
                        'has_videos', wc.has_videos,
                        'video_count', wc.video_count
                    ) as content,
                    wbi.* as business_intel,
                    wcd.* as community_data,
                    wtd.* as technical_details,
                    wpa.* as performance_analytics,
                    wr.* as relationships
                FROM workflows w
                LEFT JOIN workflow_metadata wm ON w.workflow_id = wm.workflow_id
                LEFT JOIN workflow_structure ws ON w.workflow_id = ws.workflow_id
                LEFT JOIN workflow_content wc ON w.workflow_id = wc.workflow_id
                LEFT JOIN workflow_business_intelligence wbi ON w.workflow_id = wbi.workflow_id
                LEFT JOIN workflow_community_data wcd ON w.workflow_id = wcd.workflow_id
                LEFT JOIN workflow_technical_details wtd ON w.workflow_id = wtd.workflow_id
                LEFT JOIN workflow_performance_analytics wpa ON w.workflow_id = wpa.workflow_id
                LEFT JOIN workflow_relationships wr ON w.workflow_id = wr.workflow_id
                WHERE w.workflow_id = %s
            """, (workflow_id,))
            
            row = cursor.fetchone()
            
            if not row:
                self.send_error(404, "Workflow not found")
                cursor.close()
                conn.close()
                return
            
            # Extract data from the single query result
            workflow = dict(row)
            metadata = workflow.pop('metadata', {})
            structure = workflow.pop('structure', {})
            content = workflow.pop('content', {})
            business_intel = {k: v for k, v in workflow.items() if k.startswith('business_')} if any(k.startswith('business_') for k in workflow.keys()) else None
            community_data = {k: v for k, v in workflow.items() if k.startswith('community_')} if any(k.startswith('community_') for k in workflow.keys()) else None
            technical_details = {k: v for k, v in workflow.items() if k.startswith('technical_')} if any(k.startswith('technical_') for k in workflow.keys()) else None
            performance_analytics = {k: v for k, v in workflow.items() if k.startswith('performance_')} if any(k.startswith('performance_') for k in workflow.keys()) else None
            relationships = {k: v for k, v in workflow.items() if k.startswith('related_')} if any(k.startswith('related_') for k in workflow.keys()) else None
            
            cursor.close()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Pass all L2 enhanced data to the HTML generator
            html = self.generate_workflow_detail_html(
                workflow, metadata, structure, content,
                business_intel, community_data, technical_details,
                performance_analytics, relationships
            )
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Page Error: {str(e)}")
    
    def generate_workflow_detail_html(self, workflow, metadata, structure=None, content=None, 
                                        business_intel=None, community_data=None, technical_details=None,
                                        performance_analytics=None, relationships=None):
        """Generate comprehensive workflow detail HTML page following the original design specification"""
        
        # Determine status and layer completion
        layers_success = []
        for i in range(1, 8):
            layer_key = f'layer{i}_success'
            if layer_key in workflow:
                layers_success.append(workflow[layer_key])
        
        all_success = all(layers_success) if layers_success else False
        any_success = any(layers_success) if layers_success else False
        success_count = sum(layers_success) if layers_success else 0
        
        # Smart status indicators
        if all_success:
            status_badge = '<span class="status-badge success">✅ Fully Scraped</span>'
            status_emoji = '🚀'
        elif any_success:
            status_badge = '<span class="status-badge partial">⚠️ Partially Scraped</span>'
            status_emoji = '🔄'
        else:
            status_badge = '<span class="status-badge pending">⏳ Not Scraped</span>'
            status_emoji = '⏳'
        
        # Hero section metrics
        quality_score = workflow.get('quality_score', 0) or 0
        processing_time = workflow.get('processing_time', 0) or 0
        views = metadata.get('views', 0) if metadata else 0
        author = metadata.get('author_name', 'Unknown') if metadata else 'Unknown'
        use_case = metadata.get('use_case', 'General Automation') if metadata else 'General Automation'
        
        # Smart summary metrics
        smart_summary = []
        if views and views > 0:
            smart_summary.append(f"👀 {views:,} views")
        if processing_time and processing_time > 0:
            smart_summary.append(f"⚡ {processing_time:.1f}s execution")
        if quality_score and quality_score > 0:
            smart_summary.append(f"📊 {quality_score:.1f}% quality")
        if success_count and success_count > 0:
            smart_summary.append(f"🔄 {success_count}/7 layers complete")
        
        smart_summary_html = ' • '.join(smart_summary) if smart_summary else "📋 Basic workflow data available"
        
        # Layer progress indicator
        layer_progress = []
        for i in range(1, 8):
            layer_key = f'layer{i}_success'
            if layer_key in workflow:
                status = '✅' if workflow[layer_key] else '⏳'
                layer_progress.append(f'<span class="layer-indicator {status.lower()}">L{i}{status}</span>')
        
        layers_html = ' '.join(layer_progress)
        
        # Check if we have rich data
        has_rich_data = metadata and (
            metadata.get('description') or 
            metadata.get('author_name') or 
            metadata.get('use_case') or 
            metadata.get('views') or
            metadata.get('tags')
        )
        
        # Generate smart cards based on available data
        smart_cards = []
        
        # Business Intelligence Card (Priority 1) - ALWAYS SHOW
        business_metrics = []
        if metadata and metadata.get('use_case'):
            business_metrics.append(f"<div class='metric-item'><span class='metric-label'>Use Case</span><span class='metric-value'>{metadata.get('use_case')}</span></div>")
        else:
            business_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Use Case</span><span class='metric-value'>⏳ Pending Layer 1 extraction</span></div>")
        
        if metadata and metadata.get('workflow_industry'):
            business_metrics.append(f"<div class='metric-item'><span class='metric-label'>Industry</span><span class='metric-value'>{metadata.get('workflow_industry')}</span></div>")
        else:
            business_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Industry</span><span class='metric-value'>⏳ Pending extraction</span></div>")
        
        if metadata and metadata.get('workflow_skill_level'):
            business_metrics.append(f"<div class='metric-item'><span class='metric-label'>Skill Level</span><span class='metric-value'>{metadata.get('workflow_skill_level')}</span></div>")
        else:
            business_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Skill Level</span><span class='metric-value'>⏳ Pending extraction</span></div>")
        
        if business_intel:
            business_metrics.append(f"<div class='metric-item'><span class='metric-label'>ROI Estimate</span><span class='metric-value'>⏳ Layer 2 Enhanced pending</span></div>")
            business_metrics.append(f"<div class='metric-item'><span class='metric-label'>Cost Savings</span><span class='metric-value'>⏳ Layer 2 Enhanced pending</span></div>")
        
        # ALWAYS show this card
        smart_cards.append(f'''
        <div class="smart-card business-card">
            <div class="card-header">
                <h3>💼 Business Intelligence</h3>
                <span class="card-icon">💼</span>
            </div>
            <div class="card-content">
                {' '.join(business_metrics)}
            </div>
        </div>
        ''')
        
        # Technical Overview Card (Priority 2) - ALWAYS SHOW
        technical_metrics = []
        if quality_score and quality_score > 0:
            technical_metrics.append(f"<div class='metric-item'><span class='metric-label'>Quality Score</span><span class='metric-value'>{quality_score:.1f}%</span></div>")
        else:
            technical_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Quality Score</span><span class='metric-value'>⏳ Not yet calculated</span></div>")
        
        if structure and structure.get('node_count'):
            technical_metrics.append(f"<div class='metric-item'><span class='metric-label'>Nodes</span><span class='metric-value'>{structure.get('node_count')}</span></div>")
        else:
            technical_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Nodes</span><span class='metric-value'>⏳ Layer 2 pending</span></div>")
        
        if processing_time and processing_time > 0:
            technical_metrics.append(f"<div class='metric-item'><span class='metric-label'>Execution Time</span><span class='metric-value'>{processing_time:.2f}s</span></div>")
        else:
            technical_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Execution Time</span><span class='metric-value'>⏳ Not yet measured</span></div>")
        
        if metadata and metadata.get('workflow_estimated_time'):
            technical_metrics.append(f"<div class='metric-item'><span class='metric-label'>Setup Time</span><span class='metric-value'>{metadata.get('workflow_estimated_time')}</span></div>")
        else:
            technical_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Setup Time</span><span class='metric-value'>⏳ Pending extraction</span></div>")
        
        # ALWAYS show this card
        smart_cards.append(f'''
        <div class="smart-card technical-card">
            <div class="card-header">
                <h3>🔧 Technical Overview</h3>
                <span class="card-icon">🔧</span>
            </div>
            <div class="card-content">
                {' '.join(technical_metrics)}
                <div class="layer-progress">
                    <span class="progress-label">Layer Progress:</span>
                    {layers_html}
                </div>
            </div>
        </div>
        ''')
        
        # Community Metrics Card (Priority 3) - ALWAYS SHOW
        community_metrics = []
        if views and views > 0:
            community_metrics.append(f"<div class='metric-item'><span class='metric-label'>Views</span><span class='metric-value'>{views:,}</span></div>")
        else:
            community_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Views</span><span class='metric-value'>⏳ Pending Layer 1</span></div>")
        
        if author and author != 'Unknown':
            community_metrics.append(f"<div class='metric-item'><span class='metric-label'>Author</span><span class='metric-value'>{author}</span></div>")
        else:
            community_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Author</span><span class='metric-value'>⏳ Pending extraction</span></div>")
        
        if metadata and metadata.get('tags') and len(metadata.get('tags', [])) > 0:
            tags_html = ' '.join([f'<span class="tag-badge">{tag}</span>' for tag in metadata.get('tags', [])])
            community_metrics.append(f"<div class='metric-item'><span class='metric-label'>Tags</span><div class='tags-container'>{tags_html}</div></div>")
        else:
            community_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Tags</span><span class='metric-value'>⏳ Pending Layer 1</span></div>")
        
        if community_data:
            community_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Community Rating</span><span class='metric-value'>⏳ Layer 2 Enhanced pending</span></div>")
        
        # ALWAYS show this card
        smart_cards.append(f'''
        <div class="smart-card community-card">
            <div class="card-header">
                <h3>👥 Community Metrics</h3>
                <span class="card-icon">👥</span>
            </div>
            <div class="card-content">
                {' '.join(community_metrics)}
            </div>
        </div>
        ''')
        
        # Content Details Card (Priority 4) - ALWAYS SHOW
        content_sections = []
        if metadata and metadata.get('description'):
            content_sections.append(f'''
            <div class="content-section">
                <h4>📝 Description</h4>
                <div class="content-text">{metadata.get('description')}</div>
            </div>
            ''')
        else:
            content_sections.append(f'''
            <div class="content-section pending-section">
                <h4>📝 Description</h4>
                <div class="content-text">⏳ Pending Layer 1 extraction</div>
            </div>
            ''')
        
        # ALWAYS show this card
        smart_cards.append(f'''
        <div class="smart-card content-card">
            <div class="card-header">
                <h3>📋 Content Details</h3>
                <span class="card-icon">📋</span>
            </div>
            <div class="card-content">
                {''.join(content_sections)}
            </div>
        </div>
        ''')
        
        # Performance Analytics Card (Priority 5) - ALWAYS SHOW
        perf_metrics = []
        if performance_analytics and performance_analytics.get('execution_success_rate'):
            perf_metrics.append(f"<div class='metric-item'><span class='metric-label'>Success Rate</span><span class='metric-value'>{performance_analytics.get('execution_success_rate')}%</span></div>")
        else:
            perf_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Success Rate</span><span class='metric-value'>⏳ Layer 2 Enhanced pending</span></div>")
        
        if performance_analytics and performance_analytics.get('avg_execution_time'):
            perf_metrics.append(f"<div class='metric-item'><span class='metric-label'>Avg Execution</span><span class='metric-value'>{performance_analytics.get('avg_execution_time')}s</span></div>")
        else:
            perf_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Avg Execution</span><span class='metric-value'>⏳ Pending analytics</span></div>")
        
        smart_cards.append(f'''
        <div class="smart-card performance-card">
            <div class="card-header">
                <h3>📊 Performance Analytics</h3>
                <span class="card-icon">📊</span>
            </div>
            <div class="card-content">
                {' '.join(perf_metrics)}
            </div>
        </div>
        ''')
        
        # Workflow Relationships Card (Priority 6) - ALWAYS SHOW
        rel_metrics = []
        if relationships and relationships.get('related_workflows'):
            rel_metrics.append(f"<div class='metric-item'><span class='metric-label'>Related Workflows</span><span class='metric-value'>{len(relationships.get('related_workflows', []))} found</span></div>")
        else:
            rel_metrics.append(f"<div class='metric-item pending'><span class='metric-label'>Related Workflows</span><span class='metric-value'>⏳ Layer 2 Enhanced pending</span></div>")
        
        smart_cards.append(f'''
        <div class="smart-card relationships-card">
            <div class="card-header">
                <h3>🔗 Workflow Relationships</h3>
                <span class="card-icon">🔗</span>
            </div>
            <div class="card-content">
                {' '.join(rel_metrics)}
            </div>
        </div>
        ''')
        
        smart_cards_html = ''.join(smart_cards)
        
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
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .info-item {{
            display: flex;
            flex-direction: column;
            gap: 5px;
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
        
        .content-section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .content-section h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            font-weight: 600;
        }}
        
        .content-text {{
            color: #333;
            line-height: 1.6;
            font-size: 1em;
        }}
        
        .content-text p {{
            margin-bottom: 15px;
        }}
        
        .content-text ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}
        
        .content-text li {{
            margin-bottom: 8px;
        }}
        
        .tags-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .tag-badge {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .no-data {{
            background: #f8f9fa;
            border-left: 4px solid #ffc107;
        }}
        
        .no-data h3 {{
            color: #856404;
        }}
        
        .no-data .content-text {{
            color: #856404;
        }}
        
        .category-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .category-badge {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* HERO SECTION STYLES */
        .hero-section {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 25px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .hero-title {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .hero-title h1 {{
            color: #667eea;
            font-size: 2.8em;
            font-weight: 700;
            margin: 0;
        }}
        
        .hero-title .status-badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }}
        
        .status-badge.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-badge.partial {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .status-badge.pending {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .workflow-title {{
            margin: 25px 0;
        }}
        
        .workflow-title h2 {{
            color: #333;
            font-size: 2.2em;
            font-weight: 600;
            line-height: 1.3;
            margin-bottom: 15px;
        }}
        
        .workflow-url {{
            margin: 15px 0;
            font-size: 1.1em;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .smart-summary {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #667eea;
        }}
        
        .smart-summary h3 {{
            color: #667eea;
            font-size: 1.2em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .smart-summary p {{
            color: #495057;
            font-size: 1.1em;
            line-height: 1.5;
        }}
        
        /* SMART CARDS GRID */
        .smart-cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .smart-card {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 0;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .smart-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .card-header h3 {{
            color: #333;
            font-size: 1.3em;
            font-weight: 600;
            margin: 0;
        }}
        
        .card-icon {{
            font-size: 1.5em;
        }}
        
        .card-content {{
            padding: 25px;
        }}
        
        .metric-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f8f9fa;
        }}
        
        .metric-item:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.95em;
            font-weight: 500;
        }}
        
        .metric-value {{
            color: #333;
            font-size: 1.1em;
            font-weight: 600;
        }}
        
        .layer-progress {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e9ecef;
        }}
        
        .progress-label {{
            color: #666;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        
        .layer-indicator {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 0.8em;
            font-weight: 500;
            margin-right: 5px;
        }}
        
        .layer-indicator.✅ {{
            background: #d4edda;
            color: #155724;
        }}
        
        .layer-indicator.⏳ {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .pending-section {{
            background: #f8f9fa;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .pending-section h4 {{
            color: #856404;
        }}
        
        .pending-section .content-text {{
            color: #856404;
        }}
        
        /* RESPONSIVE DESIGN */
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .hero-section {{
                padding: 25px;
            }}
            
            .hero-title h1 {{
                font-size: 2.2em;
            }}
            
            .workflow-title h2 {{
                font-size: 1.8em;
            }}
            
            .smart-cards-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .smart-card {{
                margin-bottom: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Workflow List</a>
        
        <!-- HERO SECTION - Above the fold -->
        <div class="hero-section">
            <div class="hero-title">
                <h1>{status_emoji} Workflow #{workflow['workflow_id']}</h1>
                {status_badge}
            </div>
            
            {f'<div class="workflow-title"><h2>{metadata.get("title", "Untitled Workflow") if metadata else "Untitled Workflow"}</h2></div>' if metadata and metadata.get("title") else ''}
            
            <div class="workflow-url">
                <strong>🔗 URL:</strong> <a href="{workflow['url']}" target="_blank">{workflow['url']}</a>
            </div>
            
            <div class="smart-summary">
                <h3>📊 Smart Summary</h3>
                <p>{smart_summary_html}</p>
            </div>
            
            {f'<div class="category-badges">' + ''.join([f'<span class="category-badge">{cat}</span>' for cat in metadata.get("categories", [])]) + '</div>' if metadata and metadata.get('categories') else ''}
        </div>
        
        <!-- SMART CARDS GRID -->
        <div class="smart-cards-grid">
            {smart_cards_html}
        </div>
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
            category_filter = query_params.get('category', [None])[0]
            status_filter = query_params.get('status', [None])[0]
            
            limit = 500  # Load more workflows for better client-side filtering
            offset = (page - 1) * limit
            
            workflows, total = get_workflows(limit, offset, search, sort_by, order, category_filter, status_filter)
            stats = get_statistics()
            categories = get_categories()
            
            total_pages = (total + limit - 1) // limit
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_html(workflows, total, page, total_pages, search, sort_by, order, stats, categories, category_filter, status_filter)
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Page Error: {str(e)}")
    
    def generate_html(self, workflows, total, page, total_pages, search, sort_by, order, stats, categories, category_filter, status_filter):
        """Generate HTML page with sorting and filtering functionality"""
        
        # Generate sort links
        def sort_link(column, display_name):
            active_class = "sort-active" if sort_by == column else ""
            arrow = " ↑" if sort_by == column and order.lower() == 'asc' else " ↓" if sort_by == column else " ↕"
            
            # Use JavaScript onclick for instant client-side sorting
            return f'''
                <span onclick="sortTable('{column}')" class="sort-link {active_class}" data-sort="{column}" data-label="{display_name}" style="cursor: pointer;">
                    {display_name}{arrow}
                </span>
            '''
        
        # Prepare workflows data for JavaScript (outside f-string to avoid syntax issues)
        workflows_json = json.dumps([dict(w) for w in workflows], default=str, ensure_ascii=False)
        
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
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        @media (max-width: 1400px) {{
            .stats-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
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
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .filter-form {{
            width: 100%;
        }}
        
        .filter-row {{
            display: grid;
            grid-template-columns: 2.5fr 1fr 1fr auto;
            gap: 20px;
            align-items: end;
        }}
        
        @media (max-width: 1024px) {{
            .filter-row {{
                grid-template-columns: 1fr 1fr;
            }}
        }}
        
        @media (max-width: 640px) {{
            .filter-row {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            min-width: 150px;
        }}
        
        .filter-group label {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #2d3748;
            font-size: 14px;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        
        .filter-select {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            font-size: 1em;
            background: white;
            transition: border-color 0.3s;
        }}
        
        .filter-actions {{
            display: flex;
            gap: 10px;
            align-items: center;
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
        
        .search-icon {{
            background: #6c757d;
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
        
        .loading {{
            opacity: 0.6;
            pointer-events: none;
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
            <p>Enhanced sortable workflow data viewer with real-time search</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_workflows']:,}</div>
                <div class="stat-label">Total Workflows</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('layer1_complete', 0):,}/{stats['total_workflows']:,}</div>
                <div class="stat-label">L1 Completed ({(stats.get('layer1_complete', 0) / stats['total_workflows'] * 100 if stats['total_workflows'] > 0 else 0):.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('layer2_complete', 0):,}/{stats['total_workflows']:,}</div>
                <div class="stat-label">L2 Completed ({(stats.get('layer2_complete', 0) / stats['total_workflows'] * 100 if stats['total_workflows'] > 0 else 0):.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('layer3_complete', 0):,}/{stats['total_workflows']:,}</div>
                <div class="stat-label">L3 Completed ({(stats.get('layer3_complete', 0) / stats['total_workflows'] * 100 if stats['total_workflows'] > 0 else 0):.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{(stats['avg_quality_score'] if stats['avg_quality_score'] is not None else 0):.1f}%</div>
                <div class="stat-label">Average Quality</div>
            </div>
        </div>
        
        <div class="search-container">
            <form method="GET" class="filter-form" id="searchForm">
                <div class="filter-row">
                    <div class="filter-group">
                        <label for="search">Search:</label>
                        <input type="text" name="search" placeholder="Search by workflow ID, URL, or title..." 
                               value="{search or ''}" class="search-box" id="search" autocomplete="off">
                    </div>
                    
                    <div class="filter-group">
                        <label for="category">Category:</label>
                        <select name="category" id="category" class="filter-select">
                            <option value="">All Categories</option>
                            {''.join([f'<option value="{cat}"{" selected" if cat == category_filter else ""}>{cat}</option>' for cat in categories])}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="status">Status:</label>
                        <select name="status" id="status" class="filter-select">
                            <option value="">All Status</option>
                            <option value="fully_successful"{" selected" if status_filter == "fully_successful" else ""}>Fully Successful</option>
                            <option value="partial_success"{" selected" if status_filter == "partial_success" else ""}>Partial Success</option>
                            <option value="failed"{" selected" if status_filter == "failed" else ""}>Failed</option>
                            <option value="invalid"{" selected" if status_filter == "invalid" else ""}>Invalid</option>
                            <option value="pending"{" selected" if status_filter == "pending" else ""}>Pending</option>
                        </select>
                    </div>
                    
                    <div class="filter-actions">
                        <button type="submit" class="btn">🔍 Search</button>
                        <button type="button" class="btn search-icon" onclick="clearSearch()">Clear</button>
                    </div>
                </div>
                <input type="hidden" name="sort" value="{sort_by}">
                <input type="hidden" name="order" value="{order}">
            </form>
        </div>
        
        <div class="table-container" id="tableContainer">
            <table>
                <thead>
                    <tr>
                        <th>{sort_link('workflow_id', 'Workflow ID')}</th>
                        <th>{sort_link('title', 'Title')}</th>
                        <th>{sort_link('quality_score', 'Quality Score')}</th>
                        <th>{sort_link('status', 'Status')}</th>
                        <th>{sort_link('categories', 'Categories')}</th>
                        <th>{sort_link('extracted_at', 'Extracted At')}</th>
                    </tr>
                </thead>
                <tbody id="workflowsTable">
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
                            <div class="title-cell">
                                {workflow.get('title', 'Untitled Workflow')[:50]}{'...' if len(workflow.get('title', '')) > 50 else ''}
                            </div>
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
            category_param = f"&category={urllib.parse.quote(category_filter)}" if category_filter else ""
            status_param = f"&status={urllib.parse.quote(status_filter)}" if status_filter else ""
            sort_param = f"&sort={sort_by}&order={order}"
            
            prev_style = 'style="pointer-events: none; opacity: 0.5;"' if page == 1 else ""
            html += f'<a href="/?page={page-1}{search_param}{category_param}{status_param}{sort_param}" class="page-btn" {prev_style}>← Previous</a>'
            
            # Page numbers (show max 7 pages around current)
            start_page = max(1, page - 3)
            end_page = min(total_pages, page + 3)
            
            if start_page > 1:
                html += f'<a href="/?page=1{search_param}{category_param}{status_param}{sort_param}" class="page-btn">1</a>'
                if start_page > 2:
                    html += '<span style="padding: 10px;">...</span>'
            
            for p in range(start_page, end_page + 1):
                active_class = 'active' if p == page else ''
                html += f'<a href="/?page={p}{search_param}{category_param}{status_param}{sort_param}" class="page-btn {active_class}">{p}</a>'
            
            if end_page < total_pages:
                if end_page < total_pages - 1:
                    html += '<span style="padding: 10px;">...</span>'
                html += f'<a href="/?page={total_pages}{search_param}{category_param}{status_param}{sort_param}" class="page-btn">{total_pages}</a>'
            
            # Next button
            next_style = 'style="pointer-events: none; opacity: 0.5;"' if page == total_pages else ""
            html += f'<a href="/?page={page+1}{search_param}{category_param}{status_param}{sort_param}" class="page-btn" {next_style}>Next →</a>'
        
        html += f"""
        </div>
        
        <div class="refresh-info">
            Showing {(page-1)*50 + 1} to {min(page*50, total)} of {total:,} workflows • 
            Page {page} of {total_pages} • 
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        let searchTimeout;
        let isSearching = false;
        let currentSort = '{sort_by}';
        let currentOrder = '{order}';
        let originalWorkflows = {workflows_json};
        let allWorkflows = [...originalWorkflows]; // Copy for filtering
        
        // Client-side sorting for instant response
        function sortTable(column) {{
            // Toggle order if clicking same column
            if (currentSort === column) {{
                currentOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSort = column;
                currentOrder = 'desc';
            }}
            
            // Sort the workflows array
            allWorkflows.sort((a, b) => {{
                let valA = a[column];
                let valB = b[column];
                
                // Handle numeric columns
                if (column === 'workflow_id' || column === 'quality_score') {{
                    valA = parseInt(valA) || 0;
                    valB = parseInt(valB) || 0;
                }} else if (column === 'status') {{
                    // Status sorting: fully > partial > failed > pending
                    const getStatusValue = (w) => {{
                        if (w.layer1_success && w.layer2_success && w.layer3_success) return 3;
                        if (w.layer1_success || w.layer2_success || w.layer3_success) return 2;
                        if (w.error_message) return 1;
                        return 0;
                    }};
                    valA = getStatusValue(a);
                    valB = getStatusValue(b);
                }} else {{
                    // String comparison (null-safe)
                    valA = (valA || '').toString().toLowerCase();
                    valB = (valB || '').toString().toLowerCase();
                }}
                
                if (currentOrder === 'asc') {{
                    return valA > valB ? 1 : valA < valB ? -1 : 0;
                }} else {{
                    return valA < valB ? 1 : valA > valB ? -1 : 0;
                }}
            }});
            
            // Re-render table
            renderTable();
            
            // Update column headers
            updateSortIndicators();
        }}
        
        function renderTable() {{
            const tbody = document.getElementById('workflowsTable');
            tbody.innerHTML = allWorkflows.slice(0, 50).map(w => generateWorkflowRow(w)).join('');
        }}
        
        function generateWorkflowRow(w) {{
            const statusBadge = w.layer1_success && w.layer2_success && w.layer3_success 
                ? '<span class="badge badge-success">✅ Fully Successful</span>'
                : (w.layer1_success || w.layer2_success || w.layer3_success)
                ? '<span class="badge badge-warning">⚠️ Partial Success</span>'
                : w.error_message 
                ? '<span class="badge badge-error">❌ Failed</span>'
                : '<span class="badge badge-pending">⏳ Pending</span>';
            
            return `
                <tr>
                    <td><a href="/workflow/${{w.workflow_id}}" class="workflow-link">${{w.workflow_id}}</a></td>
                    <td>${{w.title || 'N/A'}}</td>
                    <td>${{w.quality_score ? w.quality_score.toFixed(1) + '%' : 'N/A'}}</td>
                    <td>${{statusBadge}}</td>
                    <td>${{w.categories || 'N/A'}}</td>
                    <td>${{w.extracted_at ? new Date(w.extracted_at).toLocaleString() : 'N/A'}}</td>
                </tr>
            `;
        }}
        
        function updateSortIndicators() {{
            // Update all column headers to show current sort
            document.querySelectorAll('th[data-sort]').forEach(th => {{
                const column = th.getAttribute('data-sort');
                const arrow = column === currentSort ? (currentOrder === 'asc' ? ' ↑' : ' ↓') : ' ↕';
                th.textContent = th.getAttribute('data-label') + arrow;
            }});
        }}
        
        // Client-side filtering and search
        function filterAndSearch() {{
            const searchValue = document.getElementById('search').value.trim().toLowerCase();
            const categoryFilter = document.getElementById('category').value.toLowerCase();
            const statusFilter = document.getElementById('status').value;
            
            // Filter workflows from original dataset
            let filteredWorkflows = originalWorkflows.filter(w => {{
                // Search filter
                const matchesSearch = !searchValue || 
                    (w.workflow_id && w.workflow_id.toString().toLowerCase().includes(searchValue)) ||
                    (w.title && w.title.toLowerCase().includes(searchValue)) ||
                    (w.url && w.url.toLowerCase().includes(searchValue));
                
                // Category filter
                // Category filter (handle JSONB arrays)
                const matchesCategory = !categoryFilter || (() => {
                    if (!w.categories) return false;
                    try {
                        // If it's a string that looks like JSON array, parse it
                        if (typeof w.categories === 'string' && w.categories.startsWith('[')) {
                            const categories = JSON.parse(w.categories);
                            return categories.some(cat => cat.toLowerCase().includes(categoryFilter));
                        }
                        // If it's already an array
                        if (Array.isArray(w.categories)) {
                            return w.categories.some(cat => cat.toLowerCase().includes(categoryFilter));
                        }
                        // If it's a simple string
                        return w.categories.toLowerCase().includes(categoryFilter);
                    } catch (e) {
                        return w.categories.toLowerCase().includes(categoryFilter);
                    }
                })();
                
                // Status filter
                const matchesStatus = !statusFilter || (() => {{
                    if (statusFilter === 'fully_successful') 
                        return w.layer1_success && w.layer2_success && w.layer3_success;
                    if (statusFilter === 'partial_success') 
                        return (w.layer1_success || w.layer2_success || w.layer3_success) && 
                               !(w.layer1_success && w.layer2_success && w.layer3_success);
                    if (statusFilter === 'failed') 
                        return w.error_message;
                    if (statusFilter === 'pending') 
                        return !w.layer1_success && !w.layer2_success && !w.layer3_success && !w.error_message;
                    return true;
                }})();
                
                return matchesSearch && matchesCategory && matchesStatus;
            }});
            
            // Update the workflows array and re-render
            allWorkflows = filteredWorkflows;
            renderTable();
        }}
        
        // Dynamic search as you type
        document.getElementById('search').addEventListener('input', function() {{
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {{
                filterAndSearch();
            }}, 300); // Reduced to 300ms for faster response
        }});
        
        // Search on Enter key
        document.getElementById('search').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                clearTimeout(searchTimeout);
                performSearch(this.value.trim());
            }}
        }});
        
        // Filter change handlers
        document.getElementById('category').addEventListener('change', function() {{
            filterAndSearch();
        }});
        
        document.getElementById('status').addEventListener('change', function() {{
            filterAndSearch();
        }});
        
        function performSearch(searchValue) {{
            if (isSearching) return;
            
            isSearching = true;
            const tableContainer = document.getElementById('tableContainer');
            tableContainer.classList.add('loading');
            
            const category = document.getElementById('category').value;
            const status = document.getElementById('status').value;
            const sort = new URLSearchParams(window.location.search).get('sort') || 'extracted_at';
            const order = new URLSearchParams(window.location.search).get('order') || 'desc';
            
            const params = new URLSearchParams();
            if (searchValue) params.set('search', searchValue);
            if (category) params.set('category', category);
            if (status) params.set('status', status);
            params.set('sort', sort);
            params.set('order', order);
            params.set('page', '1');
            
            fetch(`/api/workflows?${{params.toString()}}`)
                .then(response => response.json())
                .then(data => {{
                    updateTable(data.workflows);
                    updatePagination(data.page, data.total_pages, searchValue, category, status, sort, order);
                    isSearching = false;
                    tableContainer.classList.remove('loading');
                }})
                .catch(error => {{
                    console.error('Search error:', error);
                    isSearching = false;
                    tableContainer.classList.remove('loading');
                }});
        }}
        
        function updateTable(workflows) {{
            const tbody = document.getElementById('workflowsTable');
            
            if (workflows.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #666;">No workflows found</td></tr>';
                return;
            }}
            
            tbody.innerHTML = workflows.map(workflow => {{
                const status = workflow.layer1_success && workflow.layer2_success && workflow.layer3_success ? 'Complete' : 'Partial';
                const statusClass = status === 'Complete' ? 'status-success' : 'status-partial';
                
                const categories = workflow.categories || [];
                let categoriesHtml = '<span style="color: #999;">Uncategorized</span>';
                if (categories.length > 0) {{
                    const categoryBadges = categories.slice(0, 2).map(cat => `<span class="category-badge">${{cat}}</span>`).join(' ');
                    const moreCount = categories.length > 2 ? `<span class="category-more">+${{categories.length - 2}}</span>` : '';
                    categoriesHtml = categoryBadges + moreCount;
                }}
                
                return `
                    <tr>
                        <td>
                            <a href="/workflow/${{workflow.workflow_id}}" class="workflow-link">
                                ${{workflow.workflow_id}}
                            </a>
                        </td>
                        <td>
                            <div class="title-cell">
                                ${{workflow.title.substring(0, 50)}}{{(workflow.title.length > 50 ? '...' : '')}}
                            </div>
                        </td>
                        <td>
                            <div style="min-width: 100px;">
                                <div style="margin-bottom: 5px;">${{workflow.quality_score.toFixed(1)}}%</div>
                                <div class="quality-bar">
                                    <div class="quality-fill" style="width: ${{workflow.quality_score}}%"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="status-badge ${{statusClass}}">${{status === 'Complete' ? '✅ Complete' : '⚠️ Partial'}}</span>
                        </td>
                        <td>${{categoriesHtml}}</td>
                        <td>${{workflow.extracted_at ? new Date(workflow.extracted_at).toLocaleDateString() + ' ' + new Date(workflow.extracted_at).toLocaleTimeString().substring(0, 5) : 'N/A'}}</td>
                    </tr>
                `;
            }}).join('');
        }}
        
        function updatePagination(page, totalPages, search, category, status, sort, order) {{
            const pagination = document.querySelector('.pagination');
            
            if (totalPages <= 1) {{
                pagination.innerHTML = '';
                return;
            }}
            
            let paginationHTML = '';
            
            // Previous button
            if (page > 1) {{
                const prevParams = new URLSearchParams();
                if (search) prevParams.set('search', search);
                if (category) prevParams.set('category', category);
                if (status) prevParams.set('status', status);
                prevParams.set('sort', sort);
                prevParams.set('order', order);
                prevParams.set('page', page - 1);
                paginationHTML += `<a href="/?${{prevParams.toString()}}" class="page-btn">← Previous</a>`;
            }}
            
            // Page numbers
            const startPage = Math.max(1, page - 3);
            const endPage = Math.min(totalPages, page + 3);
            
            if (startPage > 1) {{
                const firstParams = new URLSearchParams();
                if (search) firstParams.set('search', search);
                if (category) firstParams.set('category', category);
                if (status) firstParams.set('status', status);
                firstParams.set('sort', sort);
                firstParams.set('order', order);
                firstParams.set('page', 1);
                paginationHTML += `<a href="/?${{firstParams.toString()}}" class="page-btn">1</a>`;
                if (startPage > 2) {{
                    paginationHTML += '<span style="padding: 10px;">...</span>';
                }}
            }}
            
            for (let p = startPage; p <= endPage; p++) {{
                const activeClass = p === page ? 'active' : '';
                const pageParams = new URLSearchParams();
                if (search) pageParams.set('search', search);
                if (category) pageParams.set('category', category);
                if (status) pageParams.set('status', status);
                pageParams.set('sort', sort);
                pageParams.set('order', order);
                pageParams.set('page', p);
                paginationHTML += `<a href="/?${{pageParams.toString()}}" class="page-btn ${{activeClass}}">${{p}}</a>`;
            }}
            
            if (endPage < totalPages) {{
                if (endPage < totalPages - 1) {{
                    paginationHTML += '<span style="padding: 10px;">...</span>';
                }}
                const lastParams = new URLSearchParams();
                if (search) lastParams.set('search', search);
                if (category) lastParams.set('category', category);
                if (status) lastParams.set('status', status);
                lastParams.set('sort', sort);
                lastParams.set('order', order);
                lastParams.set('page', totalPages);
                paginationHTML += `<a href="/?${{lastParams.toString()}}" class="page-btn">${{totalPages}}</a>`;
            }}
            
            // Next button
            if (page < totalPages) {{
                const nextParams = new URLSearchParams();
                if (search) nextParams.set('search', search);
                if (category) nextParams.set('category', category);
                if (status) nextParams.set('status', status);
                nextParams.set('sort', sort);
                nextParams.set('order', order);
                nextParams.set('page', page + 1);
                paginationHTML += `<a href="/?${{nextParams.toString()}}" class="page-btn">Next →</a>`;
            }}
            
            pagination.innerHTML = paginationHTML;
        }}
        
        function clearSearch() {{
            document.getElementById('search').value = '';
            document.getElementById('category').value = '';
            document.getElementById('status').value = '';
            filterAndSearch();
        }}
        
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
    print(f"🔧 Features: Dynamic Search, Sortable columns, Pagination, Auto-refresh")
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
