#!/bin/bash
# Opens dashboard in a NEW Cursor terminal tab (not chat output)

# Get the project directory
PROJECT_DIR="/Users/tsvikavagman/Desktop/Code Projects/shared-tools/n8n-scraper"

# Parse arguments
TEST_ARGS="$@"

# If no args provided, use default
if [ -z "$TEST_ARGS" ]; then
    TEST_ARGS="-v --cov=src --cov-report=term-missing"
fi

# Create a temporary script that will run in the new terminal
TEMP_SCRIPT=$(mktemp /tmp/cursor-dash.XXXXXX.sh)
cat > "$TEMP_SCRIPT" << EOF
#!/bin/bash
cd "$PROJECT_DIR"
source venv/bin/activate
clear
python pytest-dashboard-visible.py $TEST_ARGS
echo ""
echo "🎉 Tests completed! Press any key to close this terminal..."
read -n 1 -s
EOF

chmod +x "$TEMP_SCRIPT"

# Use AppleScript to tell Cursor to open a new terminal and run our script
osascript <<APPLESCRIPT
tell application "Cursor"
    activate
    delay 0.3
    
    -- Open new terminal using Cmd+Shift+' (backtick)
    tell application "System Events"
        key code 50 using {command down, shift down}
    end tell
    
    delay 0.5
    
    -- Type the command to run our script
    tell application "System Events"
        keystroke "$TEMP_SCRIPT"
        delay 0.2
        key code 36 -- Press Enter
    end tell
end tell
APPLESCRIPT

# Clean up temp script after a delay (give it time to execute)
(sleep 15 && rm -f "$TEMP_SCRIPT") &

echo "✅ Dashboard launched in new Cursor terminal tab!"
echo "📺 Look for the new terminal tab at the bottom of Cursor"





