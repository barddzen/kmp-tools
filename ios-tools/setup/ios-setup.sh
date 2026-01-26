#!/bin/bash
# Setup a new iOS-only Xcode project with git, GitHub, NAS remotes, and assets folder
# Usage: ios-setup.sh "ProjectName"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$1" ]; then
    echo "Error: Project name required"
    echo "Usage: ios-setup.sh \"ProjectName\""
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_PATH="$HOME/Development/$PROJECT_NAME"
NAS_PATH="/Volumes/git"
GITHUB_USER="barddzen"

echo ""
echo "Setting up iOS project: $PROJECT_NAME"
echo "========================================"
echo ""

# Step 1: Create local folder
if [ -d "$PROJECT_PATH" ]; then
    echo "Folder $PROJECT_PATH already exists, skipping..."
else
    echo "Creating $PROJECT_PATH..."
    mkdir -p "$PROJECT_PATH"
fi

cd "$PROJECT_PATH"

# Step 2: Initialize git
if [ -d ".git" ]; then
    echo "Git repo already initialized, skipping..."
else
    echo "Initializing git repo..."
    git init
fi

# Step 3: Create assets folder structure (iOS-only, no android folder)
echo "Setting up assets folder structure..."
mkdir -p assets/icons
mkdir -p assets/screenshots/Input/ios_iphone
mkdir -p assets/screenshots/Input/ios_ipad
mkdir -p assets/screenshots/Output
echo "   - assets/icons/"
echo "   - assets/screenshots/Input/{ios_iphone,ios_ipad}/"
echo "   - assets/screenshots/Output/"

# Step 4: Create README if no files exist
if [ ! -f "README.md" ]; then
    echo "Creating README.md..."
    echo "# $PROJECT_NAME" > README.md
    echo "" >> README.md
    echo "iOS application built with Xcode/Swift." >> README.md
fi

# Step 5: Create .gitignore for iOS projects
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Xcode
build/
DerivedData/
*.xcuserstate
*.xcscmblueprint
*.xccheckout

# User-specific Xcode files
xcuserdata/

# CocoaPods
Pods/

# Swift Package Manager
.build/
.swiftpm/

# Carthage
Carthage/Build/

# fastlane
fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots/**/*.png
fastlane/test_output

# macOS
.DS_Store
*.swp
*~

# Archives
*.ipa
*.dSYM.zip
*.dSYM

# Playgrounds
timeline.xctimeline
playground.xcworkspace
EOF
fi

# Step 6: Create .gitkeep files to preserve empty directories
touch assets/icons/.gitkeep
touch assets/screenshots/Input/ios_iphone/.gitkeep
touch assets/screenshots/Input/ios_ipad/.gitkeep
touch assets/screenshots/Output/.gitkeep

# Step 7: NAS bare repo
echo ""
DEFAULT_NAS_NAME="$PROJECT_NAME-iOS"
read -p "NAS repo name? [$DEFAULT_NAS_NAME]: " NAS_NAME
NAS_NAME="${NAS_NAME:-$DEFAULT_NAS_NAME}"
NAS_REPO_PATH="$NAS_PATH/$NAS_NAME.git"

# Wake up SMB mount
if [[ -d "$NAS_PATH" ]]; then
    ls "$NAS_PATH" > /dev/null 2>&1
    sleep 0.5
fi

if [ -d "$NAS_REPO_PATH" ]; then
    echo "NAS repo $NAS_REPO_PATH already exists, skipping..."
else
    if [ -d "$NAS_PATH" ]; then
        echo "Creating NAS bare repo at $NAS_REPO_PATH..."
        git init --bare "$NAS_REPO_PATH"
    else
        echo "Warning: NAS not mounted at $NAS_PATH, skipping NAS repo creation..."
    fi
fi

# Step 8: GitHub repo
echo ""
read -p "GitHub repo name? [$PROJECT_NAME]: " GITHUB_NAME
GITHUB_NAME="${GITHUB_NAME:-$PROJECT_NAME}"

if gh repo view "$GITHUB_USER/$GITHUB_NAME" > /dev/null 2>&1; then
    echo "GitHub repo $GITHUB_USER/$GITHUB_NAME already exists, skipping..."
else
    echo "Creating GitHub repo $GITHUB_USER/$GITHUB_NAME..."
    read -p "   Make repo private? (Y/n): " PRIVATE_CHOICE

    # Check if we have commits to push
    if git rev-parse HEAD > /dev/null 2>&1; then
        # Has commits, use --push
        if [[ "$PRIVATE_CHOICE" =~ ^[Nn]$ ]]; then
            gh repo create "$GITHUB_USER/$GITHUB_NAME" --public --source=. --push
        else
            gh repo create "$GITHUB_USER/$GITHUB_NAME" --private --source=. --push
        fi
    else
        # No commits yet, create repo without --push
        if [[ "$PRIVATE_CHOICE" =~ ^[Nn]$ ]]; then
            gh repo create "$GITHUB_USER/$GITHUB_NAME" --public
        else
            gh repo create "$GITHUB_USER/$GITHUB_NAME" --private
        fi
    fi
fi

# Step 9: Configure remotes
echo ""
echo "Configuring remotes..."

if git remote | grep -q "^origin$"; then
    echo "   - origin already configured"
else
    echo "   - Adding origin (GitHub)..."
    git remote add origin "https://github.com/$GITHUB_USER/$GITHUB_NAME.git"
fi

if git remote | grep -q "^YutzyNAS$"; then
    echo "   - YutzyNAS already configured"
else
    if [ -d "$NAS_REPO_PATH" ]; then
        echo "   - Adding YutzyNAS..."
        git remote add YutzyNAS "$NAS_REPO_PATH"
    else
        echo "   - Skipping YutzyNAS (NAS repo not available)"
    fi
fi

# Step 10: Initial commit if needed
if ! git rev-parse HEAD > /dev/null 2>&1; then
    echo ""
    "$SCRIPT_DIR/../git/ios-commit.sh" "Initial commit"
fi

# Step 11: Push to remotes
echo ""
"$SCRIPT_DIR/../git/ios-push.sh"

echo ""
echo "iOS Project $PROJECT_NAME is ready!"
echo ""
echo "Location: $PROJECT_PATH"
echo "GitHub:   https://github.com/$GITHUB_USER/$GITHUB_NAME"
if [ -d "$NAS_REPO_PATH" ]; then
    echo "NAS:      $NAS_REPO_PATH"
fi
echo ""
echo "Assets structure created:"
echo "  assets/icons/           <- Put source icon here"
echo "  assets/screenshots/     <- Put screenshots in Input/{ios_iphone,ios_ipad}"
echo ""
echo "Next steps:"
echo "  1. Create Xcode project in this folder (or move existing one)"
echo "  2. Add your icon: ios-icons.sh assets/icons/your-icon.png"
echo "  3. Add screenshots: ios-screenshots.sh --auto"
