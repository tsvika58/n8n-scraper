#!/bin/bash
# Terminal Monitor Launcher

cd "$(dirname "$0")"

echo "📊 N8N Scraper Terminal Monitor"
echo ""

# Check if psycopg2 is installed
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "⚠️  Installing required package: psycopg2-binary"
    pip3 install psycopg2-binary
    echo ""
fi

# Parse arguments
if [ "$1" = "watch" ]; then
    echo "🔄 Starting watch mode..."
    python3 scripts/terminal-monitor.py watch ${2:-2}
elif [ "$1" = "stats" ]; then
    echo "📊 Showing current statistics..."
    python3 scripts/terminal-monitor.py stats
elif [ "$1" = "recent" ]; then
    echo "📋 Showing recent workflows..."
    python3 scripts/terminal-monitor.py recent
else
    echo "Usage:"
    echo "  ./monitor.sh           # Show current stats"
    echo "  ./monitor.sh watch     # Watch mode (2s refresh)"
    echo "  ./monitor.sh watch 5   # Watch mode (5s refresh)"
    echo "  ./monitor.sh stats     # Show stats only"
    echo "  ./monitor.sh recent    # Show recent workflows"
    echo ""
    echo "Running default (stats)..."
    echo ""
    python3 scripts/terminal-monitor.py
fi
