#!/usr/bin/env python3
"""
Global Connection Monitor
Monitor database connections across ALL containers and services

Usage:
    python monitor_global_connections.py
"""

import sys
import time
import os
from datetime import datetime

sys.path.append('/app')

from src.storage.global_connection_coordinator import (
    get_global_status,
    global_coordinator
)
from loguru import logger


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header():
    """Print monitor header"""
    print("=" * 90)
    print("🌍 GLOBAL CONNECTION MONITOR (ALL CONTAINERS)")
    print("=" * 90)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def print_supabase_config(status):
    """Print Supabase configuration"""
    print("📊 SUPABASE CONFIGURATION")
    print("-" * 90)
    print(f"  Plan:                  {status['supabase_plan'].upper()}")
    print(f"  Max Connections:       {status['max_connections']}")
    print(f"  Reserved for Supabase: {status['reserved_for_supabase']} (10%)")
    print(f"  Available for Apps:    {status['available_for_apps']}")
    print()


def print_usage_summary(status):
    """Print usage summary"""
    utilization = status['utilization_pct']
    
    # Color coding
    if utilization < 50:
        status_icon = "🟢"
        status_text = "HEALTHY"
    elif utilization < 75:
        status_icon = "🟡"
        status_text = "MODERATE"
    elif utilization < 90:
        status_icon = "🟠"
        status_text = "HIGH"
    else:
        status_icon = "🔴"
        status_text = "CRITICAL"
    
    print("📈 GLOBAL USAGE")
    print("-" * 90)
    print(f"  Status:                {status_icon} {status_text}")
    print(f"  Total Allocated:       {status['total_allocated']}/{status['available_for_apps']}")
    print(f"  Remaining:             {status['remaining']}")
    print(f"  Utilization:           {utilization:.1f}%")
    
    # Progress bar
    bar_length = 50
    filled = int(bar_length * utilization / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"  [{bar}] {utilization:.1f}%")
    print()


def print_service_breakdown(status):
    """Print per-service breakdown"""
    services = status['services']
    
    if not services:
        print("🔧 SERVICES")
        print("-" * 90)
        print("  No services currently using connections")
        print()
        return
    
    print("🔧 SERVICES")
    print("-" * 90)
    
    # Header
    print(f"  {'Service':<15} {'Containers':<12} {'Connections':<15} {'% of Total':<12}")
    print(f"  {'-'*15} {'-'*12} {'-'*15} {'-'*12}")
    
    # Services
    for service_name, service_data in sorted(services.items()):
        containers = len(service_data['containers'])
        connections = service_data['total_connections']
        pct = (connections / status['total_allocated'] * 100) if status['total_allocated'] > 0 else 0
        
        print(f"  {service_name:<15} {containers:<12} {connections:<15} {pct:.1f}%")
    
    print()


def print_container_details(status):
    """Print per-container details"""
    services = status['services']
    
    if not services:
        return
    
    print("🐳 CONTAINER DETAILS")
    print("-" * 90)
    
    for service_name, service_data in sorted(services.items()):
        print(f"\n  {service_name.upper()}:")
        
        for container in service_data['containers']:
            container_id_short = container['container_id'][:12]
            hostname = container['hostname']
            connections = container['connections']
            reserved_time = datetime.fromtimestamp(container['reserved_at']).strftime('%H:%M:%S')
            
            print(f"    • {container_id_short}... ({hostname})")
            print(f"      Connections: {connections} | Reserved at: {reserved_time}")
    
    print()


def print_warnings(status):
    """Print warnings if any"""
    warnings = []
    
    # Check utilization
    if status['utilization_pct'] > 90:
        warnings.append("⚠️  CRITICAL: Connection pool >90% utilized!")
    elif status['utilization_pct'] > 75:
        warnings.append("⚠️  WARNING: Connection pool >75% utilized")
    
    # Check remaining
    if status['remaining'] < 5:
        warnings.append(f"⚠️  WARNING: Only {status['remaining']} connections remaining")
    
    # Check if approaching limit
    if status['total_allocated'] >= status['available_for_apps']:
        warnings.append("🔴 CRITICAL: Connection pool exhausted!")
    
    if warnings:
        print("⚠️  WARNINGS")
        print("-" * 90)
        for warning in warnings:
            print(f"  {warning}")
        print()


def print_recommendations(status):
    """Print recommendations"""
    utilization = status['utilization_pct']
    
    print("💡 RECOMMENDATIONS")
    print("-" * 90)
    
    if utilization > 90:
        print("  🔴 URGENT ACTIONS:")
        print("     1. Upgrade Supabase plan for more connections")
        print("     2. Stop non-essential services")
        print("     3. Reduce scraper concurrency")
    elif utilization > 75:
        print("  🟠 SUGGESTED ACTIONS:")
        print("     1. Monitor closely for further increases")
        print("     2. Consider upgrading Supabase plan")
        print("     3. Review service connection usage")
    elif utilization < 50:
        print("  🟢 HEALTHY:")
        print("     • Connection usage is within safe limits")
        print("     • No action needed")
    
    print()


def monitor_loop(interval=10):
    """Main monitoring loop"""
    logger.info(f"🚀 Starting global connection monitor (refresh every {interval}s)")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get status
            status = get_global_status()
            
            # Clear and print
            clear_screen()
            print_header()
            print_supabase_config(status)
            print_usage_summary(status)
            print_service_breakdown(status)
            print_container_details(status)
            print_warnings(status)
            print_recommendations(status)
            
            print("-" * 90)
            print(f"🔄 Refreshing in {interval} seconds... (Press Ctrl+C to stop)")
            
            # Wait
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user")
        sys.exit(0)


def main():
    """Main entry point"""
    
    # Check if Redis is available
    if not global_coordinator.use_redis:
        print("=" * 90)
        print("⚠️  WARNING: Redis not available")
        print("=" * 90)
        print()
        print("Global connection coordination requires Redis.")
        print()
        print("To enable:")
        print("  1. Start Redis: docker-compose -f docker-compose-with-redis.yml up -d")
        print("  2. Set REDIS_URL environment variable")
        print("  3. Restart this monitor")
        print()
        print("=" * 90)
        sys.exit(1)
    
    # Parse arguments
    interval = 10
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}")
            print("Usage: python monitor_global_connections.py [interval_seconds]")
            sys.exit(1)
    
    # Run monitor
    monitor_loop(interval)


if __name__ == "__main__":
    main()

