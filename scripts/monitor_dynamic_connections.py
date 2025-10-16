#!/usr/bin/env python3
"""
Dynamic Connection Pool Monitor
Real-time monitoring of connection allocation across scrapers

Usage:
    python monitor_dynamic_connections.py
"""

import sys
import time
import os
from datetime import datetime

sys.path.append('/app')

from src.storage.dynamic_connection_manager import (
    dynamic_connection_manager,
    get_connection_stats
)
from loguru import logger


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header():
    """Print monitor header"""
    print("=" * 80)
    print("📊 DYNAMIC CONNECTION POOL MONITOR")
    print("=" * 80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def print_pool_status(stats):
    """Print global pool status"""
    pool = stats['pool']
    
    print("🌐 GLOBAL POOL STATUS")
    print("-" * 80)
    print(f"  Total Connections:     {pool['global_pool_size']}")
    print(f"  In Use:                {pool['checked_out']}/{pool['size']}")
    print(f"  Available:             {pool['checked_in']}")
    print(f"  Overflow:              {pool['overflow']}")
    print(f"  Utilization:           {pool['checked_out']/pool['size']*100:.1f}%")
    print()


def print_scraper_allocation(stats):
    """Print per-scraper allocation"""
    scrapers = stats['scrapers']
    
    if not scrapers:
        print("🔧 SCRAPER ALLOCATION")
        print("-" * 80)
        print("  No active scrapers")
        print()
        return
    
    print("🔧 SCRAPER ALLOCATION")
    print("-" * 80)
    
    # Header
    print(f"  {'Scraper':<25} {'Status':<12} {'Conn':<8} {'Limit':<8} {'Idle':<10}")
    print(f"  {'-'*25} {'-'*12} {'-'*8} {'-'*8} {'-'*10}")
    
    # Scrapers
    for scraper in scrapers:
        status_icon = "🟢" if scraper['active'] else "⚪"
        status_text = "Active" if scraper['active'] else "Idle"
        status = f"{status_icon} {status_text}"
        
        connections = f"{scraper['connections']}/{scraper['limit']}"
        idle = f"{scraper['idle_seconds']}s" if not scraper['active'] else "-"
        
        print(f"  {scraper['scraper']:<25} {status:<12} {scraper['connections']:<8} {scraper['limit']:<8} {idle:<10}")
    
    print()


def print_allocation_strategy(stats):
    """Print current allocation strategy"""
    scrapers = stats['scrapers']
    active_count = sum(1 for s in scrapers if s['active'])
    
    print("📋 ALLOCATION STRATEGY")
    print("-" * 80)
    
    if active_count == 0:
        print("  Strategy: No active scrapers")
    elif active_count == 1:
        print("  Strategy: Single scraper mode")
        print(f"  • Active scraper can use up to {stats['pool']['scraper_max_limit']} connections")
    elif active_count == 2:
        print("  Strategy: Dual scraper mode")
        print(f"  • Each scraper can use up to {stats['pool']['global_pool_size']//2} connections")
    else:
        print("  Strategy: Multi-scraper fair distribution")
        print(f"  • Each scraper limited to {stats['pool']['scraper_soft_limit']} connections")
    
    print()


def print_efficiency_metrics(stats):
    """Print efficiency metrics"""
    pool = stats['pool']
    scrapers = stats['scrapers']
    
    total_connections = pool['checked_out']
    active_scrapers = sum(1 for s in scrapers if s['active'])
    
    print("📈 EFFICIENCY METRICS")
    print("-" * 80)
    
    if active_scrapers > 0:
        avg_per_scraper = total_connections / active_scrapers
        print(f"  Active Scrapers:       {active_scrapers}")
        print(f"  Avg Connections/Scraper: {avg_per_scraper:.1f}")
        print(f"  Pool Utilization:      {total_connections/pool['size']*100:.1f}%")
        
        # Efficiency score
        ideal_usage = active_scrapers * pool['scraper_soft_limit']
        efficiency = min(100, (total_connections / ideal_usage * 100)) if ideal_usage > 0 else 0
        print(f"  Efficiency Score:      {efficiency:.1f}%")
    else:
        print("  No active scrapers")
    
    print()


def monitor_loop(interval=5):
    """Main monitoring loop"""
    logger.info(f"🚀 Starting dynamic connection monitor (refresh every {interval}s)")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get stats
            stats = get_connection_stats()
            
            # Clear and print
            clear_screen()
            print_header()
            print_pool_status(stats)
            print_scraper_allocation(stats)
            print_allocation_strategy(stats)
            print_efficiency_metrics(stats)
            
            print("-" * 80)
            print(f"🔄 Refreshing in {interval} seconds... (Press Ctrl+C to stop)")
            
            # Wait
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
        sys.exit(0)


def main():
    """Main entry point"""
    
    # Parse arguments
    interval = 5
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}")
            print("Usage: python monitor_dynamic_connections.py [interval_seconds]")
            sys.exit(1)
    
    # Run monitor
    monitor_loop(interval)


if __name__ == "__main__":
    main()


