#!/usr/bin/env python3
"""
Enhanced Real-Time Scraping Dashboard
Features:
- Live scraping progress with heartbeat
- Multi-state progress bar (success/failed/scraping/pending)
- Cumulative statistics
- Recent activity feed
- CPU/Memory monitoring
- Sound alerts
- Adaptive auto-refresh
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json
import time
import psutil
import os
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

class EnhancedRealtimeDashboard:
    def __init__(self):
        self.stats = {}
        self.last_update = datetime.now()
        self.start_time = datetime.now()
        
    def get_database_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_system_metrics(self):
        """Get CPU and memory usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Get Docker container stats if available
            try:
                import subprocess
                result = subprocess.run(
                    ['docker', 'stats', 'n8n-scraper-app', '--no-stream', '--format', '{{.CPUPerc}},{{.MemUsage}}'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split(',')
                    container_cpu = float(parts[0].replace('%', ''))
                    container_mem = parts[1].split('/')[0].strip()
                    return {
                        'cpu_percent': container_cpu,
                        'memory_percent': memory.percent,
                        'memory_used': container_mem,
                        'memory_total': f"{memory.total / (1024**3):.1f}GB"
                    }
            except:
                pass
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
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
                    layer3_success
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
                    error_message,
                    CASE 
                        WHEN layer1_success AND layer2_success AND layer3_success AND quality_score > 0 
                        THEN 'success'
                        WHEN (layer1_success = false OR layer2_success = false OR layer3_success = false)
                             AND error_message IS NOT NULL AND error_message != ''
                        THEN 'failed'
                        WHEN extracted_at IS NOT NULL AND (
                             (layer1_success = false AND layer2_success = false AND layer3_success = false)
                             OR quality_score = 0
                             OR (error_message IS NULL OR error_message = '')
                        )
                        THEN 'empty'
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
                time_since_last = datetime.now() - session_stats['last_completion']
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
                    'total_errors': scraped_failed,
                    'total_empty': empty_deleted
                },
                
                'recent_activity': [
                    {
                        'workflow_id': w['workflow_id'],
                        'status': w['status'],
                        'quality_score': float(w['quality_score']) if w['quality_score'] else 0,
                        'processing_time': float(w['processing_time']) if w['processing_time'] else 0,
                        'timestamp': w['extracted_at'].isoformat() if w['extracted_at'] else None,
                        'url': w['url']
                    }
                    for w in recent_activity
                ],
                
                'database_status': {
                    'connected': True,
                    'host': DB_CONFIG['host'],
                    'total_records': total,
                    'database_size_mb': round(float(db_status['db_size'] or 0) / (1024 * 1024), 1),
                    'last_write': db_status['last_write'].isoformat() if db_status['last_write'] else None
                },
                
                'system_metrics': system_metrics
            }
            
            return self.stats
            
        except Exception as e:
            print(f"Error getting comprehensive stats: {e}")
            import traceback
            traceback.print_exc()
            return self.stats

# Global dashboard instance
dashboard = EnhancedRealtimeDashboard()

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress HTTP request logs"""
        pass
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/api/stats':
            self.serve_stats()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the enhanced dashboard HTML"""
        html = self.generate_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_stats(self):
        """Serve statistics API"""
        stats = dashboard.get_comprehensive_stats()
        
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
        
        self.wfile.write(json.dumps(stats, default=json_serial).encode('utf-8'))
    
    def generate_dashboard_html(self):
        """Generate enhanced dashboard HTML with real-time features"""
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 28px;
            color: #667eea;
        }
        
        .heartbeat-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .heartbeat {
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .heartbeat.disconnected {
            background: #f44336;
            animation: blink 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.1); }
        }
        
        @keyframes blink {
            0%, 50%, 100% { opacity: 1; }
            25%, 75% { opacity: 0.3; }
        }
        
        .status-text {
            font-weight: 600;
            color: #4CAF50;
        }
        
        .status-text.disconnected {
            color: #f44336;
        }
        
        .last-update {
            font-size: 14px;
            color: #757575;
        }
        
        .progress-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #667eea;
        }
        
        .progress-bar-container {
            margin-bottom: 20px;
        }
        
        .progress-bar {
            height: 40px;
            background: #e0e0e0;
            border-radius: 20px;
            overflow: hidden;
            display: flex;
            position: relative;
        }
        
        .progress-segment {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            transition: width 0.3s ease;
        }
        
        .progress-success {
            background: #4CAF50;
        }
        
        .progress-failed {
            background: #f44336;
        }
        
        .progress-empty {
            background: #FF9800;
        }
        
        .progress-scraping {
            background: linear-gradient(90deg, #FFC107, #FF9800);
            background-size: 200% 100%;
            animation: scanning 2s linear infinite;
        }
        
        .progress-pending {
            background: #9E9E9E;
        }
        
        @keyframes scanning {
            0% { background-position: 0% 50%; }
            100% { background-position: 100% 50%; }
        }
        
        .progress-legend {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .legend-dot {
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .stat-label {
            font-size: 14px;
            color: #757575;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-subtitle {
            font-size: 12px;
            color: #9E9E9E;
            margin-top: 5px;
        }
        
        .live-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .status-active {
            background: #4CAF50;
            color: white;
        }
        
        .status-idle {
            background: #9E9E9E;
            color: white;
        }
        
        .current-workflows {
            margin-top: 15px;
        }
        
        .live-progress-section {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            display: block !important;
            visibility: visible !important;
        }
        
        .live-progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-weight: 600;
            color: #495057;
        }
        
        .live-progress-section .progress-bar-container {
            margin-bottom: 15px;
        }
        
        .live-progress-section .progress-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }
        
        .live-progress-section .progress-bar {
            height: 20px !important;
            background: #e0e0e0 !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            display: flex !important;
        }
        
        .current-workflow-item {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .workflow-id {
            font-weight: 600;
            color: #667eea;
        }
        
        .recent-activity {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-height: 400px;
            overflow-y: auto;
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-status {
            font-size: 20px;
        }
        
        .activity-details {
            flex: 1;
        }
        
        .activity-time {
            font-size: 12px;
            color: #9E9E9E;
        }
        
        .quality-badge {
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .system-metrics {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .metric-row:last-child {
            border-bottom: none;
        }
        
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🚀 N8N Scraper - Real-Time Dashboard</h1>
            <div class="heartbeat-container">
                <div class="heartbeat" id="heartbeat"></div>
                <span class="status-text" id="status-text">● LIVE</span>
                <span class="last-update" id="last-update">Last update: --</span>
            </div>
        </div>
        
        <!-- Overall Progress -->
        <div class="progress-section">
            <div class="section-title">📊 OVERALL PROGRESS</div>
            <div class="progress-bar-container">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: 600;">Total Workflows: <span id="total-workflows">0</span></span>
                    <span style="font-weight: 600;"><span id="completion-percentage">0</span>% Complete</span>
                </div>
                <div class="progress-bar" id="progress-bar"></div>
                <div class="progress-legend">
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #4CAF50;"></div>
                        <span>Scraped Successfully: <strong id="scraped-success">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #f44336;"></div>
                        <span>Failed: <strong id="scraped-failed">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #FF9800;"></div>
                        <span>Empty/Deleted: <strong id="empty-deleted">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #FFC107;"></div>
                        <span>Currently Scraping: <strong id="currently-scraping">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #9E9E9E;"></div>
                        <span>Pending: <strong id="pending">0</strong></span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Cumulative Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value" id="success-rate">0%</div>
                <div class="stat-subtitle">Of attempted workflows</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Quality Score</div>
                <div class="stat-value" id="avg-quality">0.0</div>
                <div class="stat-subtitle">Out of 100</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Processing Time</div>
                <div class="stat-value" id="avg-time">0.0s</div>
                <div class="stat-subtitle">Per workflow</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">⚡ Processing Efficiency</div>
                <div class="stat-value" id="processing-efficiency">0%</div>
                <div class="stat-subtitle">Workflows completed</div>
            </div>
        </div>
        
        <!-- Live Scraping Status -->
        <div class="live-section">
            <div class="section-title">🔄 LIVE SCRAPING STATUS</div>
            <div id="scraping-status-badge" class="status-badge status-idle">● IDLE</div>
            <div id="scraping-details" style="font-size: 14px; color: #757575;">
                Waiting for scraping activity...
            </div>
            
            <!-- Live Scraping Progress Bar -->
            <div class="live-progress-section">
                <div class="live-progress-header">
                    <span>Live Progress</span>
                    <span id="live-progress-text">0 / 0 workflows</span>
                </div>
                <div class="progress-bar-container">
                    <div id="live-progress-bar" class="progress-bar">
                        <div class="progress-segment progress-success" style="width: 0%;"></div>
                        <div class="progress-segment progress-failed" style="width: 0%;"></div>
                        <div class="progress-segment progress-empty" style="width: 0%;"></div>
                        <div class="progress-segment progress-pending" style="width: 100%;"></div>
                    </div>
                </div>
                <div id="live-progress-legend" class="progress-legend">
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #4CAF50;"></div>
                        <span>Success: <strong id="live-success">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #F44336;"></div>
                        <span>Failed: <strong id="live-failed">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #FF9800;"></div>
                        <span>Empty/Deleted: <strong id="live-empty">0</strong></span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot" style="background: #9E9E9E;"></div>
                        <span>Pending: <strong id="live-pending">0</strong></span>
                    </div>
                </div>
            </div>
            
            <div id="current-workflows" class="current-workflows"></div>
        </div>
        
        <!-- Recent Activity -->
        <div class="recent-activity">
            <div class="section-title">🕐 RECENT ACTIVITY (Last 10 workflows)</div>
            <div id="recent-activity-list"></div>
        </div>
        
        <!-- System Metrics & Database Status -->
        <div class="system-metrics">
            <div class="section-title">💾 SYSTEM & DATABASE STATUS</div>
            <div class="metric-row">
                <span>CPU Usage</span>
                <strong id="cpu-usage">0%</strong>
            </div>
            <div class="metric-row">
                <span>Memory Usage</span>
                <strong id="memory-usage">0%</strong>
            </div>
            <div class="metric-row">
                <span>Database Connection</span>
                <strong id="db-connection">● Connected</strong>
            </div>
            <div class="metric-row">
                <span>Total Records</span>
                <strong id="total-records">0</strong>
            </div>
            <div class="metric-row">
                <span>Database Size</span>
                <strong id="db-size">0 MB</strong>
            </div>
        </div>
    </div>
    
    <!-- Sound for alerts -->
    <audio id="success-sound" preload="auto">
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuGzfLVgivAQAoQXrPo7KdWEws=" type="audio/wav">
    </audio>
    
    <script>
        let lastScrapedCount = 0;
        let refreshInterval = 5000; // Start with 5 seconds
        let isFirstLoad = true;
        
        function playSuccessSound() {
            try {
                const audio = document.getElementById('success-sound');
                audio.play().catch(e => console.log('Could not play sound:', e));
            } catch (e) {
                console.log('Sound playback error:', e);
            }
        }
        
        function updateProgressBar(data) {
            const progressBar = document.getElementById('progress-bar');
            const total = data.overall_progress.total_workflows || 1;
            const success = data.overall_progress.scraped_successfully || 0;
            const failed = data.overall_progress.scraped_failed || 0;
            const empty = data.overall_progress.empty_deleted || 0;
            const scraping = data.overall_progress.currently_scraping || 0;
            const pending = data.overall_progress.pending || 0;
            
            const successPercent = (success / total * 100);
            const failedPercent = (failed / total * 100);
            const emptyPercent = (empty / total * 100);
            const scrapingPercent = (scraping / total * 100);
            const pendingPercent = (pending / total * 100);
            
            // Always show all segments, even if 0, to maintain consistent visual structure
            progressBar.innerHTML = `
                <div class="progress-segment progress-success" style="width: ${successPercent}%">${success > 0 ? success : ''}</div>
                <div class="progress-segment progress-failed" style="width: ${failedPercent}%">${failed > 0 ? failed : ''}</div>
                <div class="progress-segment progress-empty" style="width: ${emptyPercent}%">${empty > 0 ? empty : ''}</div>
                <div class="progress-segment progress-scraping" style="width: ${scrapingPercent}%">${scraping > 0 ? scraping : ''}</div>
                <div class="progress-segment progress-pending" style="width: ${pendingPercent}%">${pending > 0 ? pending : ''}</div>
            `;
            
            // Update numbers
            document.getElementById('total-workflows').textContent = total;
            document.getElementById('completion-percentage').textContent = data.overall_progress.completion_percentage.toFixed(1);
            document.getElementById('scraped-success').textContent = success;
            document.getElementById('scraped-failed').textContent = failed;
            document.getElementById('empty-deleted').textContent = empty;
            document.getElementById('currently-scraping').textContent = scraping;
            document.getElementById('pending').textContent = pending;
            
            // Check if new workflows were scraped
            if (!isFirstLoad && success > lastScrapedCount) {
                playSuccessSound();
            }
            lastScrapedCount = success;
            isFirstLoad = false;
        }
        
        function updateDashboard() {
            fetch('/api/stats')
                .then(res => res.json())
                .then(data => {
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
                    document.getElementById('success-rate').textContent = '📈 ' + data.cumulative_stats.success_rate.toFixed(1) + '%';
                    document.getElementById('avg-quality').textContent = '⭐ ' + data.cumulative_stats.avg_quality_score.toFixed(1);
                    document.getElementById('avg-time').textContent = '⏱️ ' + data.cumulative_stats.avg_processing_time.toFixed(1) + 's';
                    document.getElementById('processing-efficiency').textContent = '⚡ ' + data.overall_progress.completion_percentage.toFixed(1) + '%';
                    
                    // Update live scraping status
                    const statusBadge = document.getElementById('scraping-status-badge');
                    const scrapingDetails = document.getElementById('scraping-details');
                    
                    if (data.live_scraping.is_active) {
                        statusBadge.className = 'status-badge status-active';
                        statusBadge.textContent = `● SCRAPING (${data.live_scraping.concurrent_count} concurrent)`;
                        
                        let detailsHTML = `
                            <div style="margin: 10px 0;">
                                <strong>Rate:</strong> ${data.live_scraping.rate_per_minute.toFixed(1)} workflows/min<br>
                                ${data.live_scraping.eta_minutes > 0 ? `<strong>ETA:</strong> ${data.live_scraping.eta_minutes.toFixed(1)} minutes remaining` : ''}
                            </div>
                        `;
                        
                        scrapingDetails.innerHTML = detailsHTML;
                        
                        // Show current workflows
                        const currentWorkflowsDiv = document.getElementById('current-workflows');
                        if (data.live_scraping.current_workflows && data.live_scraping.current_workflows.length > 0) {
                            currentWorkflowsDiv.innerHTML = data.live_scraping.current_workflows.map(w => `
                                <div class="current-workflow-item">
                                    <span class="workflow-id">#${w.workflow_id}</span> → Processing...
                                </div>
                            `).join('');
                        } else {
                            currentWorkflowsDiv.innerHTML = '';
                        }
                        
                        refreshInterval = 1000; // 1 second when scraping
                    } else {
                        statusBadge.className = 'status-badge status-idle';
                        statusBadge.textContent = '● IDLE';
                        scrapingDetails.innerHTML = 'Waiting for scraping activity...';
                        document.getElementById('current-workflows').innerHTML = '';
                        refreshInterval = 5000; // 5 seconds when idle
                    }
                    
                    // Update recent activity
                    const recentActivityList = document.getElementById('recent-activity-list');
                    if (data.recent_activity && data.recent_activity.length > 0) {
                        recentActivityList.innerHTML = data.recent_activity.map(item => {
                            let statusIcon, statusColor;
                            if (item.status === 'success') {
                                statusIcon = '✓';
                                statusColor = '#4CAF50';
                            } else if (item.status === 'failed') {
                                statusIcon = '✗';
                                statusColor = '#f44336';
                            } else if (item.status === 'empty') {
                                statusIcon = '○';
                                statusColor = '#FF9800';
                            } else {
                                statusIcon = '⚠';
                                statusColor = '#FFC107';
                            }
                            
            const timestamp = item.timestamp ? new Date(item.timestamp) : new Date();
            const secondsAgo = Math.floor((new Date() - timestamp) / 1000);
            let timeText;
            if (secondsAgo < 60) {
                timeText = `${secondsAgo}s ago`;
            } else if (secondsAgo < 3600) {
                timeText = `${Math.floor(secondsAgo / 60)}m ago`;
            } else if (secondsAgo < 86400) {
                timeText = `${Math.floor(secondsAgo / 3600)}h ago`;
            } else {
                timeText = `${Math.floor(secondsAgo / 86400)}d ago`;
            }
                            
                            return `
                                <div class="activity-item">
                                    <span class="activity-status" style="color: ${statusColor}">${statusIcon}</span>
                                    <div class="activity-details">
                                        <strong>#${item.workflow_id}</strong>
                                        ${item.processing_time > 0 ? `${item.processing_time.toFixed(1)}s` : 'Failed'}
                                        ${item.quality_score > 0 ? `<span class="quality-badge">Quality: ${item.quality_score.toFixed(0)}</span>` : ''}
                                    </div>
                                    <span class="activity-time">${timeText}</span>
                                </div>
                            `;
                        }).join('');
                    } else {
                        recentActivityList.innerHTML = '<div style="text-align: center; color: #9E9E9E; padding: 20px;">No recent activity</div>';
                    }
                    
                    // Update system metrics
                    document.getElementById('cpu-usage').textContent = data.system_metrics.cpu_percent.toFixed(1) + '%';
                    document.getElementById('memory-usage').textContent = data.system_metrics.memory_percent.toFixed(1) + '%';
                    document.getElementById('db-connection').textContent = data.database_status.connected ? '● Connected' : '○ Disconnected';
                    document.getElementById('total-records').textContent = data.database_status.total_records;
                    document.getElementById('db-size').textContent = data.database_status.database_size_mb.toFixed(1) + ' MB';
                    
                    // Update live progress bar
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
                        
                        liveProgressText.textContent = `${attemptedCount} / ${liveTotal} workflows`;
                    } else {
                        // When idle, show zeros
                        liveProgressText.textContent = `0 / 0 workflows`;
                    }
                    
                    // Update progress bar segments and legend
                    if (isCurrentlyScraping) {
                        const liveSuccessCount = data.live_scraping.current_session_success || 0;
                        const liveFailedCount = data.live_scraping.current_session_failed || 0;
                        const liveEmptyCount = data.live_scraping.current_session_empty || 0;
                        const liveTotal = data.live_scraping.current_session_total || 0;
                        const pendingCount = Math.max(0, liveTotal - (liveSuccessCount + liveFailedCount + liveEmptyCount));
                        
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
                        // When idle, show all gray (100% pending)
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
                    
                    // Schedule next update
                    setTimeout(updateDashboard, refreshInterval);
                })
                .catch(err => {
                    console.error('Connection lost:', err);
                    
                    // Show disconnected state
                    const heartbeat = document.getElementById('heartbeat');
                    const statusText = document.getElementById('status-text');
                    heartbeat.classList.add('disconnected');
                    statusText.classList.add('disconnected');
                    statusText.textContent = '○ DISCONNECTED';
                    
                    // Retry in 5 seconds
                    setTimeout(updateDashboard, 5000);
                });
        }
        
        // Start dashboard
        updateDashboard();
    </script>
</body>
</html>
        '''

def main():
    port = 5001
    print(f"🚀 Starting Enhanced Real-Time Dashboard on port {port}...")
    print(f"📊 Access at: http://localhost:{port}")
    print(f"🔄 Features:")
    print(f"   • Real-time updates (1s when scraping, 5s idle)")
    print(f"   • Heartbeat indicator with connection status")
    print(f"   • Multi-state progress bar (success/failed/scraping/pending)")
    print(f"   • CPU/Memory monitoring")
    print(f"   • Sound alerts on completion")
    print(f"   • Recent activity feed")
    print()
    
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down dashboard...")
        server.shutdown()

if __name__ == '__main__':
    main()

