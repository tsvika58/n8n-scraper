#!/usr/bin/env python3
"""
Visual Terminal Monitor - Real-time scraping feedback
Shows all layers with progress bars, live updates, and visual feedback
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

def get_layer1_5_stats():
    """Get Layer 1.5 statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer1_5_extracted_at IS NOT NULL THEN 1 END) as completed,
                COUNT(CASE WHEN layer1_5_extracted_at IS NULL THEN 1 END) as remaining,
                AVG((layer1_5_metadata->>'content_length')::int) as avg_content
            FROM workflow_metadata
        """)
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return {
            'total': result[0],
            'completed': result[1],
            'remaining': result[2],
            'avg_content': int(result[3]) if result[3] else 0,
            'pct': (result[1] / result[0] * 100) if result[0] > 0 else 0
        }
    except Exception as e:
        return {'total': 0, 'completed': 0, 'remaining': 0, 'avg_content': 0, 'pct': 0}

def get_layer2_stats():
    """Get Layer 2 statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer2_success = true THEN 1 END) as completed,
                COUNT(CASE WHEN layer2_success IS NULL OR layer2_success = false THEN 1 END) as remaining
            FROM workflows
        """)
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return {
            'total': result[0],
            'completed': result[1],
            'remaining': result[2],
            'pct': (result[1] / result[0] * 100) if result[0] > 0 else 0
        }
    except Exception as e:
        return {'total': 0, 'completed': 0, 'remaining': 0, 'pct': 0}

def get_layer3_stats():
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
                COALESCE(SUM(CASE WHEN layer3_success = true THEN video_count ELSE 0 END), 0) as total_videos,
                COALESCE(SUM(CASE WHEN layer3_success = true THEN transcript_count ELSE 0 END), 0) as total_transcripts,
                COALESCE(AVG(CASE WHEN layer3_success = true THEN quality_score END), 0) as avg_quality
            FROM workflow_content
        """)
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        total_records = result[0]
        completed = result[1] or 0
        remaining = total_workflows - total_records
        
        return {
            'total': total_workflows,
            'completed': completed,
            'remaining': remaining,
            'total_videos': int(result[2]) or 0,
            'total_transcripts': int(result[3]) or 0,
            'avg_quality': int(result[4]) if result[4] else 0,
            'pct': (completed / total_workflows * 100) if total_workflows > 0 else 0
        }
    except Exception as e:
        return {'total': 0, 'completed': 0, 'remaining': 0, 'total_videos': 0, 'total_transcripts': 0, 'avg_quality': 0, 'pct': 0}

def get_recent_activity():
    """Get recent scraping activity"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check recent Layer 1.5 activity
        cur.execute("""
            SELECT COUNT(*) FROM workflow_metadata 
            WHERE layer1_5_extracted_at > NOW() - INTERVAL '1 minute'
        """)
        l1_5_recent = cur.fetchone()[0]
        
        # Check recent Layer 2 activity
        cur.execute("""
            SELECT COUNT(*) FROM workflows 
            WHERE updated_at > NOW() - INTERVAL '1 minute' AND layer2_success = true
        """)
        l2_recent = cur.fetchone()[0]
        
        # Check recent Layer 3 activity
        cur.execute("""
            SELECT COUNT(*) FROM workflow_content 
            WHERE layer3_extracted_at > NOW() - INTERVAL '1 minute'
        """)
        l3_recent = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {
            'l1_5_recent': l1_5_recent,
            'l2_recent': l2_recent,
            'l3_recent': l3_recent
        }
    except Exception as e:
        return {'l1_5_recent': 0, 'l2_recent': 0, 'l3_recent': 0}

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

def visual_monitor():
    """Main visual monitoring loop with 3-second updates"""
    
    # Clear screen and setup
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("\033[1;36m" + "=" * 80 + "\033[0m")
    print("\033[1;36m🚀 VISUAL TERMINAL SCRAPER MONITOR - REAL-TIME FEEDBACK\033[0m")
    print("\033[1;36m" + "=" * 80 + "\033[0m")
    print("\033[93m📊 Updates: Every 3 seconds | 🌍 Timezone: Jerusalem\033[0m")
    print("\033[93m🎯 Features: Progress bars, live activity, ETA calculations\033[0m")
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
            
            # Get stats
            l1_5 = get_layer1_5_stats()
            l2 = get_layer2_stats()
            l3 = get_layer3_stats()
            recent = get_recent_activity()
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            elapsed_str = format_time(elapsed)
            
            # Clear screen and move to top
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Header
            print("\033[1;36m" + "=" * 80 + "\033[0m")
            print(f"\033[1;36m🚀 VISUAL TERMINAL SCRAPER MONITOR - {now_jst.strftime('%H:%M:%S')} Jerusalem\033[0m")
            print("\033[1;36m" + "=" * 80 + "\033[0m")
            print(f"\033[93m⏱️  Elapsed: {elapsed_str} | Update #{iteration} | Next: 3s\033[0m")
            print("\033[1;36m" + "=" * 80 + "\033[0m")
            
            # Layer 1.5
            eta_l1_5 = calculate_eta(l1_5['completed'], l1_5['total'], start_time)
            status_l1_5 = "✅ COMPLETE" if l1_5['pct'] >= 100 else "🔄 ACTIVE" if recent['l1_5_recent'] > 0 else "⏸️  IDLE"
            
            print(f"\n\033[1;94m📄 LAYER 1.5 - PAGE CONTENT EXTRACTION\033[0m")
            print(f"\033[97mProgress: {l1_5['completed']:,}/{l1_5['total']:,} ({l1_5['pct']:.1f}%) {status_l1_5}\033[0m")
            print(f"{draw_progress_bar(l1_5['pct'])}")
            print(f"\033[97mRemaining: {l1_5['remaining']:,} | Avg: {l1_5['avg_content']:,} chars | ETA: {eta_l1_5}\033[0m")
            print(f"\033[97mRecent (1min): {recent['l1_5_recent']} workflows\033[0m")
            
            # Layer 2
            eta_l2 = calculate_eta(l2['completed'], l2['total'], start_time)
            status_l2 = "✅ COMPLETE" if l2['pct'] >= 100 else "🔄 ACTIVE" if recent['l2_recent'] > 0 else "⏸️  IDLE"
            
            print(f"\n\033[1;94m🔧 LAYER 2 - TECHNICAL DATA EXTRACTION\033[0m")
            print(f"\033[97mProgress: {l2['completed']:,}/{l2['total']:,} ({l2['pct']:.1f}%) {status_l2}\033[0m")
            print(f"{draw_progress_bar(l2['pct'])}")
            print(f"\033[97mRemaining: {l2['remaining']:,} | ETA: {eta_l2}\033[0m")
            print(f"\033[97mRecent (1min): {recent['l2_recent']} workflows\033[0m")
            
            # Layer 3
            eta_l3 = calculate_eta(l3['completed'], l3['total'], start_time)
            status_l3 = "✅ COMPLETE" if l3['pct'] >= 100 else "🔄 ACTIVE" if recent['l3_recent'] > 0 else "⏸️  IDLE"
            
            print(f"\n\033[1;94m🎥 LAYER 3 - VIDEO & TRANSCRIPT EXTRACTION\033[0m")
            print(f"\033[97mProgress: {l3['completed']:,}/{l3['total']:,} ({l3['pct']:.1f}%) {status_l3}\033[0m")
            print(f"{draw_progress_bar(l3['pct'])}")
            print(f"\033[97mRemaining: {l3['remaining']:,} | ETA: {eta_l3}\033[0m")
            print(f"\033[97mVideos: {l3['total_videos']:,} | Transcripts: {l3['total_transcripts']:,} | Quality: {l3['avg_quality']}/100\033[0m")
            print(f"\033[97mRecent (1min): {recent['l3_recent']} workflows\033[0m")
            
            # Overall
            total_completed = l1_5['completed'] + l2['completed'] + l3['completed']
            total_workflows = l1_5['total'] + l2['total'] + l3['total']
            overall_pct = (total_completed / total_workflows * 100) if total_workflows > 0 else 0
            eta_overall = calculate_eta(total_completed, total_workflows, start_time)
            
            print(f"\n\033[1;95m📊 OVERALL PROGRESS\033[0m")
            print(f"\033[97mTotal: {total_completed:,}/{total_workflows:,} ({overall_pct:.1f}%)\033[0m")
            print(f"{draw_progress_bar(overall_pct)}")
            print(f"\033[97mETA: {eta_overall} Jerusalem\033[0m")
            
            # Performance metrics
            if elapsed > 0:
                rate = total_completed / elapsed * 3600  # workflows per hour
                success_rate = (total_completed / total_workflows * 100) if total_workflows > 0 else 0
                
                print(f"\n\033[1;93m⚡ PERFORMANCE METRICS\033[0m")
                print(f"\033[97mRate: {rate:.1f} workflows/hour\033[0m")
                print(f"\033[97mSuccess Rate: {success_rate:.1f}%\033[0m")
                
                # Activity indicators
                total_recent = recent['l1_5_recent'] + recent['l2_recent'] + recent['l3_recent']
                if total_recent > 0:
                    print(f"\033[92m🔥 ACTIVE: {total_recent} workflows processed in last minute\033[0m")
                else:
                    print(f"\033[91m⚠️  NO ACTIVITY: No workflows processed in last minute\033[0m")
            
            print("\n" + "\033[1;36m" + "=" * 80 + "\033[0m")
            print("\033[93mNext update in 3 seconds... (Press Ctrl+C to stop)\033[0m")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n\033[92m✅ Visual monitoring stopped\033[0m")
        print("\033[1;36m" + "=" * 80 + "\033[0m")

if __name__ == "__main__":
    visual_monitor()

