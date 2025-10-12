#!/bin/bash
# Launch Real-Time Dashboard

cd "$(dirname "$0")"

echo "🚀 Starting N8N Scraper Real-Time Dashboard..."
echo ""

# Check if psycopg2 is installed
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "⚠️  Installing required package: psycopg2-binary"
    pip3 install psycopg2-binary
    echo ""
fi

# Start the dashboard
python3 scripts/realtime-dashboard.py
