#!/bin/bash
# Opens a new terminal WITHIN Cursor IDE and runs the dashboard there

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

# Create a script that will run in the new Cursor terminal
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
echo -e "${BLUE}║                🧪 CURSOR TERMINAL DASHBOARD 🧪                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}📂 Project: n8n-scraper${NC}"
echo -e "${YELLOW}🔄 Running: TEST_CMD_PLACEHOLDER${NC}"
echo -e "${CYAN}🎯 Features: Sticky Bottom Bar | Live Spinner | Clean Exit${NC}"
echo -e "${GREEN}✅ Running in Cursor IDE Terminal${NC}"
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

# Use AppleScript to open new terminal IN CURSOR
osascript <<EOF
tell application "Cursor"
    activate
    delay 0.5
    
    -- Use keyboard shortcut to open new terminal (Ctrl+Shift+`)
    tell application "System Events"
        keystroke "\`" using {control down, shift down}
    end tell
    
    delay 1
    
    -- Type the command to run our script
    tell application "System Events"
        keystroke "$TEMP_SCRIPT && rm $TEMP_SCRIPT"
        keystroke return
    end tell
end tell
EOF

echo "✅ Dashboard launched in new Cursor terminal!"




