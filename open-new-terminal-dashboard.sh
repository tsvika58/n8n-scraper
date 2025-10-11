#!/bin/bash
# Opens a new terminal tab and runs the dashboard there

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

# Create a script that will run in the new terminal
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'EOF'
#!/bin/bash

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Change to project directory
cd "PROJECT_DIR_PLACEHOLDER"

# Activate venv
source venv/bin/activate

# Clear screen
clear

# Show banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    🧪 NEW TERMINAL DASHBOARD 🧪                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}📂 Project: n8n-scraper${NC}"
echo -e "${YELLOW}🔄 Running: TEST_CMD_PLACEHOLDER${NC}"
echo -e "${CYAN}🎯 Features: Sticky Bottom Bar | Live Spinner | Clean Exit${NC}"
echo
sleep 2

# Run the dashboard
TEST_CMD_PLACEHOLDER

# Show completion
echo
echo -e "${GREEN}🎉 Dashboard completed! Press any key to close this terminal...${NC}"
read -n 1 -s
EOF

# Replace placeholders
sed -i '' "s|PROJECT_DIR_PLACEHOLDER|$PROJECT_DIR|g" "$TEMP_SCRIPT"
sed -i '' "s|TEST_CMD_PLACEHOLDER|$TEST_CMD|g" "$TEMP_SCRIPT"

# Make it executable
chmod +x "$TEMP_SCRIPT"

# Try different methods to open new terminal
if command -v osascript >/dev/null 2>&1; then
    # Method 1: Use osascript to open new terminal
    osascript <<EOF
tell application "Terminal"
    activate
    do script "$TEMP_SCRIPT && rm $TEMP_SCRIPT"
end tell
EOF
elif command -v gnome-terminal >/dev/null 2>&1; then
    # Method 2: Use gnome-terminal (Linux)
    gnome-terminal -- bash -c "$TEMP_SCRIPT && rm $TEMP_SCRIPT; exec bash"
elif command -v xterm >/dev/null 2>&1; then
    # Method 3: Use xterm (Linux)
    xterm -e "bash -c '$TEMP_SCRIPT && rm $TEMP_SCRIPT; exec bash'" &
else
    # Method 4: Fallback - just run in current terminal
    echo "⚠️  Could not open new terminal, running in current terminal..."
    $TEMP_SCRIPT
    rm $TEMP_SCRIPT
fi

echo "✅ Dashboard launched in new terminal!"




