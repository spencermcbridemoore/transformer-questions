#!/bin/bash
# Start JupyterLab server on remote GPU machine
# Run this on the remote machine after setup.sh

set -e

echo "Starting JupyterLab server..."

# Check if Jupyter is installed
if ! command -v jupyter &> /dev/null; then
    echo "Error: Jupyter not found. Please run setup.sh first."
    exit 1
fi

# Ensure local bin is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to project root
cd "$PROJECT_ROOT"

# Start JupyterLab
echo "Starting JupyterLab on port 8888..."
echo ""
echo "IMPORTANT:"
echo "1. Note the URL with token below"
echo "2. Create SSH tunnel on your local machine:"
echo "   Windows: .\\tunnel.ps1 -Host your-host -Port 8888"
echo "   Linux/Mac: bash tunnel.sh your-host 8888"
echo "   Or manually: ssh -L 8888:localhost:8888 your-host"
echo "3. Open browser to http://localhost:8888"
echo ""
echo "Press Ctrl+C to stop JupyterLab"
echo ""

# Start JupyterLab with configuration
jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root=false \
    --NotebookApp.token='' \
    --NotebookApp.allow_origin='*' \
    --NotebookApp.open_browser=False

