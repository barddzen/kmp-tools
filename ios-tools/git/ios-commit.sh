#!/bin/bash
# Quick commit for iOS-only Xcode projects
# Stages all changes and commits with a message
# Run from any git repository directory

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get repo root (in case we're in a subdirectory)
PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")

if [ -z "$1" ]; then
    echo "Error: Commit message required"
    echo "Usage: ios-commit.sh \"your commit message\""
    exit 1
fi

echo "Project: $PROJECT_NAME"
echo "Staging all changes..."
git add .

# Force-stage critical iOS project files (in case .gitignore is overly aggressive)
echo "Verifying critical iOS files..."

# Find and stage .xcodeproj files
find "$PROJECT_ROOT" -maxdepth 2 -name "*.xcodeproj" -type d | while read xcproj; do
    git add -f "$xcproj/project.pbxproj" 2>/dev/null || true
    git add -f "$xcproj/project.xcworkspace/contents.xcworkspacedata" 2>/dev/null || true
    git add -f "$xcproj/xcshareddata" 2>/dev/null || true
done

# Stage Assets.xcassets (icons, colors, images)
find "$PROJECT_ROOT" -name "Assets.xcassets" -type d | while read assets; do
    git add -f "$assets" 2>/dev/null || true
done

# Stage storyboards and XIBs
git add -f "$PROJECT_ROOT"/**/*.storyboard 2>/dev/null || true
git add -f "$PROJECT_ROOT"/**/*.xib 2>/dev/null || true

# Stage SpriteKit/SceneKit files
git add -f "$PROJECT_ROOT"/**/*.sks 2>/dev/null || true
git add -f "$PROJECT_ROOT"/**/*.scn 2>/dev/null || true

echo "Committing..."
git commit -m "$1"

echo "Commit complete!"
echo ""
git log -1 --oneline

# Show what was committed
echo ""
echo "Files committed:"
git diff-tree --no-commit-id --name-only -r HEAD | head -30
