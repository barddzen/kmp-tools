#!/bin/bash
# Quick commit - stages all changes and commits with a message
# Run from any git repository directory

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Get repo root (in case we're in a subdirectory)
PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")

if [ -z "$1" ]; then
    echo "❌ Error: Commit message required"
    echo "Usage: commit.sh \"your commit message\""
    exit 1
fi

echo "📁 Project: $PROJECT_NAME"
echo "📝 Staging all changes..."
git add .

# Double-check critical KMP files are staged
echo "📦 Verifying critical files..."
git add -f "$PROJECT_ROOT/composeApp/build.gradle.kts" 2>/dev/null || true
git add -f "$PROJECT_ROOT/shared/build.gradle.kts" 2>/dev/null || true
git add -f "$PROJECT_ROOT/gradle.properties" 2>/dev/null || true
git add -f "$PROJECT_ROOT/settings.gradle.kts" 2>/dev/null || true

echo "💾 Committing..."
git commit -m "$1"

echo "✅ Commit complete!"
echo ""
git log -1 --oneline

# Show what was committed
echo ""
echo "📊 Files committed:"
git diff-tree --no-commit-id --name-only -r HEAD | head -30
