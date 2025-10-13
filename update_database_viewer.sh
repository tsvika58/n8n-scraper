#!/bin/bash

echo "🔍 Updating Database Viewer with Sortable Columns..."
echo "=================================================="
echo ""

echo "1. Stopping existing database viewer..."
docker exec n8n-scraper-app pkill -f "view-database.py" 2>/dev/null || echo "   No existing viewer to stop"

echo ""
echo "2. Copying updated database viewer to container..."
docker cp scripts/view-database.py n8n-scraper-app:/app/scripts/view-database.py

echo ""
echo "3. Starting updated sortable database viewer..."
docker exec -d n8n-scraper-app python /app/scripts/view-database.py

echo ""
echo "4. Waiting for server to start..."
sleep 3

echo ""
echo "5. Testing database viewer..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5004 | grep -q "200"; then
    echo "   ✅ Database viewer is running successfully!"
    echo ""
    echo "🎉 SORTABLE DATABASE VIEWER READY!"
    echo "=================================="
    echo ""
    echo "📍 Access: http://localhost:5004"
    echo ""
    echo "✨ New Features:"
    echo "   • Click any column header to sort"
    echo "   • Visual indicators (↑↓) show sort direction"
    echo "   • Active column highlighted in blue"
    echo "   • Maintains search and pagination"
    echo ""
else
    echo "   ❌ Database viewer failed to start"
    echo "   Check logs: docker logs n8n-scraper-app"
fi



