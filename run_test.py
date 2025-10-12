#!/usr/bin/env python3
import subprocess
import time

print("="*60)
print("🚀 DASHBOARD LIVE TEST")
print("="*60)

# Step 1: Kill old dashboard
print("\n📍 Step 1: Stopping old dashboard...")
subprocess.run(["docker", "exec", "n8n-scraper-app", "pkill", "-f", "realtime-dashboard"], 
               stderr=subprocess.DEVNULL)
print("✅ Old dashboard stopped")

# Step 2: Wait
print("\n⏳ Waiting 2 seconds...")
time.sleep(2)

# Step 3: Start new dashboard
print("\n📍 Step 2: Starting new dashboard...")
subprocess.Popen(
    ["docker", "exec", "n8n-scraper-app", "python", "/app/scripts/realtime-dashboard-enhanced.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print("✅ Dashboard started in background")

# Step 4: Wait for startup
print("\n⏳ Waiting 5 seconds for dashboard to initialize...")
time.sleep(5)

# Step 5: Show dashboard URL
print("\n" + "="*60)
print("📊 Dashboard running at: http://localhost:5001")
print("🎯 WATCH THE DASHBOARD NOW!")
print("="*60)

# Step 6: Wait before test
print("\n⏳ Starting test in 3 seconds...")
time.sleep(3)

# Step 7: Run test
print("\n📍 Step 3: Running live scraping test...")
print("="*60)
result = subprocess.run(
    ["docker", "exec", "n8n-scraper-app", "python", "/app/scripts/simple_live_test.py"]
)

print("\n" + "="*60)
if result.returncode == 0:
    print("✅ TEST COMPLETED SUCCESSFULLY!")
else:
    print("⚠️  TEST COMPLETED WITH ERRORS")
print("="*60)
print("\n📊 Check dashboard at http://localhost:5001")
print("   - Status should show 'SCRAPING'")
print("   - Live progress bar should show 5/5 workflows")
print("   - Stats will persist for 5 minutes")
print("="*60)


