#!/usr/bin/env python3
"""
Simplified Multi-Layer Scraping Progress Monitor
For non-interactive terminals
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

def monitor_all_layers():
    """Monitor all active scraping layers"""
    
    print("=" * 80)
    print("🔄 SIMPLIFIED SCRAPING PROGRESS MONITOR")
    print("=" * 80)
    print("Updates shown with timestamps - Press Ctrl+C to stop\n")
    
    l1_5_start = get_layer_start_time('layer1_5')
    l2_start = get_layer_start_time('layer2')
    
    try:
        iteration = 0
        while True:
            iteration += 1
            now = datetime.utcnow()
            jerusalem_tz = pytz.timezone('Asia/Jerusalem')
            now_jst = now.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)
            
            # Get current stats
            l1_5 = get_layer1_5_stats()
            l2 = get_layer2_stats()
            
            # Calculate times
            l1_5_elapsed = (now - l1_5_start).total_seconds()
            l1_5_eta_str, l1_5_eta_jst = calculate_eta(l1_5['completed'], l1_5['remaining'], l1_5_elapsed)
            
            l2_elapsed = (now - l2_start).total_seconds()
            l2_eta_str, l2_eta_jst = calculate_eta(l2['completed'], l2['remaining'], l2_elapsed)
            
            total_completed = l1_5['completed'] + l2['completed']
            total_workflows = l1_5['total'] + l2['total']
            overall_pct = (total_completed / total_workflows * 100) if total_workflows > 0 else 0
            
            # Print update with timestamp
            print(f"\n[{now_jst.strftime('%H:%M:%S')}] Update #{iteration}")
            print(f"├─ Layer 1.5: {l1_5['completed']:,}/{l1_5['total']:,} ({l1_5['pct']:.1f}%) | ETA: {l1_5_eta_str} | Done: {l1_5_eta_jst}")
            print(f"├─ Layer 2:   {l2['completed']:,}/{l2['total']:,} ({l2['pct']:.1f}%) | ETA: {l2_eta_str} | Done: {l2_eta_jst}")
            print(f"└─ Overall:   {total_completed:,}/{total_workflows:,} ({overall_pct:.1f}%)")
            
            time.sleep(10)  # Update every 10 seconds
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        print_final_summary()

def print_final_summary():
    """Print final summary"""
    l1_5 = get_layer1_5_stats()
    l2 = get_layer2_stats()
    
    print("\n" + "=" * 80)
    print("📊 FINAL STATUS SUMMARY")
    print("=" * 80)
    print(f"Layer 1.5: {l1_5['completed']:,}/{l1_5['total']:,} ({l1_5['pct']:.1f}%)")
    print(f"Layer 2:   {l2['completed']:,}/{l2['total']:,} ({l2['pct']:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    monitor_all_layers()



