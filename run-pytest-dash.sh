#!/bin/bash
# Convenient wrapper to run pytest-dashboard with venv activated

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate venv and run dashboard with all arguments passed through
cd "$SCRIPT_DIR"
source venv/bin/activate
python pytest-dashboard.py "$@"





