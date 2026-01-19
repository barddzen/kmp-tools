#!/bin/bash
# Generate App Store screenshots with Claude Vision analysis
# Run from any KMP project directory
#
# Usage:
#   kmp-screenshots.sh --analyze      # Analyze and generate config
#   kmp-screenshots.sh --generate     # Generate from config
#   kmp-screenshots.sh --auto         # Both in one shot
#   kmp-screenshots.sh --auto --preserve-names  # Skip auto-ordering

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure we're in a git repo (proxy for being in a project)
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    echo "Run this from a KMP project directory"
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")
SCREENSHOTS_DIR="$PROJECT_ROOT/assets/screenshots"

echo ""
echo "Project: $PROJECT_NAME"
echo "Screenshots: $SCREENSHOTS_DIR"

# Check if screenshots directory exists
if [ ! -d "$SCREENSHOTS_DIR" ]; then
    echo ""
    echo "Error: Screenshots directory not found"
    echo "Create with: mkdir -p assets/screenshots/Input/{android,ios_iphone,ios_ipad}"
    exit 1
fi

# Check for Python and required modules
if ! python3 -c "from PIL import Image" 2>/dev/null; then
    echo ""
    echo "Error: Pillow not installed"
    echo "Install with: pip3 install Pillow"
    exit 1
fi

if ! python3 -c "from anthropic import Anthropic" 2>/dev/null; then
    echo ""
    echo "Error: anthropic not installed"
    echo "Install with: pip3 install anthropic"
    exit 1
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "Error: ANTHROPIC_API_KEY not set"
    exit 1
fi

# Run the pipeline
cd "$SCRIPT_DIR"
python3 screenshot_pipeline.py --base-dir "$SCREENSHOTS_DIR" "$@"
