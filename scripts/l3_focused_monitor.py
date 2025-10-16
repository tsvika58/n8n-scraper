#!/usr/bin/env python3
"""
L3 Focused Monitor - Only Layer 3 with elapsed time and ETA in Jerusalem
"""

import psycopg2
import time
import os
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

def get_l3_stats():
    """Get Layer 3 statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get total workflows
        cur.execute("SELECT COUNT(*) FROM workflows")
        total_workflows = cur.fetchone()[0]
        
        # Get Layer 3 progress
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
        
        # Get recent activity (last 1 minute)
        cur.execute("""
            SELECT COUNT(*) FROM workflow_content 
            WHERE layer3_extracted_at > NOW() - INTERVAL '1 minute'
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

def l3_focused_monitor():
    """L3 focused monitoring loop"""
    
    # Clear screen and setup
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\033[1;36m" + "=" * 80 + "\033[0m")
    print("\033[1;36m🎥 L3 SCRAPER FOCUSED MONITOR\033[0m")
    print("\033[1;36m" + "=" * 80 + "\033[0m")
    print("\033[93m📊 Updates: Every 3 seconds | 🌍 Timezone: Jerusalem\033[0m")
    print("\033[93m🎯 Focus: Layer 3 only with elapsed time and ETA\033[0m")
    print("\033[93mPress Ctrl+C to stop monitoring\033[0m")
    print("\033[1;36m" + "=" * 80 + "\033[0m")
    
    start_time = time.time()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            now = datetime.utcnow()
            jerusalem_tz = pytz.timezone('Asia/Jerusalem')
            now_jst = now.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
            
            # Get L3 stats
            l3 = get_l3_stats()
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            elapsed_str = format_time(elapsed)
            
            # Clear screen and move to top
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Header
            print("\033[1;36m" + "=" * 80 + "\033[0m")
            print(f"\033[1;36m🎥 L3 SCRAPER FOCUSED MONITOR - {now_jst.strftime('%H:%M:%S')} Jerusalem\033[0m")
            print("\033[1;36m" + "=" * 80 + "\033[0m")
            print(f"\033[93m⏱️  Elapsed: {elapsed_str} | Update #{iteration} | Next: 3s\033[0m")
            print("\033[1;36m" + "=" * 80 + "\033[0m")
            
            # L3 Progress
            eta_l3 = calculate_eta(l3['completed'], l3['total'], start_time)
            status_l3 = "✅ COMPLETE" if l3['pct'] >= 100 else "🔄 ACTIVE" if l3['recent_activity'] > 0 else "⏸️  IDLE"
            
            print(f"\n\033[1;94m🎥 LAYER 3 - VIDEO & TRANSCRIPT EXTRACTION\033[0m")
            print(f"\033[97mProgress: {l3['completed']:,}/{l3['total']:,} ({l3['pct']:.1f}%) {status_l3}\033[0m")
            print(f"{draw_progress_bar(l3['pct'])}")
            print(f"\033[97mRemaining: {l3['remaining']:,} | Pending: {l3['pending']:,} | Failed: {l3['failed']:,}\033[0m")
            print(f"\033[97mETA: {eta_l3} Jerusalem | Recent (1min): {l3['recent_activity']} workflows\033[0m")
            
            # Content Statistics
            print(f"\n\033[1;94m📊 CONTENT STATISTICS\033[0m")
            print(f"\033[97mVideos Found: {l3['total_videos']:,} | Transcripts: {l3['total_transcripts']:,} | Avg Quality: {l3['avg_quality']}/100\033[0m")
            
            if l3['last_activity']:
                last_activity_str = l3['last_activity'].strftime('%H:%M:%S')
                print(f"\033[97mLast Activity: {last_activity_str}\033[0m")
            
            # Performance metrics
            if elapsed > 0:
                rate = l3['completed'] / elapsed * 3600  # workflows per hour
                print(f"\n\033[1;93m⚡ PERFORMANCE\033[0m")
                print(f"\033[97mRate: {rate:.1f} workflows/hour | Elapsed: {elapsed_str}\033[0m")
                
                # Activity indicators
                if l3['recent_activity'] > 0:
                    print(f"\033[92m🔥 ACTIVE: {l3['recent_activity']} workflows processed in last minute\033[0m")
                else:
                    print(f"\033[91m⚠️  NO ACTIVITY: No workflows processed in last minute\033[0m")
            
            print("\n" + "\033[1;36m" + "=" * 80 + "\033[0m")
            print("\033[93mNext update in 3 seconds... (Press Ctrl+C to stop)\033[0m")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n\033[92m✅ L3 monitoring stopped\033[0m")
        print("\033[1;36m" + "=" * 80 + "\033[0m")

if __name__ == "__main__":
    l3_focused_monitor()

