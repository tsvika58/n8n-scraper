#!/usr/bin/env python3
"""
Real-Time Dashboard with WebSocket Support for Instant Updates
"""
import json
import time
import threading
import asyncio
import websockets
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import psycopg2
from psycopg2.extras import RealDictCursor
import psutil
import os
from urllib.parse import urlparse, parse_qs

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""
    pass

class RealtimeDashboard:
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.start_time = datetime.now()
        self.stats = {}
        self.clients = set()  # WebSocket clients
        self.websocket_server = None
        self.http_server = None
        
    def get_database_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(
                host="n8n-scraper-database",
                database="n8n_scraper",
                user="scraper_user",
                password="scraper_pass"
            )
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_system_metrics(self):
        """Get system CPU and memory usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            return {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_used': f"{memory.used / (1024**3):.1f}GB",
                'memory_total': f"{memory.total / (1024**3):.1f}GB"
            }
        except Exception as e:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_used': 'N/A',
                'memory_total': 'N/A'
            }
    
    def get_comprehensive_stats(self):
        """Get comprehensive statistics for the dashboard"""
        from datetime import datetime
        conn = self.get_database_connection()
        if not conn:
            return self.stats
            
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 1. Get overall progress with state distribution
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_workflows,
                    
                    -- Scraped successfully (quality > 0)
                    COUNT(*) FILTER (
                        WHERE quality_score > 0
                    ) as scraped_successfully,
                    
                    -- Failed (has error message)
                    COUNT(*) FILTER (
                        WHERE error_message IS NOT NULL
                        AND error_message != ''
                    ) as scraped_failed,
                    
                    -- Empty/Deleted (attempted but no content - we haven't found any yet)
                    0 as empty_deleted,
                    
                    -- Currently scraping (active in last 30 seconds)
                    COUNT(*) FILTER (
                        WHERE extracted_at > NOW() - INTERVAL '30 seconds'
                    ) as currently_scraping,
                    
                    -- Pending (everything else)
                    COUNT(*) FILTER (
                        WHERE quality_score IS NULL
                        AND (error_message IS NULL OR error_message = '')
                        AND extracted_at < NOW() - INTERVAL '30 seconds'
                    ) as pending,
                    
                    -- Total attempted (for completion calculation)
                    COUNT(*) FILTER (
                        WHERE extracted_at IS NOT NULL
                    ) as total_attempted,
                    
                    -- Layer success counts
                    COUNT(*) FILTER (WHERE layer1_success) as layer1_count,
                    COUNT(*) FILTER (WHERE layer2_success) as layer2_count,
                    COUNT(*) FILTER (WHERE layer3_success) as layer3_count,
                    COUNT(*) FILTER (WHERE layer4_success) as layer4_count,
                    COUNT(*) FILTER (WHERE layer5_success) as layer5_count,
                    COUNT(*) FILTER (WHERE layer6_success) as layer6_count,
                    COUNT(*) FILTER (WHERE layer7_success) as layer7_count,
                    
                    -- Cumulative stats
                    COALESCE(AVG(quality_score) FILTER (WHERE quality_score > 0), 0) as avg_quality_score,
                    COALESCE(AVG(processing_time) FILTER (WHERE processing_time > 0), 0) as avg_processing_time
                FROM workflows;
            """)
            
            overall = cursor.fetchone()
            
            # 2. Get currently scraping workflows (last 30 seconds)
            cursor.execute("""
                SELECT 
                    workflow_id,
                    url,
                    extracted_at,
                    processing_time,
                    quality_score,
                    layer1_success,
                    layer2_success,
                    layer3_success,
                    layer4_success,
                    layer5_success,
                    layer6_success,
                    layer7_success
                FROM workflows 
                WHERE extracted_at > NOW() - INTERVAL '30 seconds'
                ORDER BY extracted_at DESC 
                LIMIT 5;
            """)
            
            current_workflows = cursor.fetchall()
            
            # 2.5. Get current session stats (last 5 minutes of activity)
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE quality_score > 0) as session_success,
                    COUNT(*) FILTER (WHERE error_message IS NOT NULL AND error_message != '') as session_failed,
                    0 as session_empty,
                    COUNT(*) as session_total,
                    MAX(extracted_at) as last_completion
                FROM workflows 
                WHERE extracted_at > NOW() - INTERVAL '5 minutes';
            """)
            
            session_stats = cursor.fetchone()
            
            # 3. Get recent activity (last 10 completed workflows)
            cursor.execute("""
                SELECT 
                    workflow_id,
                    url,
                    extracted_at,
                    processing_time,
                    quality_score,
                    layer1_success,
                    layer2_success,
                    layer3_success,
                    layer4_success,
                    layer5_success,
                    layer6_success,
                    layer7_success,
                    error_message,
                    CASE 
                        WHEN quality_score > 0 THEN 'success'
                        WHEN error_message IS NOT NULL AND error_message != '' THEN 'failed'
                        WHEN extracted_at IS NOT NULL AND quality_score = 0 THEN 'empty'
                        ELSE 'partial'
                    END as status
                FROM workflows 
                WHERE extracted_at IS NOT NULL
                ORDER BY extracted_at DESC 
                LIMIT 10;
            """)
            
            recent_activity = cursor.fetchall()
            
            # 4. Calculate scraping rate (workflows per minute in last 5 minutes)
            cursor.execute("""
                SELECT 
                    COUNT(*) as recent_count,
                    EXTRACT(EPOCH FROM (MAX(extracted_at) - MIN(extracted_at))) / 60.0 as elapsed_minutes
                FROM workflows 
                WHERE extracted_at > NOW() - INTERVAL '5 minutes';
            """)
            
            rate_data = cursor.fetchone()
            
            # 5. Database status
            cursor.execute("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    MAX(extracted_at) as last_write
                FROM workflows;
            """)
            
            db_status = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            # Calculate metrics
            total = overall['total_workflows'] or 1
            scraped_successfully = overall['scraped_successfully'] or 0
            scraped_failed = overall['scraped_failed'] or 0
            empty_deleted = overall['empty_deleted'] or 0
            currently_scraping = overall['currently_scraping'] or 0
            pending = overall['pending'] or 0
            total_attempted = overall['total_attempted'] or 0
            
            # Completion = successful workflows / total workflows
            completion_percentage = (scraped_successfully / total * 100) if total > 0 else 0
            
            # Success rate = successful workflows / (successful + failed + empty) workflows
            attempted_with_results = scraped_successfully + scraped_failed + empty_deleted
            success_rate = (scraped_successfully / attempted_with_results * 100) if attempted_with_results > 0 else 0
            
            # Calculate rate and ETA
            session_total = session_stats['session_total'] or 0
            
            # Only show as "active" if:
            # 1. Currently scraping (workflows in last 30 seconds), OR
            # 2. Very recent completion (workflows in last 2 minutes)
            recent_completion = False
            if session_total > 0 and session_stats['last_completion']:
                # Parse the timestamp and check if it's within last 2 minutes
                last_completion = session_stats['last_completion']
                if isinstance(last_completion, str):
                    from datetime import datetime
                    last_completion = datetime.fromisoformat(last_completion.replace('Z', '+00:00'))
                elif hasattr(last_completion, 'replace'):
                    # Handle timezone-aware datetime
                    last_completion = last_completion.replace(tzinfo=None)
                
                time_since_last = datetime.now() - last_completion
                recent_completion = time_since_last.total_seconds() < 120  # 2 minutes
            
            is_scraping = currently_scraping > 0 or recent_completion
            
            rate_per_minute = 0
            eta_minutes = 0
            
            if is_scraping and rate_data['elapsed_minutes'] and rate_data['elapsed_minutes'] > 0:
                rate_per_minute = (rate_data['recent_count'] or 0) / rate_data['elapsed_minutes']
                if rate_per_minute > 0:
                    eta_minutes = pending / rate_per_minute
            
            # Get system metrics
            system_metrics = self.get_system_metrics()
            
            # Build comprehensive response
            self.stats = {
                'heartbeat': {
                    'timestamp': datetime.now().isoformat(),
                    'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
                    'connection_status': 'connected'
                },
                
                'overall_progress': {
                    'total_workflows': total,
                    'scraped_successfully': scraped_successfully,
                    'scraped_failed': scraped_failed,
                    'empty_deleted': empty_deleted,
                    'currently_scraping': currently_scraping,
                    'pending': pending,
                    'completion_percentage': round(completion_percentage, 1)
                },
                
                'live_scraping': {
                    'is_active': is_scraping,
                    'concurrent_count': currently_scraping,
                    'current_workflows': [dict(w) for w in current_workflows],
                    'rate_per_minute': round(rate_per_minute, 1),
                    'eta_minutes': round(eta_minutes, 1) if eta_minutes > 0 else 0,
                    # Live session data (last 5 minutes of activity)
                    'current_session_success': session_stats['session_success'] or 0,
                    'current_session_failed': session_stats['session_failed'] or 0,
                    'current_session_empty': session_stats['session_empty'] or 0,
                    'current_session_total': session_stats['session_total'] or 0
                },
                
                'cumulative_stats': {
                    'total_attempted': total_attempted,
                    'success_rate': round(success_rate, 1),
                    'avg_quality_score': round(float(overall['avg_quality_score'] or 0), 1),
                    'avg_processing_time': round(float(overall['avg_processing_time'] or 0), 1),
                    'layer1_success': overall['layer1_count'] or 0,
                    'layer2_success': overall['layer2_count'] or 0,
                    'layer3_success': overall['layer3_count'] or 0,
                    'layer4_success': overall['layer4_count'] or 0,
                    'layer5_success': overall['layer5_count'] or 0,
                    'layer6_success': overall['layer6_count'] or 0,
                    'layer7_success': overall['layer7_count'] or 0
                },
                
                'recent_activity': [dict(w) for w in recent_activity],
                
                'system_metrics': system_metrics,
                
                'database_status': {
                    'size_gb': round((db_status['db_size'] or 0) / (1024**3), 2),
                    'last_write': db_status['last_write'].isoformat() if db_status['last_write'] else None
                }
            }
            
            return self.stats
            
        except Exception as e:
            print(f"Error getting comprehensive stats: {e}")
            return self.stats
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.clients.add(websocket)
        print(f"WebSocket client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send initial data
            stats = self.get_comprehensive_stats()
            await websocket.send(json.dumps(stats, default=str))
            
            # Keep connection alive
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            print(f"WebSocket client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_update(self):
        """Broadcast update to all connected clients"""
        if self.clients:
            stats = self.get_comprehensive_stats()
            message = json.dumps(stats, default=str)
            
            # Send to all connected clients
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected
    
    def start_websocket_server(self):
        """Start WebSocket server in a separate thread"""
        async def run_websocket():
            self.websocket_server = await websockets.serve(
                self.websocket_handler, 
                self.host, 
                5002  # Different port for WebSocket
            )
            print(f"WebSocket server started on ws://{self.host}:5002")
            await self.websocket_server.wait_closed()
        
        # Run WebSocket server in a separate thread
        def run_in_thread():
            asyncio.new_event_loop().run_until_complete(run_websocket())
        
        websocket_thread = threading.Thread(target=run_in_thread, daemon=True)
        websocket_thread.start()
    
    def trigger_update(self):
        """Trigger immediate update to all connected clients"""
        if self.clients:
            # Run broadcast in a separate thread to avoid blocking
            def broadcast():
                asyncio.new_event_loop().run_until_complete(self.broadcast_update())
            
            threading.Thread(target=broadcast, daemon=True).start()

class DashboardHandler(BaseHTTPRequestHandler):
    def __init__(self, dashboard, *args, **kwargs):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/api/stats':
            self.serve_stats()
        elif self.path == '/api/trigger-update':
            # Webhook endpoint to trigger updates
            self.dashboard.trigger_update()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'update_triggered'}).encode('utf-8'))
        else:
            self.serve_dashboard()
    
    def do_POST(self):
        if self.path == '/api/trigger-update':
            # Webhook endpoint to trigger updates
            self.dashboard.trigger_update()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'update_triggered'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_HEAD(self):
        """Handle HEAD requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def serve_stats(self):
        """Serve API stats"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Convert datetime and decimal objects to JSON-serializable format
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__class__') and 'decimal' in str(obj.__class__):
                return float(obj)
            raise TypeError(f"Type {type(obj)} not serializable")
        
        stats = self.dashboard.get_comprehensive_stats()
        self.wfile.write(json.dumps(stats, default=json_serial).encode('utf-8'))
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = self.generate_dashboard_html()
        self.wfile.write(html.encode('utf-8'))
    
    def generate_dashboard_html(self):
        """Generate enhanced dashboard HTML with WebSocket support"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 N8N Scraper - Real-Time Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .heartbeat {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        
        .heartbeat.disconnected {
            background: #ef4444;
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .status-text {
            font-weight: 600;
            color: #10b981;
        }
        
        .status-text.disconnected {
            color: #ef4444;
        }
        
        .last-update {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        .section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .section h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .progress-container {
            margin-bottom: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            margin-bottom: 12px;
        }
        
        .progress-segment {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .progress-success { background: #10b981; }
        .progress-failed { background: #ef4444; }
        .progress-empty { background: #f59e0b; }
        .progress-scraping { background: #3b82f6; }
        .progress-pending { background: #6b7280; }
        
        .progress-text {
            text-align: center;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: center;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.875rem;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .stat-label {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.875rem;
        }
        
        .status-active {
            background: #dcfce7;
            color: #166534;
        }
        
        .status-idle {
            background: #f3f4f6;
            color: #374151;
        }
        
        .activity-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            gap: 12px;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        .activity-success { background: #dcfce7; color: #166534; }
        .activity-failed { background: #fef2f2; color: #dc2626; }
        .activity-empty { background: #fef3c7; color: #d97706; }
        .activity-partial { background: #dbeafe; color: #2563eb; }
        
        .activity-details {
            flex: 1;
        }
        
        .activity-workflow {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .activity-meta {
            font-size: 0.875rem;
            color: #6b7280;
        }
        
        .activity-time {
            font-size: 0.875rem;
            color: #9ca3af;
        }
        
        .websocket-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            z-index: 1000;
        }
        
        .websocket-connected {
            background: #dcfce7;
            color: #166534;
        }
        
        .websocket-disconnected {
            background: #fef2f2;
            color: #dc2626;
        }
    </style>
</head>
<body>
    <div class="websocket-status" id="websocket-status">Connecting...</div>
    
    <div class="container">
        <div class="header">
            <h1>🚀 N8N Scraper - Real-Time Dashboard</h1>
            <div class="status-indicator">
                <div class="heartbeat" id="heartbeat"></div>
                <span class="status-text" id="status-text">● LIVE</span>
                <span class="last-update" id="last-update">Last update: --</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Overall Progress</h2>
            <div class="progress-container">
                <div class="progress-text" id="progress-text">Loading...</div>
                <div class="progress-bar" id="progress-bar">
                    <div class="progress-segment progress-pending" style="width: 100%;"></div>
                </div>
                <div class="legend" id="progress-legend">
                    <div class="legend-item">
                        <div class="legend-color progress-success"></div>
                        <span>Scraped Successfully: <span id="scraped-success">0</span></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color progress-failed"></div>
                        <span>Failed: <span id="scraped-failed">0</span></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color progress-empty"></div>
                        <span>Empty/Deleted: <span id="empty-deleted">0</span></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color progress-scraping"></div>
                        <span>Currently Scraping: <span id="currently-scraping">0</span></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color progress-pending"></div>
                        <span>Pending: <span id="pending">0</span></span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="success-rate">--</div>
                <div class="stat-label">📈 Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-quality">--</div>
                <div class="stat-label">⭐ Avg Quality Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-time">--</div>
                <div class="stat-label">⏱️ Avg Processing Time</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="completion-percentage">--</div>
                <div class="stat-label">⚡ Processing Efficiency</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Live Scraping Status</h2>
            <div id="scraping-status">
                <div class="status-badge status-idle" id="scraping-status-badge">● IDLE</div>
                <div id="scraping-details">Waiting for scraping activity...</div>
                <div id="current-workflows"></div>
                
                <div class="progress-container" style="margin-top: 20px;">
                    <div class="progress-text" id="live-progress-text">0 / 0 workflows</div>
                    <div class="progress-bar" id="live-progress-bar">
                        <div class="progress-segment progress-pending" style="width: 100%;"></div>
                    </div>
                    <div class="legend" id="live-progress-legend">
                        <div class="legend-item">
                            <div class="legend-color progress-success"></div>
                            <span>Success: <span id="live-success">0</span></span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color progress-failed"></div>
                            <span>Failed: <span id="live-failed">0</span></span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color progress-empty"></div>
                            <span>Empty/Deleted: <span id="live-empty">0</span></span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color progress-pending"></div>
                            <span>Pending: <span id="live-pending">0</span></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Recent Activity (Last 10 workflows)</h2>
            <div class="activity-list" id="recent-activity-list">
                <div class="activity-item">
                    <div class="activity-icon activity-success">✓</div>
                    <div class="activity-details">
                        <div class="activity-workflow">Loading...</div>
                        <div class="activity-meta">Please wait...</div>
                    </div>
                    <div class="activity-time">--</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let websocket = null;
        let reconnectAttempts = 0;
        const maxReconnectAttempts = 5;
        
        function connectWebSocket() {
            const wsUrl = `ws://${window.location.hostname}:5001`;
            websocket = new WebSocket(wsUrl);
            
            websocket.onopen = function(event) {
                console.log('WebSocket connected');
                document.getElementById('websocket-status').textContent = 'Connected';
                document.getElementById('websocket-status').className = 'websocket-status websocket-connected';
                reconnectAttempts = 0;
            };
            
            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            websocket.onclose = function(event) {
                console.log('WebSocket disconnected');
                document.getElementById('websocket-status').textContent = 'Disconnected';
                document.getElementById('websocket-status').className = 'websocket-status websocket-disconnected';
                
                // Attempt to reconnect
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`);
                    setTimeout(connectWebSocket, 2000 * reconnectAttempts);
                }
            };
            
            websocket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            // Update heartbeat
            const heartbeat = document.getElementById('heartbeat');
            const statusText = document.getElementById('status-text');
            heartbeat.classList.remove('disconnected');
            statusText.classList.remove('disconnected');
            statusText.textContent = '● LIVE';
            
            // Update last update time
            const now = new Date();
            const lastUpdate = new Date(data.heartbeat.timestamp);
            const secondsAgo = Math.floor((now - lastUpdate) / 1000);
            let updateText;
            if (secondsAgo < 60) {
                updateText = `${secondsAgo}s ago`;
            } else if (secondsAgo < 3600) {
                updateText = `${Math.floor(secondsAgo / 60)}m ago`;
            } else if (secondsAgo < 86400) {
                updateText = `${Math.floor(secondsAgo / 3600)}h ago`;
            } else {
                updateText = `${Math.floor(secondsAgo / 86400)}d ago`;
            }
            document.getElementById('last-update').textContent = `Last update: ${updateText}`;
            
            // Update progress bar
            updateProgressBar(data);
            
            // Update cumulative stats
            updateCumulativeStats(data);
            
            // Update live scraping status
            updateLiveScrapingStatus(data);
            
            // Update recent activity
            updateRecentActivity(data);
        }
        
        function updateProgressBar(data) {
            const total = data.overall_progress.total_workflows;
            const success = data.overall_progress.scraped_successfully;
            const failed = data.overall_progress.scraped_failed;
            const empty = data.overall_progress.empty_deleted;
            const scraping = data.overall_progress.currently_scraping;
            const pending = data.overall_progress.pending;
            
            const totalAttempted = success + failed + empty + scraping;
            const completionPercentage = data.overall_progress.completion_percentage;
            
            // Update progress text
            document.getElementById('progress-text').textContent = `${completionPercentage}% Complete`;
            
            // Update progress bar
            const progressBar = document.getElementById('progress-bar');
            const successWidth = (success / total) * 100;
            const failedWidth = (failed / total) * 100;
            const emptyWidth = (empty / total) * 100;
            const scrapingWidth = (scraping / total) * 100;
            const pendingWidth = (pending / total) * 100;
            
            progressBar.innerHTML = `
                <div class="progress-segment progress-success" style="width: ${successWidth}%;"></div>
                <div class="progress-segment progress-failed" style="width: ${failedWidth}%;"></div>
                <div class="progress-segment progress-empty" style="width: ${emptyWidth}%;"></div>
                <div class="progress-segment progress-scraping" style="width: ${scrapingWidth}%;"></div>
                <div class="progress-segment progress-pending" style="width: ${pendingWidth}%;"></div>
            `;
            
            // Update numbers
            document.getElementById('total-workflows').textContent = total;
            document.getElementById('completion-percentage').textContent = completionPercentage.toFixed(1);
            document.getElementById('scraped-success').textContent = success;
            document.getElementById('scraped-failed').textContent = failed;
            document.getElementById('empty-deleted').textContent = empty;
            document.getElementById('currently-scraping').textContent = scraping;
            document.getElementById('pending').textContent = pending;
        }
        
        function updateCumulativeStats(data) {
            document.getElementById('success-rate').textContent = data.cumulative_stats.success_rate.toFixed(1) + '%';
            document.getElementById('avg-quality').textContent = data.cumulative_stats.avg_quality_score.toFixed(1);
            document.getElementById('avg-time').textContent = data.cumulative_stats.avg_processing_time.toFixed(1) + 's';
            document.getElementById('completion-percentage').textContent = data.overall_progress.completion_percentage.toFixed(1) + '%';
        }
        
        function updateLiveScrapingStatus(data) {
            const statusBadge = document.getElementById('scraping-status-badge');
            const scrapingDetails = document.getElementById('scraping-details');
            
            if (data.live_scraping.is_active) {
                statusBadge.className = 'status-badge status-active';
                statusBadge.textContent = `● SCRAPING (${data.live_scraping.concurrent_count} concurrent)`;
                
                if (data.live_scraping.rate_per_minute > 0) {
                    scrapingDetails.innerHTML = `
                        Rate: ${data.live_scraping.rate_per_minute} workflows/min
                        ${data.live_scraping.eta_minutes > 0 ? `ETA: ${data.live_scraping.eta_minutes.toFixed(1)} min` : ''}
                    `;
                } else {
                    scrapingDetails.innerHTML = 'Processing workflows...';
                }
                
                // Show current workflows
                const currentWorkflowsDiv = document.getElementById('current-workflows');
                if (data.live_scraping.current_workflows && data.live_scraping.current_workflows.length > 0) {
                    currentWorkflowsDiv.innerHTML = `
                        <div style="margin-top: 12px; font-size: 0.875rem; color: #6b7280;">
                            Currently processing: ${data.live_scraping.current_workflows.map(w => `#${w.workflow_id}`).join(', ')}
                        </div>
                    `;
                } else {
                    currentWorkflowsDiv.innerHTML = '';
                }
            } else {
                statusBadge.className = 'status-badge status-idle';
                statusBadge.textContent = '● IDLE';
                scrapingDetails.innerHTML = 'Waiting for scraping activity...';
                document.getElementById('current-workflows').innerHTML = '';
            }
            
            // Update live progress bar
            updateLiveProgressBar(data);
        }
        
        function updateLiveProgressBar(data) {
            const liveProgressText = document.getElementById('live-progress-text');
            const liveProgressBar = document.getElementById('live-progress-bar');
            const liveSuccess = document.getElementById('live-success');
            const liveFailed = document.getElementById('live-failed');
            const liveEmpty = document.getElementById('live-empty');
            const livePending = document.getElementById('live-pending');
            
            // Live progress should only show current scraping activity, not cumulative totals
            const isCurrentlyScraping = data.live_scraping.is_active;
            
            if (isCurrentlyScraping) {
                // When actively scraping, show current session progress
                const liveSuccessCount = data.live_scraping.current_session_success || 0;
                const liveFailedCount = data.live_scraping.current_session_failed || 0;
                const liveEmptyCount = data.live_scraping.current_session_empty || 0;
                const liveTotal = data.live_scraping.current_session_total || 0;
                const attemptedCount = liveSuccessCount + liveFailedCount + liveEmptyCount;
                const pendingCount = Math.max(0, liveTotal - attemptedCount);
                
                liveProgressText.textContent = `${attemptedCount} / ${liveTotal} workflows`;
                
                // Update progress bar segments
                const successWidth = liveTotal > 0 ? (liveSuccessCount / liveTotal) * 100 : 0;
                const failedWidth = liveTotal > 0 ? (liveFailedCount / liveTotal) * 100 : 0;
                const emptyWidth = liveTotal > 0 ? (liveEmptyCount / liveTotal) * 100 : 0;
                const pendingWidth = liveTotal > 0 ? (pendingCount / liveTotal) * 100 : 100;
                
                liveProgressBar.innerHTML = `
                    <div class="progress-segment progress-success" style="width: ${successWidth}%;"></div>
                    <div class="progress-segment progress-failed" style="width: ${failedWidth}%;"></div>
                    <div class="progress-segment progress-empty" style="width: ${emptyWidth}%;"></div>
                    <div class="progress-segment progress-pending" style="width: ${pendingWidth}%;"></div>
                `;
                
                // Update legend counts
                liveSuccess.textContent = liveSuccessCount;
                liveFailed.textContent = liveFailedCount;
                liveEmpty.textContent = liveEmptyCount;
                livePending.textContent = pendingCount;
            } else {
                // When idle, show empty state
                liveProgressText.textContent = `0 / 0 workflows`;
                liveProgressBar.innerHTML = `
                    <div class="progress-segment progress-success" style="width: 0%;"></div>
                    <div class="progress-segment progress-failed" style="width: 0%;"></div>
                    <div class="progress-segment progress-empty" style="width: 0%;"></div>
                    <div class="progress-segment progress-pending" style="width: 100%;"></div>
                `;
                
                // Update legend counts to zero
                liveSuccess.textContent = 0;
                liveFailed.textContent = 0;
                liveEmpty.textContent = 0;
                livePending.textContent = 0;
            }
        }
        
        function updateRecentActivity(data) {
            const recentActivityList = document.getElementById('recent-activity-list');
            if (data.recent_activity && data.recent_activity.length > 0) {
                recentActivityList.innerHTML = data.recent_activity.map(activity => {
                    const timeAgo = getTimeAgo(activity.extracted_at);
                    const statusIcon = getStatusIcon(activity.status);
                    const statusClass = getStatusClass(activity.status);
                    
                    return `
                        <div class="activity-item">
                            <div class="activity-icon ${statusClass}">${statusIcon}</div>
                            <div class="activity-details">
                                <div class="activity-workflow">#${activity.workflow_id}</div>
                                <div class="activity-meta">
                                    ${activity.processing_time ? activity.processing_time.toFixed(1) + 's' : '--'} 
                                    ${activity.quality_score ? 'Quality: ' + activity.quality_score.toFixed(0) : ''}
                                </div>
                            </div>
                            <div class="activity-time">${timeAgo}</div>
                        </div>
                    `;
                }).join('');
            } else {
                recentActivityList.innerHTML = '<div class="activity-item"><div class="activity-details">No recent activity</div></div>';
            }
        }
        
        function getTimeAgo(timestamp) {
            const now = new Date();
            const time = new Date(timestamp);
            const diffMs = now - time;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            return `${diffDays}d ago`;
        }
        
        function getStatusIcon(status) {
            switch (status) {
                case 'success': return '✓';
                case 'failed': return '✗';
                case 'empty': return '○';
                case 'partial': return '◐';
                default: return '?';
            }
        }
        
        function getStatusClass(status) {
            switch (status) {
                case 'success': return 'activity-success';
                case 'failed': return 'activity-failed';
                case 'empty': return 'activity-empty';
                case 'partial': return 'activity-partial';
                default: return 'activity-partial';
            }
        }
        
        // Fallback polling function
        function startPolling() {
            console.log('Starting polling fallback...');
            setInterval(async () => {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    updateDashboard(data);
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000); // Poll every 2 seconds
        }
        
        // Try WebSocket first, fallback to polling
        setTimeout(() => {
            if (!websocket || websocket.readyState !== WebSocket.OPEN) {
                console.log('WebSocket failed, starting polling fallback');
                startPolling();
            }
        }, 3000);
        
        // Connect WebSocket on page load
        connectWebSocket();
    </script>
</body>
</html>
        '''

def create_handler(dashboard):
    """Create handler with dashboard instance"""
    def handler(*args, **kwargs):
        return DashboardHandler(dashboard, *args, **kwargs)
    return handler

def main():
    print("🚀 Starting Enhanced Real-Time Dashboard with WebSocket Support...")
    print(f"📊 HTTP Server: http://localhost:5001")
    print(f"🔌 WebSocket Server: ws://localhost:5002")
    print("🔄 Features:")
    print("   • Real-time updates via WebSocket")
    print("   • Webhook endpoint for instant updates")
    print("   • Heartbeat indicator with connection status")
    print("   • Multi-state progress bar (success/failed/scraping/pending)")
    print("   • CPU/Memory monitoring")
    print("   • Recent activity feed")
    
    dashboard = RealtimeDashboard()
    
    # Start WebSocket server
    dashboard.start_websocket_server()
    
    # Start HTTP server
    handler = create_handler(dashboard)
    httpd = ThreadedHTTPServer(('0.0.0.0', 5001), handler)
    
    print(f"\n✅ Dashboard running on http://localhost:5001")
    print(f"✅ WebSocket running on ws://localhost:5002")
    print(f"✅ Webhook endpoint: http://localhost:5001/api/trigger-update")
    print("\nPress Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard...")
        httpd.shutdown()

if __name__ == "__main__":
    main()
