#!/bin/bash
docker exec n8n-scraper-app pkill -f realtime-dashboard
sleep 3
docker exec n8n-scraper-app python /app/scripts/realtime-dashboard-enhanced.py &
sleep 5
docker exec n8n-scraper-app python /app/scripts/simple_live_test.py




