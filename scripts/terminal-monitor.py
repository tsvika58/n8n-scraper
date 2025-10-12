#!/usr/bin/env python3
"""
Terminal Live Monitor
Real-time monitoring in terminal with watch mode
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os
import sys
from datetime import datetime, timedelta

# Database connection
DB_CONFIG = {
    'host': 'n8n-scraper-database',
    'port': 5432,
    'database': 'n8n_scraper',
    'user': 'scraper_user',
    'password': 'scraper_pass'
}

def get_database_connection():
    """Get database connection"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def get_stats():
    """Get current statistics"""
    conn = get_database_connection()
    if not conn:
        return None
        
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
        
        # Get current workflow being processed
        cursor.execute("""
            SELECT workflow_id, url, extracted_at, quality_score
            FROM workflows 
            WHERE extracted_at > NOW() - INTERVAL '30 seconds'
            ORDER BY extracted_at DESC 
            LIMIT 1;
        """)
        
        current = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'total': stats['total_workflows'],
            'successful': stats['fully_successful'],
            'partial': stats['partial_success'],
            'errors': stats['with_errors'],
            'avg_quality': stats['avg_quality_score'],
            'avg_time': stats['avg_processing_time'],
            'recent': recent['recent_workflows'],
            'latest': stats['latest_workflow'],
            'current': dict(current) if current else None,
            'is_scraping': recent['recent_workflows'] > 0
        }
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return None

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time_ago(dt):
    """Format datetime as time ago"""
    if not dt:
        return "Never"
    
    now = datetime.now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=None)
    
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return f"{diff.seconds}s ago"

def print_header():
    """Print dashboard header"""
    print("🚀" + "=" * 58 + "🚀")
    print("   N8N SCRAPER - TERMINAL LIVE MONITOR")
    print("🚀" + "=" * 58 + "🚀")
    print()

def print_stats(stats):
    """Print current statistics"""
    if not stats:
        print("❌ Unable to get statistics")
        return
    
    # Status indicator
    status = "🟢 SCRAPING" if stats['is_scraping'] else "🔴 IDLE"
    print(f"Status: {status}")
    print()
    
    # Main stats in a nice grid
    print("📊 OVERVIEW:")
    print("┌─────────────────┬─────────────────┬─────────────────┐")
    print(f"│ Total: {stats['total']:>8,} │ Success: {stats['successful']:>6,} │ Quality: {stats['avg_quality']:>5.1f}% │")
    print(f"│ Partial: {stats['partial']:>6,} │ Errors: {stats['errors']:>8,} │ Time: {stats['avg_time']:>6.2f}s │")
    print("└─────────────────┴─────────────────┴─────────────────┘")
    print()
    
    # Recent activity
    print(f"⚡ Recent Activity: {stats['recent']} workflows in last 5 minutes")
    print(f"🕒 Last Workflow: {format_time_ago(stats['latest'])}")
    print()
    
    # Current workflow
    if stats['current']:
        current = stats['current']
        print("🔄 CURRENTLY PROCESSING:")
        print(f"   ID: {current['workflow_id']}")
        print(f"   URL: {current['url'][:60]}...")
        print(f"   Quality: {current['quality_score']:.1f}%")
        print(f"   Time: {format_time_ago(current['extracted_at'])}")
    else:
        print("🔄 Currently Processing: None")
    
    print()

def print_recent_workflows():
    """Print recent workflows"""
    conn = get_database_connection()
    if not conn:
        return
        
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                workflow_id,
                LEFT(url, 40) as url_preview,
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
        
        print("📋 RECENT WORKFLOWS:")
        print("┌──────────────┬────────────────────────────────────────┬─────────┬──────────┬──────────┐")
        print("│ Workflow ID  │ URL                                     │ Quality │ Status   │ Time     │")
        print("├──────────────┼────────────────────────────────────────┼─────────┼──────────┼──────────┤")
        
        for wf in workflows:
            status = "✅" if wf['layer1_success'] and wf['layer2_success'] and wf['layer3_success'] else "⚠️"
            quality = f"{wf['quality_score']:.1f}%" if wf['quality_score'] else "N/A"
            time_str = format_time_ago(wf['extracted_at'])
            
            print(f"│ {wf['workflow_id']:<12} │ {wf['url_preview']:<38} │ {quality:>7} │ {status:<8} │ {time_str:<8} │")
        
        print("└──────────────┴────────────────────────────────────────┴─────────┴──────────┴──────────┘")
        
    except Exception as e:
        print(f"❌ Error loading recent workflows: {e}")

def watch_mode(interval=2):
    """Watch mode with auto-refresh"""
    print(f"🔄 Watch mode active (refresh every {interval}s)")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            clear_screen()
            print_header()
            print_stats(get_stats())
            print_recent_workflows()
            print()
            print(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            print("Press Ctrl+C to stop watching")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitor...")
        print("✅ Monitor stopped")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'watch':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
            watch_mode(interval)
        elif command == 'stats':
            print_header()
            print_stats(get_stats())
        elif command == 'recent':
            print_header()
            print_recent_workflows()
        elif command == 'help':
            print("Usage:")
            print("  python terminal-monitor.py           # Show current stats once")
            print("  python terminal-monitor.py watch     # Watch mode (refresh every 2s)")
            print("  python terminal-monitor.py watch 5   # Watch mode (refresh every 5s)")
            print("  python terminal-monitor.py stats     # Show stats only")
            print("  python terminal-monitor.py recent    # Show recent workflows only")
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python terminal-monitor.py help' for usage info")
    else:
        # Default: show stats once
        print_header()
        print_stats(get_stats())

if __name__ == '__main__':
    main()
