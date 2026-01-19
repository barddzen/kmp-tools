#!/bin/bash
# Show current status and recent history
# Run from any git repository directory

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")

echo "📁 Project: $PROJECT_NAME"
echo ""

echo "📊 Git Status"
echo "════════════════════════════════════════"
git status -s
echo ""

echo "📝 Recent Commits (last 5)"
echo "════════════════════════════════════════"
git log --oneline -5
echo ""

echo "🏷️  Recent Tags (last 5)"
echo "════════════════════════════════════════"
git tag -l | tail -5
echo ""

echo "🌿 Current Branch"
echo "════════════════════════════════════════"
git branch --show-current
echo ""

echo "🔄 Uncommitted Changes"
echo "════════════════════════════════════════"
git diff --stat
