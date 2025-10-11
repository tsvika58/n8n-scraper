#!/bin/bash
# Opens a new terminal in Cursor IDE and runs tests there
# This ensures tests always have a dedicated, focused terminal window

# Get the project directory
PROJECT_DIR="/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"

# Parse arguments to determine which test command to run
TEST_ARGS="$@"

# If no args provided, use default
if [ -z "$TEST_ARGS" ]; then
    TEST_CMD="./test-with-timer.sh -v --cov=src --cov-report=term-missing"
else
    TEST_CMD="./test-with-timer.sh $TEST_ARGS"
fi

# Create a temporary script that will run in the new terminal
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'SCRIPT_END'
#!/bin/bash

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Change to project directory
cd "PROJECT_DIR_PLACEHOLDER"

# Clear screen for clean output
clear

# Show banner
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                   🧪 Pytest Dashboard - New Terminal                 ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}📂 Project: n8n-scraper${NC}"
echo -e "${YELLOW}🔄 Running: TEST_CMD_PLACEHOLDER${NC}"
echo
sleep 1

# Run the test command
TEST_CMD_PLACEHOLDER

# Keep terminal open after tests complete
echo
echo -e "${GREEN}Press any key to close this terminal...${NC}"
read -n 1 -s
SCRIPT_END

# Replace placeholders
sed -i '' "s|PROJECT_DIR_PLACEHOLDER|$PROJECT_DIR|g" "$TEMP_SCRIPT"
sed -i '' "s|TEST_CMD_PLACEHOLDER|$TEST_CMD|g" "$TEMP_SCRIPT"

# Make it executable
chmod +x "$TEMP_SCRIPT"

# Use AppleScript to open a new terminal in Cursor and run the command
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

echo "✅ Tests launched in new Cursor terminal"





