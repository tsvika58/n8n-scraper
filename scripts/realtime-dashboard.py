#!/usr/bin/env python3
"""
Real-Time Scraping Dashboard
Shows live progress, statistics, and current scraping status
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

# Database connection
DB_CONFIG = {
    'host': 'n8n-scraper-database',
    'port': 5432,
    'database': 'n8n_scraper',
    'user': 'scraper_user',
    'password': 'scraper_pass'
}

class RealtimeDashboard:
    def __init__(self):
        self.stats = {}
        self.last_update = datetime.now()
        self.is_scraping = False
        self.current_workflow = None
        
    def get_database_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_current_stats(self):
        """Get current database statistics"""
        conn = self.get_database_connection()
        if not conn:
            return self.stats
            
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_workflows,
                    COUNT(*) FILTER (WHERE layer1_success AND layer2_success AND layer3_success) as fully_successful,
                    COUNT(*) FILTER (WHERE NOT (layer1_success AND layer2_success AND layer3_success)) as partial_success,
                    COUNT(*) FILTER (WHERE error_message IS NOT NULL) as with_errors,
                    ROUND(AVG(quality_score)::numeric, 2) as avg_quality_score,
                    ROUND(AVG(processing_time)::numeric, 2) as avg_processing_time,
                    MIN(extracted_at) as first_workflow,
                    MAX(extracted_at) as latest_workflow
                FROM workflows;
            """)
            
            stats = cursor.fetchone()
            
            # Get recent activity (last 5 minutes)
            five_min_ago = datetime.now() - timedelta(minutes=5)
            cursor.execute("""
                SELECT COUNT(*) as recent_workflows
                FROM workflows 
                WHERE extracted_at > %s;
            """, (five_min_ago,))
            
            recent = cursor.fetchone()
            
            # Get current workflow being processed (if any)
            cursor.execute("""
                SELECT workflow_id, url, extracted_at, processing_time
                FROM workflows 
                WHERE extracted_at > NOW() - INTERVAL '30 seconds'
                ORDER BY extracted_at DESC 
                LIMIT 1;
            """)
            
            current = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            # Update stats
            self.stats.update({
                'total_workflows': stats['total_workflows'],
                'fully_successful': stats['fully_successful'],
                'partial_success': stats['partial_success'],
                'with_errors': stats['with_errors'],
                'avg_quality_score': stats['avg_quality_score'],
                'avg_processing_time': stats['avg_processing_time'],
                'recent_workflows': recent['recent_workflows'],
                'current_workflow': dict(current) if current else None,
                'last_update': datetime.now().isoformat(),
                'is_scraping': recent['recent_workflows'] > 0,
                'success_rate': round((stats['fully_successful'] / stats['total_workflows'] * 100), 1) if stats['total_workflows'] > 0 else 0
            })
            
            return self.stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return self.stats
    
    def get_workflow_details(self, workflow_id):
        """Get full details for a specific workflow"""
        conn = self.get_database_connection()
        if not conn:
            return None
            
        try:
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
            
            cursor.close()
            conn.close()
            
            return {
                'workflow': dict(workflow),
                'metadata': dict(metadata) if metadata else None,
                'structure': dict(structure) if structure else None,
                'content': dict(content) if content else None
            }
            
        except Exception as e:
            print(f"Error getting workflow details: {e}")
            return None

# Global dashboard instance
dashboard = RealtimeDashboard()

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/stats':
            self.serve_stats()
        elif path.startswith('/api/workflow/'):
            workflow_id = path.split('/')[-1]
            self.serve_workflow_details(workflow_id)
        elif path == '/api/recent':
            self.serve_recent_workflows()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = self.generate_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_stats(self):
        """Serve current statistics as JSON"""
        stats = dashboard.get_current_stats()
        
        # Convert Decimal to float for JSON serialization
        def convert_decimals(obj):
            if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                if isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                else:
                    return [convert_decimals(item) for item in obj]
            elif hasattr(obj, 'to_eng_string'):  # Decimal type
                return float(obj)
            else:
                return obj
        
        stats = convert_decimals(stats)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats, indent=2).encode('utf-8'))
    
    def serve_workflow_details(self, workflow_id):
        """Serve full workflow details as JSON"""
        details = dashboard.get_workflow_details(workflow_id)
        
        if details:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(details, indent=2).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def serve_recent_workflows(self):
        """Serve recent workflows list"""
        conn = dashboard.get_database_connection()
        if not conn:
            self.send_response(500)
            self.end_headers()
            return
            
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT 
                    workflow_id,
                    LEFT(url, 60) as url_preview,
                    quality_score,
                    layer1_success,
                    layer2_success,
                    layer3_success,
                    processing_time,
                    extracted_at
                FROM workflows
                ORDER BY extracted_at DESC
                LIMIT 20;
            """)
            
            workflows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Convert Decimal to float for JSON serialization
            def convert_decimals(obj):
                if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
                    if isinstance(obj, dict):
                        return {k: convert_decimals(v) for k, v in obj.items()}
                    else:
                        return [convert_decimals(item) for item in obj]
                elif hasattr(obj, 'to_eng_string'):  # Decimal type
                    return float(obj)
                else:
                    return obj
            
            workflows_data = [convert_decimals(dict(w)) for w in workflows]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(workflows_data, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
    
    def generate_dashboard_html(self):
        """Generate the main dashboard HTML"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 N8N Scraper - Real-Time Dashboard</title>
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
        
        .header p {{
            font-size: 1.1em;
            color: #666;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }}
        
        .status-active {{
            background: #10b981;
        }}
        
        .status-idle {{
            background: #6b7280;
            animation: none;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-card .icon {{
            font-size: 2em;
            margin-bottom: 15px;
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .stat-card .subtitle {{
            color: #888;
            font-size: 0.85em;
        }}
        
        .progress-section {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .progress-bar {{
            background: #e5e7eb;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 15px 0;
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, #10b981, #059669);
            height: 100%;
            transition: width 0.5s ease;
            border-radius: 10px;
        }}
        
        .recent-workflows {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .workflow-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            background: #f8fafc;
            transition: background 0.3s;
            cursor: pointer;
        }}
        
        .workflow-item:hover {{
            background: #e2e8f0;
        }}
        
        .workflow-id {{
            font-weight: bold;
            color: #667eea;
            margin-right: 15px;
            min-width: 120px;
        }}
        
        .workflow-url {{
            flex: 1;
            color: #666;
            font-size: 0.9em;
        }}
        
        .workflow-quality {{
            margin-left: 15px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .quality-high {{ background: #d1fae5; color: #065f46; }}
        .quality-medium {{ background: #fef3c7; color: #92400e; }}
        .quality-low {{ background: #fee2e2; color: #991b1b; }}
        
        .status-badge {{
            margin-left: 10px;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .status-success {{ background: #d1fae5; color: #065f46; }}
        .status-partial {{ background: #fef3c7; color: #92400e; }}
        .status-error {{ background: #fee2e2; color: #991b1b; }}
        
        .current-workflow {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .current-workflow h3 {{
            margin-bottom: 10px;
        }}
        
        .current-workflow .workflow-info {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .last-update {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
            margin-top: 20px;
        }}
        
        .refresh-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            margin-left: 8px;
            animation: pulse 1s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 N8N Scraper Dashboard</h1>
            <p>Real-time monitoring and progress tracking</p>
            <p>
                <span class="status-indicator status-idle" id="status-indicator"></span>
                <span id="status-text">Checking status...</span>
            </p>
        </div>
        
        <div id="current-workflow" class="current-workflow" style="display: none;">
            <h3>🔄 Currently Processing</h3>
            <div class="workflow-info" id="current-workflow-info"></div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">Total Workflows</div>
                <div class="value" id="total-workflows">0</div>
                <div class="subtitle" id="total-subtitle">Workflows scraped</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">✅</div>
                <div class="label">Success Rate</div>
                <div class="value" id="success-rate">0%</div>
                <div class="subtitle" id="success-subtitle">Fully successful</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⭐</div>
                <div class="label">Avg Quality</div>
                <div class="value" id="avg-quality">0%</div>
                <div class="subtitle" id="quality-subtitle">Quality score</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⚡</div>
                <div class="label">Processing Speed</div>
                <div class="value" id="processing-speed">0s</div>
                <div class="subtitle" id="speed-subtitle">Average time</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🕒</div>
                <div class="label">Recent Activity</div>
                <div class="value" id="recent-activity">0</div>
                <div class="subtitle" id="recent-subtitle">Last 5 minutes</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">❌</div>
                <div class="label">Errors</div>
                <div class="value" id="error-count">0</div>
                <div class="subtitle" id="error-subtitle">With errors</div>
            </div>
        </div>
        
        <div class="progress-section">
            <h3>📈 Progress Overview</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
            <p style="text-align: center; margin-top: 10px;">
                <span id="progress-text">Loading...</span>
            </p>
        </div>
        
        <div class="recent-workflows">
            <h3>🔄 Recent Workflows</h3>
            <div id="workflows-list">
                <p style="text-align: center; color: #666;">Loading recent workflows...</p>
            </div>
        </div>
        
        <div class="last-update">
            Last updated: <span id="last-update">Never</span>
            <span class="refresh-indicator"></span>
            <br>
            Auto-refreshes every 2 seconds
        </div>
    </div>
    
    <script>
        let stats = {{}};
        
        async function updateDashboard() {{
            try {{
                const response = await fetch('/api/stats');
                stats = await response.json();
                
                // Update basic stats
                document.getElementById('total-workflows').textContent = stats.total_workflows.toLocaleString();
                document.getElementById('success-rate').textContent = stats.success_rate + '%';
                document.getElementById('avg-quality').textContent = stats.avg_quality_score + '%';
                document.getElementById('processing-speed').textContent = stats.avg_processing_time + 's';
                document.getElementById('recent-activity').textContent = stats.recent_workflows;
                document.getElementById('error-count').textContent = stats.with_errors;
                
                // Update progress bar
                const progress = (stats.fully_successful / stats.total_workflows) * 100;
                document.getElementById('progress-fill').style.width = progress + '%';
                document.getElementById('progress-text').textContent = 
                    `${{stats.fully_successful.toLocaleString()}} / ${{stats.total_workflows.toLocaleString()}} workflows successful (${{Math.round(progress)}}%)`;
                
                // Update status indicator
                const indicator = document.getElementById('status-indicator');
                const statusText = document.getElementById('status-text');
                
                if (stats.is_scraping) {{
                    indicator.className = 'status-indicator status-active';
                    statusText.textContent = 'Scraping in progress...';
                }} else {{
                    indicator.className = 'status-indicator status-idle';
                    statusText.textContent = 'Scraping idle';
                }}
                
                // Update current workflow
                const currentWorkflowDiv = document.getElementById('current-workflow');
                const currentWorkflowInfo = document.getElementById('current-workflow-info');
                
                if (stats.current_workflow) {{
                    currentWorkflowDiv.style.display = 'block';
                    currentWorkflowInfo.innerHTML = `
                        <strong>${{stats.current_workflow.workflow_id}}</strong><br>
                        ${{stats.current_workflow.url}}<br>
                        Quality: ${{stats.current_workflow.quality_score?.toFixed(1) || 'N/A'}}% | 
                        Processing: ${{stats.current_workflow.processing_time?.toFixed(2) || 'N/A'}}s
                    `;
                }} else {{
                    currentWorkflowDiv.style.display = 'none';
                }}
                
                // Update last update time
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
            }} catch (error) {{
                console.error('Error updating dashboard:', error);
            }}
        }}
        
        async function loadRecentWorkflows() {{
            try {{
                const response = await fetch('/api/recent');
                const workflows = await response.json();
                
                const listDiv = document.getElementById('workflows-list');
                
                if (workflows.length === 0) {{
                    listDiv.innerHTML = '<p style="text-align: center; color: #666;">No recent workflows found</p>';
                    return;
                }}
                
                listDiv.innerHTML = workflows.map(workflow => {{
                    const qualityClass = workflow.quality_score > 70 ? 'quality-high' : 
                                       workflow.quality_score > 40 ? 'quality-medium' : 'quality-low';
                    
                    const statusClass = workflow.layer1_success && workflow.layer2_success && workflow.layer3_success ? 'status-success' :
                                       workflow.error_message ? 'status-error' : 'status-partial';
                    
                    const statusText = workflow.layer1_success && workflow.layer2_success && workflow.layer3_success ? 'Complete' :
                                      workflow.error_message ? 'Error' : 'Partial';
                    
                    return `
                        <div class="workflow-item" onclick="showWorkflowDetails('${{workflow.workflow_id}}')">
                            <div class="workflow-id">${{workflow.workflow_id}}</div>
                            <div class="workflow-url">${{workflow.url_preview}}...</div>
                            <div class="workflow-quality ${{qualityClass}}">${{workflow.quality_score?.toFixed(1) || 'N/A'}}%</div>
                            <div class="status-badge ${{statusClass}}">${{statusText}}</div>
                        </div>
                    `;
                }}).join('');
                
            }} catch (error) {{
                console.error('Error loading recent workflows:', error);
            }}
        }}
        
        async function showWorkflowDetails(workflowId) {{
            try {{
                const response = await fetch(`/api/workflow/${{workflowId}}`);
                const details = await response.json();
                
                if (details) {{
                    // Create a modal or new window to show full details
                    const detailsWindow = window.open('', '_blank', 'width=800,height=600');
                    detailsWindow.document.write(`
                        <html>
                            <head>
                                <title>Workflow Details: ${{workflowId}}</title>
                                <style>
                                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
                                    .section {{ margin-bottom: 30px; }}
                                    .section h3 {{ color: #667eea; margin-bottom: 10px; }}
                                    pre {{ background: #f8f9fa; padding: 15px; border-radius: 8px; overflow-x: auto; }}
                                    .field {{ margin-bottom: 10px; }}
                                    .field strong {{ display: inline-block; width: 150px; }}
                                </style>
                            </head>
                            <body>
                                <h1>Workflow Details: ${{workflowId}}</h1>
                                
                                <div class="section">
                                    <h3>Basic Information</h3>
                                    <div class="field"><strong>Workflow ID:</strong> ${{details.workflow.workflow_id}}</div>
                                    <div class="field"><strong>URL:</strong> ${{details.workflow.url}}</div>
                                    <div class="field"><strong>Quality Score:</strong> ${{details.workflow.quality_score}}%</div>
                                    <div class="field"><strong>Processing Time:</strong> ${{details.workflow.processing_time}}s</div>
                                    <div class="field"><strong>Extracted At:</strong> ${{details.workflow.extracted_at}}</div>
                                </div>
                                
                                <div class="section">
                                    <h3>Processing Status</h3>
                                    <div class="field"><strong>Layer 1:</strong> ${{details.workflow.layer1_success ? '✅' : '❌'}}</div>
                                    <div class="field"><strong>Layer 2:</strong> ${{details.workflow.layer2_success ? '✅' : '❌'}}</div>
                                    <div class="field"><strong>Layer 3:</strong> ${{details.workflow.layer3_success ? '✅' : '❌'}}</div>
                                    <div class="field"><strong>Retry Count:</strong> ${{details.workflow.retry_count || 0}}</div>
                                    ${{details.workflow.error_message ? `<div class="field"><strong>Error:</strong> ${{details.workflow.error_message}}</div>` : ''}}
                                </div>
                                
                                ${{details.metadata ? `
                                <div class="section">
                                    <h3>Metadata</h3>
                                    <pre>${{JSON.stringify(details.metadata, null, 2)}}</pre>
                                </div>
                                ` : ''}}
                                
                                ${{details.structure ? `
                                <div class="section">
                                    <h3>Structure</h3>
                                    <pre>${{JSON.stringify(details.structure, null, 2)}}</pre>
                                </div>
                                ` : ''}}
                                
                                ${{details.content ? `
                                <div class="section">
                                    <h3>Content</h3>
                                    <pre>${{JSON.stringify(details.content, null, 2)}}</pre>
                                </div>
                                ` : ''}}
                            </body>
                        </html>
                    `);
                }}
            }} catch (error) {{
                console.error('Error loading workflow details:', error);
                alert('Error loading workflow details');
            }}
        }}
        
        // Initial load and set up auto-refresh
        updateDashboard();
        loadRecentWorkflows();
        
        setInterval(() => {{
            updateDashboard();
        }}, 2000); // Update stats every 2 seconds
        
        setInterval(() => {{
            loadRecentWorkflows();
        }}, 5000); // Update recent workflows every 5 seconds
    </script>
</body>
</html>
        """
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    port = 5001
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    
    print("=" * 60)
    print("🚀 N8N Scraper - Real-Time Dashboard")
    print("=" * 60)
    print(f"\n✅ Dashboard running at: http://localhost:{port}")
    print(f"✅ Database: {DB_CONFIG['database']}")
    print(f"✅ Auto-refresh: Every 2 seconds")
    print("\n📊 Features:")
    print("   • Real-time scraping progress")
    print("   • Live statistics and success rates")
    print("   • Current workflow being processed")
    print("   • Recent workflows with full details")
    print("   • Click any workflow for complete data")
    print("\n💡 Press Ctrl+C to stop the dashboard")
    print("=" * 60)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down dashboard...")
        server.shutdown()
        print("✅ Dashboard stopped")

if __name__ == '__main__':
    main()
