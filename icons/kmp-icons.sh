#!/bin/bash
# Generate iOS and Android icons from a single source image
# Run from any KMP project directory
#
# Usage: kmp-icons.sh <source_image.png>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure we're in a git repo (proxy for being in a project)
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    echo "Run this from a KMP project directory"
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")

if [ -z "$1" ]; then
    echo "Error: Source image required"
    echo ""
    echo "Usage: kmp-icons.sh <source_image.png>"
    echo ""
    echo "Example:"
    echo "  kmp-icons.sh assets/icons/my-icon.png"
    exit 1
fi

SOURCE_IMAGE="$1"

# Handle relative paths
if [[ ! "$SOURCE_IMAGE" = /* ]]; then
    SOURCE_IMAGE="$PROJECT_ROOT/$SOURCE_IMAGE"
fi

if [ ! -f "$SOURCE_IMAGE" ]; then
    echo "Error: Image not found: $SOURCE_IMAGE"
    exit 1
fi

echo ""
echo "Project: $PROJECT_NAME"

# Check for Python and Pillow
if ! python3 -c "from PIL import Image" 2>/dev/null; then
    echo ""
    echo "Error: Pillow not installed"
    echo "Install with: pip3 install Pillow"
    exit 1
fi

# Run the generator
cd "$SCRIPT_DIR"
python3 generate_icons.py "$PROJECT_ROOT" "$SOURCE_IMAGE"
