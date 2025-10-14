#!/usr/bin/env python3
"""
Unified Multi-Layer Scraping Progress Monitor

Real-time monitoring of all active scraping layers
"""

import sys
sys.path.append('/app')

from src.storage.database import get_session
from sqlalchemy import text
import time
from datetime import datetime, timedelta
import pytz

def format_time(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_layer_start_time(layer_field):
    """Get the earliest extraction time for a layer"""
    with get_session() as session:
        if layer_field == 'layer1_5':
            result = session.execute(text("""
                SELECT MIN(layer1_5_extracted_at) 
                FROM workflow_metadata
                WHERE layer1_5_extracted_at IS NOT NULL
            """)).fetchone()
        else:
            result = session.execute(text("""
                SELECT MIN(updated_at) 
                FROM workflows
                WHERE layer2_success = true
            """)).fetchone()
        return result[0] if result and result[0] else datetime.utcnow()

def calculate_eta(completed, remaining, elapsed_seconds):
    """Calculate ETA and completion time in Jerusalem"""
    if completed > 0 and elapsed_seconds > 0:
        rate = completed / elapsed_seconds
        eta_seconds = remaining / rate if rate > 0 else 0
        eta_str = format_time(eta_seconds)
        
        # Calculate completion time in Jerusalem timezone
        now = datetime.utcnow()
        completion_time_utc = now + timedelta(seconds=eta_seconds)
        jerusalem_tz = pytz.timezone('Asia/Jerusalem')
        completion_time_jst = completion_time_utc.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
        eta_jst = completion_time_jst.strftime('%H:%M:%S')
        return eta_str, eta_jst
    return "--:--:--", "--:--:--"

def get_layer1_5_stats():
    """Get Layer 1.5 statistics"""
    with get_session() as session:
        result = session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer1_5_extracted_at IS NOT NULL THEN 1 END) as completed,
                COUNT(CASE WHEN layer1_5_extracted_at IS NULL THEN 1 END) as remaining,
                AVG((layer1_5_metadata->>'content_length')::int) as avg_content
            FROM workflow_metadata
        """)).fetchone()
        
        return {
            'total': result[0],
            'completed': result[1],
            'remaining': result[2],
            'avg_content': int(result[3]) if result[3] else 0,
            'pct': (result[1] / result[0] * 100) if result[0] > 0 else 0
        }

def get_layer2_stats():
    """Get Layer 2 statistics"""
    with get_session() as session:
        result = session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN layer2_success = true THEN 1 END) as completed,
                COUNT(CASE WHEN layer2_success IS NULL OR layer2_success = false THEN 1 END) as remaining
            FROM workflows
        """)).fetchone()
        
        return {
            'total': result[0],
            'completed': result[1],
            'remaining': result[2],
            'pct': (result[1] / result[0] * 100) if result[0] > 0 else 0
        }

def draw_progress_bar(pct, width=40):
    """Draw a progress bar"""
    filled = int(width * pct / 100)
    return '█' * filled + '░' * (width - filled)

def monitor_all_layers():
    """Monitor all active scraping layers"""
    
    print("\033[2J\033[H")  # Clear screen
    print("🔄 UNIFIED SCRAPING PROGRESS MONITOR")
    print("=" * 80)
    print("Monitoring Layer 1.5 (Page Content) & Layer 2 (Technical Data)")
    print("Press Ctrl+C to stop monitoring\n")
    
    l1_5_start = get_layer_start_time('layer1_5')
    l2_start = get_layer_start_time('layer2')
    
    try:
        while True:
            # Clear screen and redraw
            print("\033[2J\033[H")  # Clear screen and move to top
            
            print("🔄 UNIFIED SCRAPING PROGRESS MONITOR")
            print("=" * 80)
            
            # Get current stats
            l1_5 = get_layer1_5_stats()
            l2 = get_layer2_stats()
            
            now = datetime.utcnow()
            
            # Calculate Layer 1.5 times
            l1_5_elapsed = (now - l1_5_start).total_seconds()
            l1_5_elapsed_str = format_time(l1_5_elapsed)
            l1_5_eta_str, l1_5_eta_jst = calculate_eta(l1_5['completed'], l1_5['remaining'], l1_5_elapsed)
            
            # Calculate Layer 2 times
            l2_elapsed = (now - l2_start).total_seconds()
            l2_elapsed_str = format_time(l2_elapsed)
            l2_eta_str, l2_eta_jst = calculate_eta(l2['completed'], l2['remaining'], l2_elapsed)
            
            # Layer 1.5 Section
            print("\n📄 LAYER 1.5 - PAGE CONTENT EXTRACTION")
            print("-" * 80)
            print(f"Progress: {l1_5['completed']:,}/{l1_5['total']:,} workflows ({l1_5['pct']:.1f}%)")
            print(f"[{draw_progress_bar(l1_5['pct'])}]")
            print(f"Remaining: {l1_5['remaining']:,} workflows")
            print(f"Avg Content: {l1_5['avg_content']:,} characters")
            print(f"⏱️  Elapsed: {l1_5_elapsed_str} | ETA: {l1_5_eta_str} | Complete: {l1_5_eta_jst} Jerusalem")
            
            # Layer 2 Section
            print("\n🔧 LAYER 2 - TECHNICAL DATA EXTRACTION")
            print("-" * 80)
            print(f"Progress: {l2['completed']:,}/{l2['total']:,} workflows ({l2['pct']:.1f}%)")
            print(f"[{draw_progress_bar(l2['pct'])}]")
            print(f"Remaining: {l2['remaining']:,} workflows")
            print(f"⏱️  Elapsed: {l2_elapsed_str} | ETA: {l2_eta_str} | Complete: {l2_eta_jst} Jerusalem")
            
            # Overall Summary
            total_completed = l1_5['completed'] + l2['completed']
            total_workflows = l1_5['total'] + l2['total']
            overall_pct = (total_completed / total_workflows * 100) if total_workflows > 0 else 0
            
            print("\n📊 OVERALL PROGRESS")
            print("-" * 80)
            print(f"Total Completed: {total_completed:,}/{total_workflows:,} ({overall_pct:.1f}%)")
            print(f"[{draw_progress_bar(overall_pct)}]")
            
            # Determine which will finish first
            l1_5_finish_time = now + timedelta(seconds=(l1_5['remaining'] * l1_5_elapsed / l1_5['completed']) if l1_5['completed'] > 0 else 0)
            l2_finish_time = now + timedelta(seconds=(l2['remaining'] * l2_elapsed / l2['completed']) if l2['completed'] > 0 else 0)
            
            if l1_5['remaining'] > 0 and l2['remaining'] > 0:
                if l1_5_finish_time < l2_finish_time:
                    print(f"\n🏁 Layer 1.5 will finish first (~{l1_5_eta_str})")
                    print(f"   Layer 2 will finish ~{format_time((l2_finish_time - l1_5_finish_time).total_seconds())} later")
                else:
                    print(f"\n🏁 Layer 2 will finish first (~{l2_eta_str})")
                    print(f"   Layer 1.5 will finish ~{format_time((l1_5_finish_time - l2_finish_time).total_seconds())} later")
            
            print("\n" + "=" * 80)
            print("Updating every 5 seconds... Press Ctrl+C to stop")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        print_final_summary()

def print_final_summary():
    """Print final summary"""
    l1_5 = get_layer1_5_stats()
    l2 = get_layer2_stats()
    
    print("\n📊 FINAL STATUS SUMMARY")
    print("=" * 80)
    print(f"Layer 1.5: {l1_5['completed']:,}/{l1_5['total']:,} ({l1_5['pct']:.1f}%)")
    print(f"Layer 2:   {l2['completed']:,}/{l2['total']:,} ({l2['pct']:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    monitor_all_layers()

