#!/usr/bin/env python3
"""
Fresh, Simple Dashboard - No Corruption
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

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/stats':
            self.serve_stats()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 N8N Scraper Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.3);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .status {
            text-align: center;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            margin-top: 20px;
        }
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 N8N Scraper Dashboard</h1>
            <p>Real-time scraping statistics and progress</p>
        </div>
        
        <div id="loading" class="loading">
            Loading dashboard data...
        </div>
        
        <div id="dashboard" style="display: none;">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="total-workflows">0</div>
                    <div class="stat-label">Total Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="successful">0</div>
                    <div class="stat-label">Successful</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="partial">0</div>
                    <div class="stat-label">Partial Success</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="errors">0</div>
                    <div class="stat-label">With Errors</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="quality">0%</div>
                    <div class="stat-label">Avg Quality</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="speed">0s</div>
                    <div class="stat-label">Avg Speed</div>
                </div>
            </div>
            
            <div class="status">
                <h3>Status: <span id="status">Checking...</span></h3>
                <p>Last Updated: <span id="last-update">-</span></p>
            </div>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('total-workflows').textContent = stats.total_workflows.toLocaleString();
                document.getElementById('successful').textContent = stats.fully_successful.toLocaleString();
                document.getElementById('partial').textContent = stats.partial_success.toLocaleString();
                document.getElementById('errors').textContent = stats.with_errors.toLocaleString();
                document.getElementById('quality').textContent = Math.round(stats.avg_quality_score) + '%';
                document.getElementById('speed').textContent = Math.round(stats.avg_processing_time) + 's';
                document.getElementById('status').textContent = stats.is_scraping ? 'Scraping Active' : 'Idle';
                document.getElementById('last-update').textContent = new Date(stats.last_update).toLocaleTimeString();
                
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                
            } catch (error) {
                console.error('Error loading stats:', error);
                document.getElementById('loading').innerHTML = 'Error loading dashboard data';
            }
        }
        
        // Load stats immediately and every 5 seconds
        loadStats();
        setInterval(loadStats, 5000);
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get basic stats
            cursor.execute("SELECT COUNT(*) as total FROM workflows")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as successful FROM workflows WHERE quality_score > 80")
            successful = cursor.fetchone()['successful']
            
            cursor.execute("SELECT COUNT(*) as partial FROM workflows WHERE quality_score > 0 AND quality_score <= 80")
            partial = cursor.fetchone()['partial']
            
            cursor.execute("SELECT COUNT(*) as errors FROM workflows WHERE quality_score = 0 OR error_message IS NOT NULL")
            errors = cursor.fetchone()['errors']
            
            cursor.execute("SELECT AVG(quality_score) as avg_quality, AVG(processing_time) as avg_time FROM workflows WHERE quality_score > 0")
            result = cursor.fetchone()
            avg_quality = float(result['avg_quality'] or 0)
            avg_time = float(result['avg_time'] or 0)
            
            cursor.close()
            conn.close()
            
            stats = {
                'total_workflows': total,
                'fully_successful': successful,
                'partial_success': partial,
                'with_errors': errors,
                'avg_quality_score': avg_quality,
                'avg_processing_time': avg_time,
                'is_scraping': False,
                'last_update': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            self.send_error(500)

def main():
    port = 5001
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"🚀 Fresh Dashboard running on http://localhost:{port}")
    server.serve_forever()

if __name__ == '__main__':
    main()






