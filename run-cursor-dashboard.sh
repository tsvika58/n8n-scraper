#!/bin/bash
# Simple approach - just run the dashboard and let user manually open new terminal

# Get the project directory
PROJECT_DIR="/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"

# Parse arguments
TEST_ARGS="$@"

# If no args provided, use default
if [ -z "$TEST_ARGS" ]; then
    TEST_CMD="python pytest-dashboard-visible.py -v --cov=src --cov-report=term-missing"
else
    TEST_CMD="python pytest-dashboard-visible.py $TEST_ARGS"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Activate venv
source venv/bin/activate

# Clear screen
clear

# Show instructions
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                🧪 CURSOR TERMINAL DASHBOARD 🧪                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo
echo "📂 Project: n8n-scraper"
echo "🔄 Running: $TEST_CMD"
echo "🎯 Features: Sticky Bottom Bar | Live Spinner | Clean Exit"
echo
echo "💡 INSTRUCTIONS:"
echo "   1. Press Ctrl+Shift+\` to open a new terminal in Cursor"
echo "   2. Copy and paste this command:"
echo "      $TEST_CMD"
echo "   3. Press Enter to run the dashboard"
echo
echo "   Or press Enter here to run in current terminal..."
read -n 1 -s

# Run the dashboard
$TEST_CMD

# Show completion
echo
echo "🎉 Dashboard completed!"




