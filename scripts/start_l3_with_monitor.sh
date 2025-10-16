#!/bin/bash

# Start L3 Scraper with Live Monitoring
# This script starts the L3 scraper in the foreground with live monitoring

echo "🚀 Starting L3 Scraper with Live Monitoring"
echo "=============================================="

# Change to the correct directory
cd /Users/tsvikavagman/Desktop/Code\ Projects/shared-tools/n8n-scraper

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if docker exec n8n-scraper-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running. Starting Redis..."
    docker-compose up -d scraper-redis
    sleep 5
    if docker exec n8n-scraper-redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis started successfully"
    else
        echo "❌ Failed to start Redis. Exiting."
        exit 1
    fi
fi

echo ""
echo "📋 Starting L3 Scraper in Foreground..."
echo "   - Live console output"
echo "   - Detailed progress tracking"
echo "   - Real-time database updates"
echo "   - Press Ctrl+C to stop"
echo ""

# Run the L3 scraper in foreground
python scripts/run_l3_foreground.py

echo ""
echo "🏁 L3 Scraper finished"

