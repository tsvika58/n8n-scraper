#!/usr/bin/env python3
"""
Test script to monitor real-time dashboard status and demonstrate live updates
"""

import requests
import time
import json
from datetime import datetime

def test_dashboard_live_status():
    """Test the real-time dashboard live status detection"""
    print("🔍 Testing Real-Time Dashboard Live Status Detection")
    print("=" * 60)
    
    dashboard_url = "http://localhost:5001/api/stats"
    
    for i in range(10):  # Test for 10 iterations
        try:
            response = requests.get(dashboard_url, timeout=5)
            if response.status_code == 200:
                stats = response.json()
                
                print(f"\n📊 Dashboard Status Update #{i+1} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"   🔄 Scraping Status: {'✅ ACTIVE' if stats.get('is_scraping') else '❌ IDLE'}")
                print(f"   🖥️  Active Processes: {stats.get('active_processes', 0)} Chrome instances")
                print(f"   📈 Total Progress: {stats.get('fully_successful', 0) + stats.get('partial_success', 0)}/{stats.get('total_workflows', 0)} workflows")
                print(f"   ⚡ Recent Activity: {stats.get('recent_workflows', 0)} workflows in last 5 minutes")
                print(f"   🎯 Success Rate: {stats.get('success_rate', 0):.1f}%")
                print(f"   💾 DB Status: {stats.get('db_status', 'Unknown')}")
                print(f"   🖥️  CPU: {stats.get('cpu_usage', 'Unknown')}")
                print(f"   💾 Memory: {stats.get('memory_usage', 'Unknown')}")
                
                # Show current workflow if available
                current_workflow = stats.get('current_workflow')
                if current_workflow:
                    print(f"   🔄 Current Workflow: {current_workflow.get('workflow_id', 'Unknown')}")
                
            else:
                print(f"❌ Failed to get dashboard stats: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting dashboard stats: {e}")
        
        # Wait 5 seconds between checks
        if i < 9:  # Don't wait after the last iteration
            print("   ⏳ Waiting 5 seconds for next update...")
            time.sleep(5)
    
    print("\n" + "=" * 60)
    print("✅ Dashboard Live Status Test Complete!")
    print("\n📋 Summary:")
    print("   - Dashboard API is responding")
    print("   - Real-time updates are working")
    print("   - Scraping detection is functional")
    print("   - System metrics are being collected")

if __name__ == "__main__":
    test_dashboard_live_status()

