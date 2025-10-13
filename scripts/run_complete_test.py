#!/usr/bin/env python3
"""
Complete Dashboard Test - Restart dashboard and run live scraping test
"""
import subprocess
import time
import sys

def run_command(cmd, description):
    """Run a command and print output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 COMPLETE DASHBOARD TEST")
    print("="*60)
    
    # Step 1: Kill old dashboard
    print("\n📍 Step 1: Stopping old dashboard...")
    run_command(
        "docker exec n8n-scraper-app pkill -f realtime-dashboard 2>/dev/null || true",
        "Stopping old dashboard process"
    )
    
    # Step 2: Wait
    print("\n⏳ Waiting 3 seconds...")
    time.sleep(3)
    
    # Step 3: Start new dashboard in background
    print("\n📍 Step 2: Starting new dashboard...")
    subprocess.Popen(
        ["docker", "exec", "n8n-scraper-app", "python", "/app/scripts/realtime-dashboard-enhanced.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Step 4: Wait for dashboard to start
    print("\n⏳ Waiting 5 seconds for dashboard to initialize...")
    time.sleep(5)
    
    # Step 5: Verify dashboard is running
    print("\n📍 Step 3: Verifying dashboard is accessible...")
    result = subprocess.run(
        ["docker", "exec", "n8n-scraper-app", "netstat", "-tuln"],
        capture_output=True,
        text=True
    )
    
    if "5001" in result.stdout:
        print("✅ Dashboard is running on port 5001")
    else:
        print("⚠️  Port 5001 not detected, but continuing...")
    
    print("\n" + "="*60)
    print("📊 Dashboard URL: http://localhost:5001")
    print("="*60)
    
    # Step 6: Run live scraping test
    print("\n📍 Step 4: Running live scraping test...")
    print("\n🎯 WATCH THE DASHBOARD NOW!")
    print("   Open http://localhost:5001 in your browser")
    print("   Watch the 'LIVE SCRAPING STATUS' section update in real-time")
    print("\n⏳ Starting test in 5 seconds...")
    time.sleep(5)
    
    print("\n" + "="*60)
    print("🚀 RUNNING LIVE SCRAPING TEST")
    print("="*60 + "\n")
    
    # Run the test (this will show output)
    success = run_command(
        "docker exec n8n-scraper-app python /app/scripts/simple_live_test.py",
        "Live Scraping Test"
    )
    
    if success:
        print("\n" + "="*60)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Check the dashboard at http://localhost:5001")
        print("   - Live scraping section should show session stats")
        print("   - Progress bar should display success/failed counts")
        print("   - Stats will persist for 5 minutes")
    else:
        print("\n" + "="*60)
        print("⚠️  TEST COMPLETED WITH ISSUES")
        print("="*60)
        print("\n📊 Check the dashboard anyway at http://localhost:5001")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())




