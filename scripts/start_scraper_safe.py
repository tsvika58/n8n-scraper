#!/usr/bin/env python3
"""
Safe Scraper Startup Script
Ensures clean startup with no redundant processes or connections

Usage:
    python start_scraper_safe.py layer1_5_production_scraper.py --all
    python start_scraper_safe.py layer3_production.py --test
"""

import sys
import os
import signal
import subprocess
import atexit
from pathlib import Path

sys.path.append('/app')

from src.storage.connection_manager import (
    connection_manager,
    prevent_duplicate_process,
    startup_cleanup,
    shutdown_cleanup
)
from loguru import logger


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"⚠️  Received signal {signum}, shutting down...")
    shutdown_cleanup()
    sys.exit(0)


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python start_scraper_safe.py <scraper_script> [args...]")
        print()
        print("Examples:")
        print("  python start_scraper_safe.py layer1_5_production_scraper.py --all")
        print("  python start_scraper_safe.py layer3_production.py --test")
        sys.exit(1)
    
    scraper_script = sys.argv[1]
    scraper_args = sys.argv[2:]
    
    # Validate scraper script exists
    script_path = Path('/app/scripts') / scraper_script
    if not script_path.exists():
        logger.error(f"❌ Scraper script not found: {script_path}")
        sys.exit(1)
    
    logger.info(f"🚀 Starting scraper: {scraper_script}")
    logger.info(f"📝 Arguments: {' '.join(scraper_args)}")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(shutdown_cleanup)
    
    try:
        # Step 1: Startup cleanup
        startup_cleanup()
        
        # Step 2: Check for duplicate processes
        if not prevent_duplicate_process(scraper_script, force=True):
            logger.error("❌ Failed to prevent duplicate process")
            sys.exit(1)
        
        # Step 3: Register this process
        connection_manager.register_process(scraper_script)
        
        # Step 4: Run the scraper
        logger.info(f"▶️  Launching {scraper_script}...")
        
        cmd = ['python', str(script_path)] + scraper_args
        result = subprocess.run(cmd, check=False)
        
        # Step 5: Cleanup after completion
        logger.info(f"🏁 Scraper finished with exit code: {result.returncode}")
        shutdown_cleanup()
        
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupted by user")
        shutdown_cleanup()
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        shutdown_cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()

