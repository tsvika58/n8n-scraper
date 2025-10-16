#!/usr/bin/env python3
"""
Enhanced Scrapers Monitoring Dashboard
Real-time monitoring for Layer 2 V2 and Layer 3 V3 scrapers.

Author: Dev1
Task: Enhanced L2 L3 Node Context Extraction
Date: October 15, 2025
"""

import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project paths
sys.path.append('.')
sys.path.append('../n8n-shared')

from src.storage.database import get_session
from sqlalchemy import text


class EnhancedScrapersMonitor:
    """Monitor for enhanced Layer 2 V2 and Layer 3 V3 scrapers."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.last_update = datetime.now()
        
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics from the database."""
        try:
            with get_session() as session:
                # Total workflows
                total_workflows = session.execute(text("SELECT COUNT(*) FROM workflows")).scalar()
                
                # Layer 2 V2 stats
                l2_v2_workflows = session.execute(text("""
                    SELECT COUNT(DISTINCT workflow_id) FROM workflow_node_contexts
                """)).scalar()
                
                total_node_contexts = session.execute(text("""
                    SELECT COUNT(*) FROM workflow_node_contexts
                """)).scalar()
                
                # Layer 3 V3 stats
                l3_v3_workflows = session.execute(text("""
                    SELECT COUNT(DISTINCT workflow_id) FROM workflow_standalone_docs
                """)).scalar()
                
                total_standalone_docs = session.execute(text("""
                    SELECT COUNT(*) FROM workflow_standalone_docs
                """)).scalar()
                
                # Recent activity (last 10 minutes)
                recent_time = datetime.now() - timedelta(minutes=10)
                recent_l2 = session.execute(text("""
                    SELECT COUNT(*) FROM workflow_node_contexts 
                    WHERE extracted_at > :recent_time
                """), {"recent_time": recent_time}).scalar()
                
                recent_l3 = session.execute(text("""
                    SELECT COUNT(*) FROM workflow_standalone_docs 
                    WHERE extracted_at > :recent_time
                """), {"recent_time": recent_time}).scalar()
                
                # Recent completions
                recent_completions = session.execute(text("""
                    SELECT workflow_id, extracted_at 
                    FROM workflow_node_contexts 
                    WHERE extracted_at > :recent_time
                    ORDER BY extracted_at DESC 
                    LIMIT 5
                """), {"recent_time": recent_time}).fetchall()
                
                return {
                    'total_workflows': total_workflows,
                    'l2_v2_workflows': l2_v2_workflows,
                    'total_node_contexts': total_node_contexts,
                    'l3_v3_workflows': l3_v3_workflows,
                    'total_standalone_docs': total_standalone_docs,
                    'recent_l2_activity': recent_l2,
                    'recent_l3_activity': recent_l3,
                    'recent_completions': [{'workflow_id': w_id, 'extracted_at': extracted_at} for w_id, extracted_at in recent_completions]
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'total_workflows': 0,
                'l2_v2_workflows': 0,
                'total_node_contexts': 0,
                'l3_v3_workflows': 0,
                'total_standalone_docs': 0,
                'recent_l2_activity': 0,
                'recent_l3_activity': 0,
                'recent_completions': []
            }
    
    def get_process_status(self) -> Dict[str, bool]:
        """Check if scraper processes are running."""
        import subprocess
        
        processes = {
            'layer2_v2': False,
            'layer3_v3': False,
            'test_script': False
        }
        
        try:
            # Check for running processes
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            output = result.stdout.lower()
            
            if 'layer2_enhanced_v2' in output:
                processes['layer2_v2'] = True
            if 'layer3_enhanced_v3' in output:
                processes['layer3_v3'] = True
            if 'test_enhanced_scrapers' in output:
                processes['test_script'] = True
                
        except Exception:
            pass
        
        return processes
    
    def display_dashboard(self, stats: Dict[str, Any], processes: Dict[str, bool]):
        """Display the monitoring dashboard."""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        
        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🚀 ENHANCED SCRAPERS MONITORING DASHBOARD")
        print("=" * 80)
        print(f"📅 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Uptime: {uptime}")
        print(f"🔄 Last Update: {self.last_update.strftime('%H:%M:%S')}")
        print()
        
        # Process Status
        print("🔧 PROCESS STATUS:")
        print(f"   Layer 2 V2 Scraper: {'🟢 RUNNING' if processes['layer2_v2'] else '🔴 NOT RUNNING'}")
        print(f"   Layer 3 V3 Scraper: {'🟢 RUNNING' if processes['layer3_v3'] else '🔴 NOT RUNNING'}")
        print(f"   Test Script: {'🟢 RUNNING' if processes['test_script'] else '🔴 NOT RUNNING'}")
        print()
        
        # Database Statistics
        if 'error' in stats:
            print(f"❌ Database Error: {stats['error']}")
        else:
            print("📊 DATABASE STATISTICS:")
            print(f"   Total Workflows: {stats['total_workflows']:,}")
            print()
            
            # Layer 2 V2 Progress
            l2_progress = (stats['l2_v2_workflows'] / stats['total_workflows'] * 100) if stats['total_workflows'] > 0 else 0
            print(f"📍 Layer 2 V2 (Node Contexts):")
            print(f"   Workflows Processed: {stats['l2_v2_workflows']:,} ({l2_progress:.1f}%)")
            print(f"   Total Node Contexts: {stats['total_node_contexts']:,}")
            print(f"   Recent Activity (10min): {stats['recent_l2_activity']:,}")
            print()
            
            # Layer 3 V3 Progress
            l3_progress = (stats['l3_v3_workflows'] / stats['total_workflows'] * 100) if stats['total_workflows'] > 0 else 0
            print(f"📄 Layer 3 V3 (Standalone Docs):")
            print(f"   Workflows Processed: {stats['l3_v3_workflows']:,} ({l3_progress:.1f}%)")
            print(f"   Total Standalone Docs: {stats['total_standalone_docs']:,}")
            print(f"   Recent Activity (10min): {stats['recent_l3_activity']:,}")
            print()
            
            # Recent Completions
            if stats['recent_completions']:
                print("🕒 RECENT COMPLETIONS:")
                for completion in stats['recent_completions']:
                    time_ago = current_time - completion['extracted_at']
                    print(f"   Workflow {completion['workflow_id']}: {time_ago.total_seconds():.0f}s ago")
                print()
        
        # Progress Bars
        if 'error' not in stats and stats['total_workflows'] > 0:
            print("📈 PROGRESS BARS:")
            
            # Layer 2 V2 Progress Bar
            l2_bar_length = 40
            l2_filled = int(l2_bar_length * l2_progress / 100)
            l2_bar = '█' * l2_filled + '░' * (l2_bar_length - l2_filled)
            print(f"   Layer 2 V2: [{l2_bar}] {l2_progress:.1f}%")
            
            # Layer 3 V3 Progress Bar
            l3_bar_length = 40
            l3_filled = int(l3_bar_length * l3_progress / 100)
            l3_bar = '█' * l3_filled + '░' * (l3_bar_length - l3_filled)
            print(f"   Layer 3 V3: [{l3_bar}] {l3_progress:.1f}%")
            print()
        
        print("=" * 80)
        print("Press Ctrl+C to exit")
    
    def run_monitor(self, refresh_interval: int = 5):
        """Run the monitoring dashboard."""
        print("🚀 Starting Enhanced Scrapers Monitor...")
        print(f"📊 Refresh interval: {refresh_interval} seconds")
        print("Press Ctrl+C to exit")
        time.sleep(2)
        
        try:
            while True:
                stats = self.get_database_stats()
                processes = self.get_process_status()
                self.display_dashboard(stats, processes)
                self.last_update = datetime.now()
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Enhanced Scrapers Monitor stopped by user")
        except Exception as e:
            print(f"\n\n❌ Monitor error: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Scrapers Monitoring Dashboard')
    parser.add_argument('--interval', '-i', type=int, default=5, 
                       help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    monitor = EnhancedScrapersMonitor()
    monitor.run_monitor(args.interval)


if __name__ == "__main__":
    main()

