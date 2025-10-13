#!/usr/bin/env python3
"""
Web-based Real-time Scraping Dashboard

Provides a beautiful web interface at http://localhost:5001
showing live scraping progress with auto-refresh.
"""

import sys
sys.path.insert(0, '/app')

from flask import Flask, render_template_string
from datetime import datetime, timedelta
from sqlalchemy import text
from src.storage.database import get_session

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>n8n Scraper Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .timestamp {
            color: #666;
            font-size: 1.1em;
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
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-card .subvalue {
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .progress-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .progress-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .progress-bar-container {
            background: #f0f0f0;
            border-radius: 25px;
            height: 40px;
            overflow: hidden;
            margin-bottom: 15px;
            position: relative;
        }
        
        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            border-radius: 25px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .progress-text {
            font-size: 1.2em;
            color: #666;
            text-align: center;
            margin-top: 10px;
        }
        
        .fields-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .field-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .field-item .icon {
            font-size: 1.5em;
        }
        
        .field-item .info {
            flex: 1;
        }
        
        .field-item .name {
            font-weight: 600;
            color: #333;
            margin-bottom: 3px;
        }
        
        .field-item .count {
            color: #666;
            font-size: 0.9em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .status-active {
            background: #d4edda;
            color: #155724;
        }
        
        .status-idle {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-complete {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .refresh-notice {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }
    </style>
    <script>
        // Auto-refresh every 3 seconds
        setTimeout(function() {
            location.reload();
        }, 3000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 n8n Workflow Scraper Dashboard</h1>
            <div class="timestamp">{{ current_time }}</div>
            {% if status == 'active' %}
                <span class="status-badge status-active pulse">🟢 SCRAPING ACTIVE</span>
            {% elif status == 'complete' %}
                <span class="status-badge status-complete">✅ COMPLETE</span>
            {% else %}
                <span class="status-badge status-idle">⏸️ IDLE</span>
            {% endif %}
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📊</div>
                <div class="label">Total Workflows</div>
                <div class="value">{{ "{:,}".format(stats.total) }}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">✅</div>
                <div class="label">Scraped</div>
                <div class="value">{{ "{:,}".format(stats.scraped) }}</div>
                <div class="subvalue">{{ "%.1f"|format(stats.scraped_pct) }}% complete</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⏳</div>
                <div class="label">Remaining</div>
                <div class="value">{{ "{:,}".format(stats.remaining) }}</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">⚡</div>
                <div class="label">Recent Activity</div>
                <div class="value">{{ stats.recent }}</div>
                <div class="subvalue">Last 10 minutes</div>
            </div>
        </div>
        
        <div class="progress-section">
            <h2>📈 Overall Progress</h2>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {{ stats.scraped_pct }}%">
                    {{ "%.1f"|format(stats.scraped_pct) }}%
                </div>
            </div>
            <div class="progress-text">
                <strong>{{ "{:,}".format(stats.scraped) }}</strong> of <strong>{{ "{:,}".format(stats.total) }}</strong> workflows scraped
            </div>
            {% if stats.last_update_text %}
            <div class="progress-text" style="margin-top: 15px; color: #999;">
                🕐 Last update: {{ stats.last_update_text }}
            </div>
            {% endif %}
            {% if stats.eta %}
            <div class="progress-text" style="margin-top: 10px; color: #667eea; font-weight: bold;">
                ⏱️ Estimated time remaining: {{ stats.eta }}
            </div>
            {% endif %}
        </div>
        
        <div class="progress-section">
            <h2>📋 Field Population Status</h2>
            <div class="fields-grid">
                {% for field in fields %}
                <div class="field-item">
                    <div class="icon">{{ field.icon }}</div>
                    <div class="info">
                        <div class="name">{{ field.name }}</div>
                        <div class="count">{{ "{:,}".format(field.count) }} ({{ "%.1f"|format(field.pct) }}%)</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="refresh-notice">
            🔄 Auto-refreshing every 3 seconds...
        </div>
    </div>
</body>
</html>
"""

def get_stats():
    """Get current scraping statistics."""
    with get_session() as session:
        # Total workflows
        result = session.execute(text('SELECT COUNT(*) FROM workflows'))
        total = result.scalar()
        
        # Workflows with Layer 1 data
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflow_metadata 
            WHERE description IS NOT NULL AND description != ''
        """))
        scraped = result.scalar()
        
        # Recently updated (last 10 minutes)
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflow_metadata 
            WHERE extracted_at > NOW() - INTERVAL '10 minutes'
        """))
        recent = result.scalar()
        
        # Get last update time
        result = session.execute(text("""
            SELECT MAX(extracted_at) 
            FROM workflow_metadata 
            WHERE extracted_at IS NOT NULL
        """))
        last_update = result.scalar()
        
        # Calculate percentages
        scraped_pct = (scraped / total * 100) if total > 0 else 0
        remaining = total - scraped
        
        # Format last update
        last_update_text = None
        if last_update:
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            time_diff = datetime.now() - last_update.replace(tzinfo=None)
            
            if time_diff.total_seconds() < 60:
                last_update_text = f"{int(time_diff.total_seconds())} seconds ago"
            elif time_diff.total_seconds() < 3600:
                last_update_text = f"{int(time_diff.total_seconds()//60)} minutes ago"
            else:
                last_update_text = f"{int(time_diff.total_seconds()//3600)} hours ago"
        
        # Calculate ETA
        eta = None
        if recent > 0 and remaining > 0:
            # Estimate based on recent activity (last 10 minutes)
            rate_per_minute = recent / 10
            if rate_per_minute > 0:
                minutes_remaining = remaining / rate_per_minute
                if minutes_remaining < 60:
                    eta = f"{int(minutes_remaining)} minutes"
                else:
                    hours = int(minutes_remaining // 60)
                    mins = int(minutes_remaining % 60)
                    eta = f"{hours}h {mins}m"
        
        # Determine status
        if recent > 0:
            status = 'active'
        elif scraped >= total:
            status = 'complete'
        else:
            status = 'idle'
        
        return {
            'total': total,
            'scraped': scraped,
            'scraped_pct': scraped_pct,
            'remaining': remaining,
            'recent': recent,
            'last_update_text': last_update_text,
            'eta': eta,
            'status': status
        }

def get_field_stats(total):
    """Get field population statistics."""
    fields_config = [
        ('description', 'Description', '📝'),
        ('author_name', 'Author', '👤'),
        ('use_case', 'Use Case', '🎯'),
        ('views', 'Views', '👁️'),
        ('tags', 'Tags', '🏷️'),
        ('workflow_skill_level', 'Skill Level', '⭐'),
        ('workflow_industry', 'Industry', '🏢'),
        ('workflow_created_at', 'Created Date', '📅'),
        ('workflow_updated_at', 'Updated Date', '🔄')
    ]
    
    fields = []
    with get_session() as session:
        for field, name, icon in fields_config:
            if field == 'views':
                # Handle integer field differently
                result = session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM workflow_metadata 
                    WHERE {field} IS NOT NULL
                """))
            else:
                result = session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM workflow_metadata 
                    WHERE {field} IS NOT NULL AND {field} != ''
                """))
            count = result.scalar()
            pct = (count / total * 100) if total > 0 else 0
            
            fields.append({
                'name': name,
                'icon': icon,
                'count': count,
                'pct': pct
            })
    
    return fields

@app.route('/')
def dashboard():
    """Main dashboard route."""
    stats = get_stats()
    fields = get_field_stats(stats['total'])
    
    return render_template_string(
        HTML_TEMPLATE,
        stats=stats,
        fields=fields,
        status=stats['status'],
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

if __name__ == '__main__':
    print("🚀 Starting Web Dashboard...")
    print("📊 Dashboard available at: http://localhost:5001")
    print("🔄 Auto-refreshes every 3 seconds")
    print("\nPress Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

