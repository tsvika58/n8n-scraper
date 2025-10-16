#!/usr/bin/env python3
"""
Check Database Connection Status
Shows current connection pool usage and reserved connections.

Author: Dev1
Task: Reserved Connection Management
Date: October 16, 2025
"""

import sys
sys.path.append('.')

from src.storage.database import print_connection_status, get_database_stats

def main():
    """Main function to check connection status."""
    print()
    print_connection_status()
    print()
    
    # Additional details
    stats = get_database_stats()
    print("📈 DETAILED STATISTICS:")
    print(f"   Total automation requests: {stats['automation_requests']}")
    print(f"   Pool checked in: {stats['pool_checked_in']}")
    print(f"   Pool checked out: {stats['pool_checked_out']}")
    print()
    
    # Usage percentage
    automation_usage_pct = (stats['automation_in_use'] / stats['total_automation_capacity']) * 100
    print(f"💯 USAGE METRICS:")
    print(f"   Automation pool usage: {automation_usage_pct:.1f}%")
    print(f"   Ad-hoc reserved: {stats['adhoc_guaranteed_available']} connections (always available)")
    print()
    
    # Recommendations
    if automation_usage_pct > 90:
        print("⚠️  RECOMMENDATION: Automation pool at high usage. Consider scaling.")
    elif automation_usage_pct > 70:
        print("⚡ NOTICE: Automation pool usage is moderate.")
    else:
        print("✅ STATUS: Automation pool has plenty of capacity.")
    
    print()

if __name__ == "__main__":
    main()


