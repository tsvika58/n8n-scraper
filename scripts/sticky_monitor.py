#!/usr/bin/env python3
"""
Sticky Monitor - Fixed bottom panel with scrolling L3 progress on top
Bottom: Overall progress, connection status, ETA
Top: L3 scraper detailed progress with live updates
"""

import psycopg2
import time
import os
import sys
from datetime import datetime, timedelta
import pytz

# Database connection
DB_URL = "postgresql://postgres.skduopoakfeaurttcaip:crg3pjm8ych4ctu%40KXT@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

def get_db_connection():
    return psycopg2.connect(DB_URL)

def format_time(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def draw_progress_bar(pct, width=50):
    """Draw a visual progress bar with colors"""
    filled = int(width * pct / 100)
    bar = '█' * filled + '░' * (width - filled)
    
    # Color coding based on progress
    if pct >= 100:
        return f"\033[92m{bar}\033[0m"  # Green
    elif pct >= 75:
        return f"\033[93m{bar}\033[0m"  # Yellow
    elif pct >= 50:
        return f"\033[94m{bar}\033[0m"  # Blue
    else:
        return f"\033[91m{bar}\033[0m"  # Red

def get_layer3_detailed_stats():
    """Get detailed Layer 3 statistics for top section"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get total workflows
        cur.execute("SELECT COUNT(*) FROM workflows")
        total_workflows = cur.fetchone()[0]
        
        # Get Layer 3 progress with detailed breakdown
        cur.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN layer3_success = true THEN 1 END) as completed,
                COUNT(CASE WHEN layer3_success = false THEN 1 END) as failed,
                COUNT(CASE WHEN layer3_success IS NULL THEN 1 END) as pending,
                COALESCE(SUM(CASE WHEN layer3_success = true THEN video_count ELSE 0 END), 0) as total_videos,
                COALESCE(SUM(CASE WHEN layer3_success = true THEN transcript_count ELSE 0 END), 0) as total_transcripts,
                COALESCE(AVG(CASE WHEN layer3_success = true THEN quality_score END), 0) as avg_quality,
                MAX(layer3_extracted_at) as last_activity
            FROM workflow_content
        """)
        result = cur.fetchone()
        
        # Get recent activity (last 5 minutes)
        cur.execute("""
            SELECT COUNT(*) FROM workflow_content 
            WHERE layer3_extracted_at > NOW() - INTERVAL '5 minutes'
        """)
        recent_activity = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        total_records = result[0]
        completed = result[1] or 0
        failed = result[2] or 0
        pending = result[3] or 0
        remaining = total_workflows - total_records
        
        return {
            'total': total_workflows,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'remaining': remaining,
            'total_videos': int(result[4]) or 0,
            'total_transcripts': int(result[5]) or 0,
            'avg_quality': int(result[6]) if result[6] else 0,
            'last_activity': result[7],
            'recent_activity': recent_activity,
            'pct': (completed / total_workflows * 100) if total_workflows > 0 else 0
        }
    except Exception as e:
        return {
            'total': 0, 'completed': 0, 'failed': 0, 'pending': 0, 'remaining': 0,
            'total_videos': 0, 'total_transcripts': 0, 'avg_quality': 0,
            'last_activity': None, 'recent_activity': 0, 'pct': 0
        }

def get_overall_stats():
    """Get overall statistics for bottom sticky panel"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Layer 1.5 stats
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer1_5_extracted_at IS NOT NULL THEN 1 END) as completed
            FROM workflow_metadata
        """)
        l1_5 = cur.fetchone()
        
        # Layer 2 stats
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer2_success = true THEN 1 END) as completed
            FROM workflows
        """)
        l2 = cur.fetchone()
        
        # Layer 3 stats
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer3_success = true THEN 1 END) as completed
            FROM workflow_content
        """)
        l3 = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            'l1_5_total': l1_5[0],
            'l1_5_completed': l1_5[1],
            'l2_total': l2[0],
            'l2_completed': l2[1],
            'l3_total': l3[0],
            'l3_completed': l3[1]
        }
    except Exception as e:
        return {
            'l1_5_total': 0, 'l1_5_completed': 0,
            'l2_total': 0, 'l2_completed': 0,
            'l3_total': 0, 'l3_completed': 0
        }

def calculate_eta(completed, total, start_time):
    """Calculate ETA based on current progress"""
    if completed == 0 or completed == total:
        return "Unknown"
    
    elapsed = time.time() - start_time
    rate = completed / elapsed  # workflows per second
    remaining = total - completed
    
    if rate > 0:
        eta_seconds = remaining / rate
        eta_time = datetime.now() + timedelta(seconds=eta_seconds)
        jerusalem_tz = pytz.timezone('Asia/Jerusalem')
        eta_jerusalem = eta_time.astimezone(jerusalem_tz)
        return eta_jerusalem.strftime('%H:%M:%S')
    return "Unknown"

def sticky_monitor():
    """Main sticky monitoring loop"""
    
    # Get terminal size
    try:
        rows, cols = os.get_terminal_size()
    except:
        rows, cols = 24, 80
    
    # Define layout
    BOTTOM_PANEL_HEIGHT = 8  # Fixed height for bottom panel
    TOP_PANEL_HEIGHT = rows - BOTTOM_PANEL_HEIGHT - 2  # Remaining space for top panel
    
    # Clear screen and setup
    os.system('clear' if os.name == 'posix' else 'cls')
    
    start_time = time.time()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            now = datetime.utcnow()
            jerusalem_tz = pytz.timezone('Asia/Jerusalem')
            now_jst = now.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
            
            # Get stats
            l3_detailed = get_layer3_detailed_stats()
            overall = get_overall_stats()
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            elapsed_str = format_time(elapsed)
            
            # Clear screen
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # TOP PANEL - L3 Detailed Progress
            print(f"\033[1;36m🎥 L3 SCRAPER DETAILED PROGRESS - {now_jst.strftime('%H:%M:%S')} Jerusalem\033[0m")
            print("\033[1;36m" + "=" * (cols-1) + "\033[0m")
            
            # L3 Progress
            status_l3 = "✅ COMPLETE" if l3_detailed['pct'] >= 100 else "🔄 ACTIVE" if l3_detailed['recent_activity'] > 0 else "⏸️  IDLE"
            eta_l3 = calculate_eta(l3_detailed['completed'], l3_detailed['total'], start_time)
            
            print(f"\033[97mProgress: {l3_detailed['completed']:,}/{l3_detailed['total']:,} ({l3_detailed['pct']:.1f}%) {status_l3}\033[0m")
            print(f"{draw_progress_bar(l3_detailed['pct'], cols-10)}")
            print(f"\033[97mRemaining: {l3_detailed['remaining']:,} | Pending: {l3_detailed['pending']:,} | Failed: {l3_detailed['failed']:,}\033[0m")
            print(f"\033[97mETA: {eta_l3} | Recent (5min): {l3_detailed['recent_activity']} workflows\033[0m")
            
            # Content Statistics
            print(f"\n\033[1;94m📊 CONTENT STATISTICS\033[0m")
            print(f"\033[97mVideos Found: {l3_detailed['total_videos']:,} | Transcripts: {l3_detailed['total_transcripts']:,} | Avg Quality: {l3_detailed['avg_quality']}/100\033[0m")
            
            if l3_detailed['last_activity']:
                last_activity_str = l3_detailed['last_activity'].strftime('%H:%M:%S')
                print(f"\033[97mLast Activity: {last_activity_str}\033[0m")
            
            # Performance metrics
            if elapsed > 0:
                rate = l3_detailed['completed'] / elapsed * 3600  # workflows per hour
                print(f"\n\033[1;93m⚡ PERFORMANCE\033[0m")
                print(f"\033[97mRate: {rate:.1f} workflows/hour | Elapsed: {elapsed_str}\033[0m")
            
            # Add some spacing to push bottom panel down
            for _ in range(TOP_PANEL_HEIGHT - 12):
                print()
            
            # BOTTOM PANEL - Sticky Overall Status
            print("\033[1;36m" + "=" * (cols-1) + "\033[0m")
            print(f"\033[1;36m📊 OVERALL SYSTEM STATUS - Update #{iteration} | Next: 3s\033[0m")
            print("\033[1;36m" + "=" * (cols-1) + "\033[0m")
            
            # Overall progress
            total_completed = overall['l1_5_completed'] + overall['l2_completed'] + overall['l3_completed']
            total_workflows = overall['l1_5_total'] + overall['l2_total'] + overall['l3_total']
            overall_pct = (total_completed / total_workflows * 100) if total_workflows > 0 else 0
            eta_overall = calculate_eta(total_completed, total_workflows, start_time)
            
            print(f"\033[97mOverall: {total_completed:,}/{total_workflows:,} ({overall_pct:.1f}%) | ETA: {eta_overall}\033[0m")
            print(f"{draw_progress_bar(overall_pct, cols-10)}")
            
            # Layer breakdown
            l1_5_pct = (overall['l1_5_completed'] / overall['l1_5_total'] * 100) if overall['l1_5_total'] > 0 else 0
            l2_pct = (overall['l2_completed'] / overall['l2_total'] * 100) if overall['l2_total'] > 0 else 0
            l3_pct = (overall['l3_completed'] / overall['l3_total'] * 100) if overall['l3_total'] > 0 else 0
            
            print(f"\033[97mL1.5: {overall['l1_5_completed']:,}/{overall['l1_5_total']:,} ({l1_5_pct:.1f}%) | L2: {overall['l2_completed']:,}/{overall['l2_total']:,} ({l2_pct:.1f}%) | L3: {overall['l3_completed']:,}/{overall['l3_total']:,} ({l3_pct:.1f}%)\033[0m")
            
            # Connection status
            try:
                conn = get_db_connection()
                conn.close()
                conn_status = "✅ Connected"
            except:
                conn_status = "❌ Disconnected"
            
            print(f"\033[97mDatabase: {conn_status} | Elapsed: {elapsed_str} | Press Ctrl+C to stop\033[0m")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n\033[92m✅ Sticky monitoring stopped\033[0m")
        print("\033[1;36m" + "=" * (cols-1) + "\033[0m")

if __name__ == "__main__":
    sticky_monitor()
