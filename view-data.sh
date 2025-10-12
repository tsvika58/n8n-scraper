#!/bin/bash
# Quick launcher for database viewer

cd "$(dirname "$0")"

echo "🚀 Starting N8N Scraper Database Viewer..."
echo ""

# Check if psycopg2 is installed
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "⚠️  Installing required package: psycopg2-binary"
    pip3 install psycopg2-binary
    echo ""
fi

# Start the viewer
python3 scripts/view-database.py
echo ""
echo "✅ Database viewer should be running at: http://localhost:5003"

