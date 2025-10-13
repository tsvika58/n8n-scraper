#!/usr/bin/env python3
"""
Monitor Layer 1 Scraping Progress

Shows real-time statistics on scraping progress.
"""

import sys
sys.path.insert(0, '/app')

import time
from sqlalchemy import text
from src.storage.database import get_session

def get_stats():
    """Get current scraping statistics."""
    with get_session() as session:
        # Total workflows
        result = session.execute(text('SELECT COUNT(*) FROM workflows'))
        total = result.scalar()
        
        # Workflows with Layer 1 data (description populated)
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflow_metadata 
            WHERE description IS NOT NULL AND description != ''
        """))
        scraped = result.scalar()
        
        # Workflows with all key Layer 1 fields
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflow_metadata 
            WHERE description IS NOT NULL 
            AND description != ''
            AND author_name IS NOT NULL
            AND use_case IS NOT NULL
        """))
        complete = result.scalar()
        
        # Recently updated (last 5 minutes)
        result = session.execute(text("""
            SELECT COUNT(*) 
            FROM workflow_metadata 
            WHERE extracted_at > NOW() - INTERVAL '5 minutes'
        """))
        recent = result.scalar()
        
        return {
            'total': total,
            'scraped': scraped,
            'complete': complete,
            'recent': recent,
            'remaining': total - scraped
        }

def print_progress_bar(current, total, width=50):
    """Print a progress bar."""
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {pct*100:.1f}%"

def main():
    """Monitor progress continuously."""
    print("\n" + "="*70)
    print("LAYER 1 SCRAPING PROGRESS MONITOR")
    print("="*70)
    print("\nPress Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            stats = get_stats()
            
            print("\r" + " "*100, end='')  # Clear line
            print(f"\r📊 Progress: {stats['scraped']}/{stats['total']} workflows", end='')
            print(f" | ✅ Complete: {stats['complete']}", end='')
            print(f" | 🔄 Recent: {stats['recent']}", end='')
            print(f" | ⏳ Remaining: {stats['remaining']}", end='', flush=True)
            
            if stats['scraped'] >= stats['total']:
                print("\n\n✅ SCRAPING COMPLETE!")
                break
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Monitoring stopped")
        print(f"\nFinal status: {stats['scraped']}/{stats['total']} workflows scraped")

if __name__ == "__main__":
    main()

