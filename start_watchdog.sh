#!/bin/bash
# Start Scraper Watchdog - Keepalive Mechanism

echo "=" | tr ' ' '=' | head -c 80; echo
echo "🐕 STARTING SCRAPER WATCHDOG"
echo "=" | tr ' ' '=' | head -c 80; echo
echo "This watchdog will:"
echo "  ✓ Monitor all scraper processes (Layer 1.5, Layer 2, Layer 3)"
echo "  ✓ Check progress every 5 minutes"
echo "  ✓ Restart scrapers if they stop or stall"
echo "  ✓ Log all activity to /app/logs/watchdog.log"
echo ""

# Check if watchdog is already running
if docker exec n8n-scraper-app pgrep -f "scraper_watchdog.py" > /dev/null; then
    echo "⚠️  Watchdog is already running!"
    echo ""
    echo "Current watchdog process:"
    docker exec n8n-scraper-app ps aux | grep scraper_watchdog.py | grep -v grep
    echo ""
    echo "To stop it first: docker exec n8n-scraper-app pkill -f scraper_watchdog.py"
    exit 1
fi

# Start watchdog in background
echo "Starting watchdog in background..."
docker exec -d n8n-scraper-app python /app/scripts/scraper_watchdog.py

# Wait a moment for it to start
sleep 2

# Check if it started
if docker exec n8n-scraper-app pgrep -f "scraper_watchdog.py" > /dev/null; then
    echo ""
    echo "✅ Watchdog started successfully!"
    echo ""
    echo "Monitor logs with:"
    echo "  docker exec n8n-scraper-app tail -f /app/logs/watchdog.log"
    echo ""
    echo "Check watchdog status:"
    echo "  docker exec n8n-scraper-app ps aux | grep scraper_watchdog"
    echo ""
    echo "Stop watchdog:"
    echo "  docker exec n8n-scraper-app pkill -f scraper_watchdog.py"
else
    echo "❌ Failed to start watchdog"
    exit 1
fi




