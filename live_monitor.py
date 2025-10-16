#!/usr/bin/env python3
"""
Live Layer 1 Scraping Progress Monitor
Shows real-time progress with visual progress bar
"""

import time
import sys
import os
sys.path.append('/app')

from src.storage.database import get_session
from sqlalchemy import text

def create_progress_bar(current, total, width=50):
    """Create a visual progress bar"""
    percentage = (current / total) * 100
    filled = int((current / total) * width)
    bar = '█' * filled + '░' * (width - filled)
    return f'[{bar}] {percentage:.1f}%'

def clear_screen():
    """Clear the terminal screen"""
    print('\033[2J\033[H', end='')

def format_number(num):
    """Format numbers with commas"""
    return f"{num:,}"

def main():
    print("🚀 Starting Layer 1 Scraping Live Monitor...")
    print("Press Ctrl+C to exit")
    time.sleep(2)
    
    while True:
        try:
            with get_session() as session:
                # Get current stats
                result = session.execute(text("""
                    SELECT 
                        COUNT(*) as total_workflows,
                        COUNT(CASE WHEN layer1_success = true THEN 1 END) as with_l1_success,
                        COUNT(CASE WHEN layer1_success IS NULL OR layer1_success = false THEN 1 END) as without_l1_success
                    FROM workflows
                """))
                
                total, with_success, without_success = result.fetchone()
                progress_pct = (with_success / total) * 100
                remaining = without_success
                
                # Calculate ETA (assuming 7.5 seconds per workflow)
                if remaining > 0:
                    eta_hours = (remaining * 7.5) / 3600
                    eta_str = f"{eta_hours:.1f} hours"
                else:
                    eta_str = "COMPLETE! 🎉"
                
                # Clear screen and show progress
                clear_screen()
                print('🚀 LAYER 1 SCRAPING LIVE MONITOR')
                print('=' * 60)
                print(f'📊 Total Workflows: {format_number(total)}')
                print(f'✅ Completed: {format_number(with_success)} workflows')
                print(f'⏳ Remaining: {format_number(remaining)} workflows')
                print(f'📈 Progress: {progress_pct:.1f}%')
                print('')
                print(create_progress_bar(with_success, total))
                print('')
                print(f'🎯 ETA: {eta_str}')
                print(f'⏰ Last Updated: {time.strftime("%H:%M:%S")}')
                print('')
                print('Press Ctrl+C to exit monitoring')
                print('=' * 60)
                
                # Update every 5 seconds
                time.sleep(5)
                
        except KeyboardInterrupt:
            clear_screen()
            print('👋 Monitoring stopped. Layer 1 scraping continues in background.')
            break
        except Exception as e:
            print(f'❌ Error: {e}')
            print('Retrying in 5 seconds...')
            time.sleep(5)

if __name__ == "__main__":
    main()



