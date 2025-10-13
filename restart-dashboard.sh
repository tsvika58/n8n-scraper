#!/bin/bash
# Restart the real-time dashboard

echo "Stopping old dashboard..."
docker exec n8n-scraper-app pkill -f realtime-dashboard 2>/dev/null

echo "Waiting 2 seconds..."
sleep 2

echo "Starting new dashboard..."
docker exec n8n-scraper-app python /app/scripts/realtime-dashboard-enhanced.py &

echo ""
echo "Dashboard starting on http://localhost:5001"




