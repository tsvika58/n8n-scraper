#!/bin/bash
# Auto-start script for N8N Scraper dashboards
# This script runs on container startup

echo "🚀 Starting N8N Scraper Dashboards..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! pg_isready -h n8n-scraper-database -p 5432 -U scraper_user > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Database ready"

# Start Real-time Scraping Dashboard (port 5002)
echo "📊 Starting Real-time Scraping Dashboard (port 5002)..."
python /app/scripts/realtime-dashboard.py > /dev/null 2>&1 &
echo "✅ Real-time Dashboard started"

# Start Database Viewer (port 5004)
echo "🗄️  Starting Database Viewer (port 5004)..."
python /app/scripts/db-viewer.py > /dev/null 2>&1 &
echo "✅ Database Viewer started"

echo ""
echo "=" * 60
echo "🎉 All dashboards started successfully!"
echo "=" * 60
echo ""
echo "📍 Access Points:"
echo "   • Real-time Scraping: http://localhost:5002"
echo "   • Database Viewer:    http://localhost:5004"
echo ""
echo "=" * 60

