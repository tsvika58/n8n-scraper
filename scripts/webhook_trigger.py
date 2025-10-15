#!/usr/bin/env python3
"""
Webhook trigger for real-time dashboard updates
"""
import requests
import time

def trigger_dashboard_update():
    """Trigger immediate dashboard update via webhook"""
    try:
        response = requests.post('http://localhost:5001/api/trigger-update', timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard update triggered")
            return True
        else:
            print(f"⚠️  Dashboard update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to trigger dashboard update: {e}")
        return False

if __name__ == "__main__":
    print("🔔 Triggering dashboard update...")
    trigger_dashboard_update()





