#!/usr/bin/env python3
"""
Simple script to start the database viewer
"""

import subprocess
import time
import requests

def start_database_viewer():
    print("🚀 Starting Database Viewer...")
    
    # Kill any existing processes
    try:
        subprocess.run(["docker", "exec", "n8n-scraper-app", "python", "-c", "import os; os.system('killall python 2>/dev/null || true')"], 
                      check=False, capture_output=True)
        print("✅ Killed existing processes")
    except:
        pass
    
    # Start the database viewer
    try:
        subprocess.run(["docker", "exec", "-d", "n8n-scraper-app", "python", "/app/scripts/view-database.py"], 
                      check=True)
        print("✅ Database viewer started")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start database viewer: {e}")
        return False
    
    # Wait for it to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test the connection
    try:
        response = requests.get("http://localhost:5004", timeout=5)
        if response.status_code == 200:
            print("✅ Database viewer is accessible!")
            print("📍 URL: http://localhost:5004")
            return True
        else:
            print(f"❌ Database viewer returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database viewer not accessible: {e}")
        return False

if __name__ == "__main__":
    success = start_database_viewer()
    if success:
        print("\n🎉 Database viewer is ready!")
    else:
        print("\n❌ Database viewer failed to start")



