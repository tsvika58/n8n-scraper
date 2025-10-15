#!/usr/bin/env python3
"""
Layer 1 Scraping Real-time Dashboard

Shows live progress with visual indicators and statistics.
"""

import sys
sys.path.insert(0, '/app')

import time
import os
from datetime import datetime, timedelta
from sqlalchemy import text
from src.storage.database import get_session

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

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
        
        # Workflows with complete Layer 1 data
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflow_metadata 
            WHERE description IS NOT NULL 
            AND description != ''
            AND author_name IS NOT NULL
            AND use_case IS NOT NULL
            AND workflow_skill_level IS NOT NULL
        """))
        complete = result.scalar()
        
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
        
        return {
            'total': total,
            'scraped': scraped,
            'complete': complete,
            'recent': recent,
            'remaining': total - scraped,
            'last_update': last_update
        }

def print_progress_bar(current, total, width=50):
    """Print a visual progress bar."""
    if total == 0:
        return "[" + "░" * width + "] 0.0%"
    
    pct = current / total
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct*100:.1f}%"

def format_duration(seconds):
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds//60)}m {int(seconds%60)}s"
    else:
        return f"{int(seconds//3600)}h {int((seconds%3600)//60)}m"

def main():
    """Main dashboard loop."""
    print("🚀 Starting Layer 1 Scraping Dashboard...")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            # Get current stats
            stats = get_stats()
            
            # Header
            print("=" * 80)
            print("🔍 LAYER 1 SCRAPING DASHBOARD")
            print("=" * 80)
            print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Progress section
            print("📊 PROGRESS OVERVIEW")
            print("-" * 40)
            progress_bar = print_progress_bar(stats['scraped'], stats['total'])
            print(f"Overall Progress: {progress_bar}")
            print(f"Workflows Scraped: {stats['scraped']:,} / {stats['total']:,}")
            print(f"Remaining: {stats['remaining']:,}")
            print()
            
            # Status indicators
            print("📈 STATUS INDICATORS")
            print("-" * 40)
            
            # Completion status
            if stats['complete'] > 0:
                complete_pct = (stats['complete'] / stats['total']) * 100
                print(f"✅ Complete Data: {stats['complete']:,} ({complete_pct:.1f}%)")
            else:
                print("⏳ Complete Data: 0 (0.0%)")
            
            # Recent activity
            if stats['recent'] > 0:
                print(f"🔄 Recent Activity: {stats['recent']} workflows in last 10 minutes")
            else:
                print("⏸️  Recent Activity: No activity in last 10 minutes")
            
            # Last update
            if stats['last_update']:
                last_update_dt = stats['last_update']
                if isinstance(last_update_dt, str):
                    last_update_dt = datetime.fromisoformat(last_update_dt.replace('Z', '+00:00'))
                
                time_diff = datetime.now() - last_update_dt.replace(tzinfo=None)
                if time_diff.total_seconds() < 60:
                    print(f"🕐 Last Update: {int(time_diff.total_seconds())} seconds ago")
                elif time_diff.total_seconds() < 3600:
                    print(f"🕐 Last Update: {int(time_diff.total_seconds()//60)} minutes ago")
                else:
                    print(f"🕐 Last Update: {int(time_diff.total_seconds()//3600)} hours ago")
            else:
                print("🕐 Last Update: Never")
            
            print()
            
            # Field population status
            print("📋 FIELD POPULATION STATUS")
            print("-" * 40)
            
            with get_session() as session:
                # Check key fields
                fields = [
                    ('description', 'Description'),
                    ('author_name', 'Author'),
                    ('use_case', 'Use Case'),
                    ('views', 'Views'),
                    ('tags', 'Tags'),
                    ('workflow_skill_level', 'Skill Level'),
                    ('workflow_industry', 'Industry'),
                    ('workflow_created_at', 'Created Date'),
                    ('workflow_updated_at', 'Updated Date')
                ]
                
                for field, name in fields:
                    result = session.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM workflow_metadata 
                        WHERE {field} IS NOT NULL AND {field} != ''
                    """))
                    count = result.scalar()
                    pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
                    
                    if pct == 100:
                        status = "✅"
                    elif pct >= 50:
                        status = "🟡"
                    elif pct > 0:
                        status = "🟠"
                    else:
                        status = "❌"
                    
                    print(f"{status} {name:<15}: {count:>5,} ({pct:>5.1f}%)")
            
            print()
            
            # Instructions
            print("💡 INSTRUCTIONS")
            print("-" * 40)
            print("• This dashboard updates every 5 seconds")
            print("• Press Ctrl+C to stop monitoring")
            print("• Check terminal logs for detailed scraping progress")
            print()
            
            # Footer
            print("=" * 80)
            print("🔄 Refreshing in 5 seconds... (Ctrl+C to stop)")
            
            # Check if scraping is complete
            if stats['scraped'] >= stats['total']:
                print("\n🎉 SCRAPING COMPLETE! All workflows have been processed.")
                break
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Dashboard stopped by user")
        print(f"\nFinal status: {stats['scraped']}/{stats['total']} workflows scraped")

if __name__ == "__main__":
    main()


