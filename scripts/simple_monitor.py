#!/usr/bin/env python3
"""
Simple monitoring script without complex dependencies
"""

import psycopg2
import time
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

def draw_progress_bar(pct, width=40):
    """Draw a progress bar"""
    filled = int(width * pct / 100)
    return '█' * filled + '░' * (width - filled)

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

def monitor_all_layers():
    """Simple monitoring loop"""
    
    print("=" * 80)
    print("🔄 SIMPLE SCRAPING PROGRESS MONITOR")
    print("=" * 80)
    print("Monitoring all 3 layers with progress bars")
    print("Press Ctrl+C to stop")
    print("=" * 80)
    
    try:
        iteration = 0
        while True:
            iteration += 1
            now = datetime.utcnow()
            jerusalem_tz = pytz.timezone('Asia/Jerusalem')
            now_jst = now.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
            
            print(f"\n[{now_jst.strftime('%H:%M:%S')}] Update #{iteration}")
            print("─" * 80)
            
            # Get stats
            l1_5 = get_layer1_5_stats()
            l2 = get_layer2_stats()
            l3 = get_layer3_stats()
            
            # Layer 1.5
            print("\n📄 LAYER 1.5 - PAGE CONTENT EXTRACTION")
            print(f"Progress: {l1_5['completed']:,}/{l1_5['total']:,} workflows ({l1_5['pct']:.1f}%)")
            print(f"[{draw_progress_bar(l1_5['pct'])}]")
            print(f"Remaining: {l1_5['remaining']:,} workflows | Avg Content: {l1_5['avg_content']:,} chars")
            
            # Layer 2
            print("\n🔧 LAYER 2 - TECHNICAL DATA EXTRACTION")
            print(f"Progress: {l2['completed']:,}/{l2['total']:,} workflows ({l2['pct']:.1f}%)")
            print(f"[{draw_progress_bar(l2['pct'])}]")
            print(f"Remaining: {l2['remaining']:,} workflows")
            
            # Layer 3
            print("\n🎥 LAYER 3 - VIDEO & TRANSCRIPT EXTRACTION")
            print(f"Progress: {l3['completed']:,}/{l3['total']:,} workflows ({l3['pct']:.1f}%)")
            print(f"[{draw_progress_bar(l3['pct'])}]")
            print(f"Remaining: {l3['remaining']:,} workflows")
            print(f"Videos: {l3['total_videos']:,} | Transcripts: {l3['total_transcripts']:,} | Quality: {l3['avg_quality']}/100")
            
            # Overall
            total_completed = l1_5['completed'] + l2['completed'] + l3['completed']
            total_workflows = l1_5['total'] + l2['total'] + l3['total']
            overall_pct = (total_completed / total_workflows * 100) if total_workflows > 0 else 0
            
            print("\n📊 OVERALL PROGRESS")
            print(f"Total Completed: {total_completed:,}/{total_workflows:,} ({overall_pct:.1f}%)")
            print(f"[{draw_progress_bar(overall_pct)}]")
            
            print("\n" + "=" * 80)
            print("Next update in 10 seconds... (Press Ctrl+C to stop)")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        print("=" * 80)

if __name__ == "__main__":
    monitor_all_layers()


