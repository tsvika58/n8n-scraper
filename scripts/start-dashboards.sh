#!/bin/bash
# Simple dashboard startup script

echo "🚀 Starting N8N Scraper Dashboards..."

# Start Real-time Scraping Dashboard (port 5002)
echo "📊 Starting Real-time Scraping Dashboard (port 5002)..."
python /app/scripts/realtime-dashboard.py > /dev/null 2>&1 &
echo "✅ Real-time Dashboard started (PID: $!)"

# Start Database Viewer (port 5004)
echo "🗄️  Starting Database Viewer (port 5004)..."
python /app/scripts/db-viewer.py > /dev/null 2>&1 &
echo "✅ Database Viewer started (PID: $!)"

echo ""
echo "🎉 Dashboards started!"
echo "   • Real-time: http://localhost:5002"
echo "   • Database:  http://localhost:5004"
