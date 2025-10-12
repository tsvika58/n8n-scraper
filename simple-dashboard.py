#!/usr/bin/env python3
"""
Simple Working Dashboard - Guaranteed to work!
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n_scraper',
    'user': 'scraper_user',
    'password': 'scraper_pass'
}

def get_stats():
    """Get current statistics"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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
                MAX(extracted_at) as latest_workflow
            FROM workflows;
        """)
        
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
            'success_rate': round((stats['fully_successful'] / stats['total_workflows'] * 100), 1) if stats['total_workflows'] > 0 else 0,
            'latest_workflow': stats['latest_workflow'].isoformat() if stats['latest_workflow'] else None,
            'last_update': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            'total_workflows': 0,
            'fully_successful': 0,
            'partial_success': 0,
            'with_errors': 0,
            'avg_quality_score': 0,
            'avg_processing_time': 0,
            'success_rate': 0,
            'latest_workflow': None,
            'last_update': datetime.now().isoformat(),
            'error': str(e)
        }

def get_recent_workflows():
    """Get recent workflows"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                workflow_id,
                LEFT(url, 50) as url_preview,
                quality_score,
                layer1_success,
                layer2_success,
                layer3_success,
                extracted_at
            FROM workflows
            ORDER BY extracted_at DESC
            LIMIT 10;
        """)
        
        workflows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [
            {
                'workflow_id': w['workflow_id'],
                'url_preview': w['url_preview'],
                'quality_score': float(w['quality_score']) if w['quality_score'] else 0,
                'layer1_success': w['layer1_success'],
                'layer2_success': w['layer2_success'],
                'layer3_success': w['layer3_success'],
                'extracted_at': w['extracted_at'].isoformat() if w['extracted_at'] else None
            }
            for w in workflows
        ]
        
    except Exception as e:
        print(f"Error getting recent workflows: {e}")
        return []

class SimpleDashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/stats':
            self.serve_stats()
        elif self.path == '/api/recent':
            self.serve_recent()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 N8N Scraper Dashboard</title>
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
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
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
        
        .workflows-section {{
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
        
        .last-update {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 N8N Scraper Dashboard</h1>
            <p>Real-time monitoring and progress tracking</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">Total Workflows</div>
                <div class="value" id="total-workflows">Loading...</div>
                <div class="subtitle">Workflows scraped</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">✅</div>
                <div class="label">Success Rate</div>
                <div class="value" id="success-rate">Loading...</div>
                <div class="subtitle">Fully successful</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⭐</div>
                <div class="label">Avg Quality</div>
                <div class="value" id="avg-quality">Loading...</div>
                <div class="subtitle">Quality score</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⚡</div>
                <div class="label">Processing Speed</div>
                <div class="value" id="processing-speed">Loading...</div>
                <div class="subtitle">Average time</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">❌</div>
                <div class="label">Errors</div>
                <div class="value" id="error-count">Loading...</div>
                <div class="subtitle">With errors</div>
            </div>
        </div>
        
        <div class="workflows-section">
            <h3>🔄 Recent Workflows</h3>
            <div id="workflows-list">
                <p style="text-align: center; color: #666;">Loading recent workflows...</p>
            </div>
        </div>
        
        <div class="last-update">
            Last updated: <span id="last-update">Never</span>
            <br>
            Auto-refreshes every 5 seconds
        </div>
    </div>
    
    <script>
        async function updateDashboard() {{
            try {{
                // Update stats
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                document.getElementById('total-workflows').textContent = stats.total_workflows.toLocaleString();
                document.getElementById('success-rate').textContent = stats.success_rate + '%';
                document.getElementById('avg-quality').textContent = stats.avg_quality_score.toFixed(1) + '%';
                document.getElementById('processing-speed').textContent = stats.avg_processing_time.toFixed(1) + 's';
                document.getElementById('error-count').textContent = stats.with_errors;
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
                // Update workflows
                const workflowsResponse = await fetch('/api/recent');
                const workflows = await workflowsResponse.json();
                
                const listDiv = document.getElementById('workflows-list');
                
                if (workflows.length === 0) {{
                    listDiv.innerHTML = '<p style="text-align: center; color: #666;">No workflows found</p>';
                    return;
                }}
                
                listDiv.innerHTML = workflows.map(workflow => {{
                    const qualityClass = workflow.quality_score > 70 ? 'quality-high' : 
                                       workflow.quality_score > 40 ? 'quality-medium' : 'quality-low';
                    
                    const statusClass = workflow.layer1_success && workflow.layer2_success && workflow.layer3_success ? 'status-success' :
                                       'status-partial';
                    
                    const statusText = workflow.layer1_success && workflow.layer2_success && workflow.layer3_success ? 'Complete' : 'Partial';
                    
                    return `
                        <div class="workflow-item">
                            <div class="workflow-id">${{workflow.workflow_id}}</div>
                            <div class="workflow-url">${{workflow.url_preview}}...</div>
                            <div class="workflow-quality ${{qualityClass}}">${{workflow.quality_score.toFixed(1)}}%</div>
                            <div class="status-badge ${{statusClass}}">${{statusText}}</div>
                        </div>
                    `;
                }}).join('');
                
            }} catch (error) {{
                console.error('Error updating dashboard:', error);
                document.getElementById('total-workflows').textContent = 'Error';
                document.getElementById('success-rate').textContent = 'Error';
                document.getElementById('avg-quality').textContent = 'Error';
                document.getElementById('processing-speed').textContent = 'Error';
                document.getElementById('error-count').textContent = 'Error';
            }}
        }}
        
        // Initial load and set up auto-refresh
        updateDashboard();
        setInterval(updateDashboard, 5000); // Update every 5 seconds
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_stats(self):
        """Serve current statistics as JSON"""
        stats = get_stats()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats, indent=2).encode('utf-8'))
    
    def serve_recent(self):
        """Serve recent workflows as JSON"""
        workflows = get_recent_workflows()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(workflows, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def main():
    port = 5002
    server = HTTPServer(('0.0.0.0', port), SimpleDashboardHandler)
    
    print("=" * 60)
    print("🚀 N8N Scraper - Simple Dashboard")
    print("=" * 60)
    print(f"\n✅ Dashboard running at: http://localhost:{port}")
    print(f"✅ Database: {DB_CONFIG['database']}")
    print(f"✅ Auto-refresh: Every 5 seconds")
    print("\n📊 Features:")
    print("   • Real-time statistics")
    print("   • Recent workflows display")
    print("   • Simple and reliable")
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
