#!/bin/bash
# Utility script to extract a pet project to its own git repository
# Usage: ./scripts/extract-project.sh <project-name>
#
# This will:
# 1. Create a new directory at ../<project-name>
# 2. Copy the project directory
# 3. Initialize a new git repository
# 4. Make an initial commit
# 5. Optionally push to GitHub

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <project-name>"
    echo ""
    echo "Extract a pet project to its own git repository."
    echo ""
    echo "Example:"
    echo "  $0 cloud-gpu"
    echo ""
    exit 1
fi

PROJECT_NAME=$1
PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
SOURCE_DIR="$PROJECT_DIR/$PROJECT_NAME"
TARGET_DIR="$(dirname "$PROJECT_DIR")/$PROJECT_NAME"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Project directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Check if target directory already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Error: Target directory '$TARGET_DIR' already exists"
    echo "Please remove it first or choose a different name"
    exit 1
fi

echo "Extracting project: $PROJECT_NAME"
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Copy the project directory
echo "Copying files..."
cp -r "$SOURCE_DIR" "$TARGET_DIR"

# Initialize git repository
echo "Initializing git repository..."
cd "$TARGET_DIR"
git init
git add .
git commit -m "Initial commit: Extract $PROJECT_NAME from transformer-questions"

echo ""
echo "✓ Project extracted successfully!"
echo ""
echo "Next steps:"
echo "1. Review the extracted project: cd $TARGET_DIR"
echo "2. Create a GitHub repository (if desired)"
echo "3. Add remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/$PROJECT_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Note: Git history from the parent repo is not preserved."
echo "If you need history, consider using git subtree or git filter-branch."

