#!/bin/bash
# Push everything - commits, tags, and pushes to both remotes
# Run from any git repository directory

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

PROJECT_ROOT=$(git rev-parse --show-toplevel)
PROJECT_NAME=$(basename "$PROJECT_ROOT")

echo "Project: $PROJECT_NAME"
echo "Pushing commits and tags to remotes..."
echo ""

# Check if there are uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "Warning: You have uncommitted changes!"
    git status -s
    echo ""
    read -p "Continue push anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Push cancelled"
        exit 1
    fi
fi

# Push commits to origin (GitHub)
echo "Pushing to origin (GitHub)..."
git push origin

# Wake up SMB mount before NAS operations (prevents stale socket errors)
if [[ -d "/Volumes/git" ]]; then
    ls /Volumes/git > /dev/null 2>&1
    sleep 0.5
fi

# Push commits to YutzyNAS (Synology)
echo "Pushing to YutzyNAS (Synology)..."
if git remote | grep -q YutzyNAS; then
    git push YutzyNAS || echo "Warning: YutzyNAS push failed (NAS may be offline)"
else
    echo "Warning: YutzyNAS remote not configured"
fi

echo ""

# Push tags to both remotes
echo "Pushing tags to origin..."
git push origin --tags

echo "Pushing tags to YutzyNAS..."
if git remote | grep -q YutzyNAS; then
    git push YutzyNAS --tags || echo "Warning: YutzyNAS tags push failed"
fi

echo ""
echo "Push complete!"
echo ""
echo "Remote status:"
git log --oneline -3
