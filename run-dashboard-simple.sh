#!/bin/bash
# Simple Dashboard Launcher - Runs in current terminal with ultimate features

# Get the project directory
PROJECT_DIR="/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"

# Parse arguments
TEST_ARGS="$@"

# If no args provided, use default
if [ -z "$TEST_ARGS" ]; then
    TEST_CMD="python pytest-dashboard-ultimate.py -v --cov=src --cov-report=term-missing"
else
    TEST_CMD="python pytest-dashboard-ultimate.py $TEST_ARGS"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Activate venv
source venv/bin/activate

# Clear screen
clear

# Show banner
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🧪 ULTIMATE PYTEST DASHBOARD 🧪                    ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo
echo "📂 Project: n8n-scraper"
echo "🔄 Running: $TEST_CMD"
echo "🎯 Features: Sticky Bottom Bar | Live Spinner | Clean Exit"
echo
sleep 2

# Run the ultimate dashboard
$TEST_CMD

# Show completion message
echo
echo "🎉 Dashboard completed! Press any key to continue..."
read -n 1 -s




