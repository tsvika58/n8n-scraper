#!/usr/bin/env python3
"""
Dynamic Scraper Startup Script
Uses dynamic connection pooling with intelligent resource allocation

Usage:
    python start_scraper_dynamic.py layer1_5_production_scraper.py --all
    python start_scraper_dynamic.py layer3_production.py --test
"""

import sys
import os
import signal
import subprocess
import atexit
from pathlib import Path

sys.path.append('/app')

from src.storage.dynamic_connection_manager import (
    dynamic_connection_manager,
    register_scraper,
    startup_dynamic_pool,
    shutdown_dynamic_pool,
    print_connection_stats
)
from src.storage.connection_manager import (
    prevent_duplicate_process,
    cleanup_zombie_processes
)
from loguru import logger


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"⚠️  Received signal {signum}, shutting down...")
    shutdown_dynamic_pool()
    sys.exit(0)


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python start_scraper_dynamic.py <scraper_script> [args...]")
        print()
        print("Examples:")
        print("  python start_scraper_dynamic.py layer1_5_production_scraper.py --all")
        print("  python start_scraper_dynamic.py layer3_production.py --test")
        print()
        print("Features:")
        print("  ✅ Dynamic connection allocation")
        print("  ✅ Idle scrapers release connections")
        print("  ✅ Active scrapers can use more when available")
        print("  ✅ Automatic zombie cleanup")
        sys.exit(1)
    
    scraper_script = sys.argv[1]
    scraper_args = sys.argv[2:]
    
    # Extract scraper name from script
    scraper_name = scraper_script.replace('_production_scraper.py', '').replace('.py', '')
    
    # Validate scraper script exists
    script_path = Path('/app/scripts') / scraper_script
    if not script_path.exists():
        logger.error(f"❌ Scraper script not found: {script_path}")
        sys.exit(1)
    
    logger.info(f"🚀 Starting scraper: {scraper_script}")
    logger.info(f"📝 Scraper name: {scraper_name}")
    logger.info(f"📝 Arguments: {' '.join(scraper_args)}")
    logger.info(f"🔄 Using dynamic connection pooling")
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(shutdown_dynamic_pool)
    
    try:
        # Step 1: Startup dynamic pool
        startup_dynamic_pool()
        
        # Step 2: Cleanup zombies
        cleanup_zombie_processes()
        
        # Step 3: Check for duplicate processes
        if not prevent_duplicate_process(scraper_script, force=True):
            logger.error("❌ Failed to prevent duplicate process")
            sys.exit(1)
        
        # Step 4: Register this scraper
        register_scraper(scraper_name)
        
        # Step 5: Show initial connection stats
        logger.info("\n📊 Initial Connection Pool Status:")
        print_connection_stats()
        
        # Step 6: Run the scraper
        logger.info(f"▶️  Launching {scraper_script}...")
        
        cmd = ['python', str(script_path)] + scraper_args
        result = subprocess.run(cmd, check=False)
        
        # Step 7: Show final connection stats
        logger.info("\n📊 Final Connection Pool Status:")
        print_connection_stats()
        
        # Step 8: Cleanup after completion
        logger.info(f"🏁 Scraper finished with exit code: {result.returncode}")
        shutdown_dynamic_pool()
        
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupted by user")
        shutdown_dynamic_pool()
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        shutdown_dynamic_pool()
        sys.exit(1)


if __name__ == "__main__":
    main()

