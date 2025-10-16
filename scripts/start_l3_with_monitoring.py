#!/usr/bin/env python3
"""
Start L3 Scraper with Live Progress Monitoring

This script provides a simple way to start the L3 scraper with live progress monitoring.
"""

import os
import sys
import subprocess
from datetime import datetime

def main():
    """Start the L3 scraper with progress monitoring."""
    print("🚀 L3 SCRAPER WITH LIVE PROGRESS MONITORING")
    print("=" * 60)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scraper_script = os.path.join(script_dir, "run_l3_foreground.py")
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{script_dir}/..:{script_dir}/../../n8n-shared"
    
    print("🔧 Starting L3 scraper with live progress monitoring...")
    print("📊 You'll see a live dashboard with:")
    print("   • Real-time progress bar")
    print("   • Success/failure rates")
    print("   • Videos and transcripts found")
    print("   • Processing rate and ETA")
    print("   • Currently processing workflow")
    print()
    print("🛑 Press Ctrl+C to stop gracefully")
    print("=" * 60)
    print()
    
    try:
        # Run the scraper
        result = subprocess.run([
            sys.executable, scraper_script
        ], env=env, cwd=os.path.dirname(script_dir))
        
        if result.returncode == 0:
            print("\n✅ L3 scraping completed successfully!")
        else:
            print(f"\n❌ L3 scraping failed with exit code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Scraping stopped by user")
        print("📊 Progress saved - you can resume later")
    except Exception as e:
        print(f"\n❌ Error starting scraper: {e}")

if __name__ == "__main__":
    main()

