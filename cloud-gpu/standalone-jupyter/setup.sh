#!/bin/bash
# Setup script for Standalone Jupyter on remote GPU machine
# Run this on the remote machine after SSH'ing in

set -e

echo "Setting up Standalone Jupyter environment..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install Python and pip if not present
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt-get install -y python3 python3-pip
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install JupyterLab
echo "Installing JupyterLab..."
pip3 install jupyterlab jupyter

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other common ML libraries
echo "Installing additional dependencies..."
pip3 install numpy pandas matplotlib scipy scikit-learn

# Install pytest and testing tools
echo "Installing pytest..."
pip3 install pytest pytest-cov

# Create Jupyter config directory
JUPYTER_CONFIG_DIR="$HOME/.jupyter"
mkdir -p "$JUPYTER_CONFIG_DIR"

# Copy jupyter config if not exists
if [ ! -f "$JUPYTER_CONFIG_DIR/jupyter_lab_config.py" ]; then
    echo "Creating Jupyter configuration..."
    cat > "$JUPYTER_CONFIG_DIR/jupyter_lab_config.py" << 'EOF'
# JupyterLab configuration for remote access
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_origin = '*'
c.ServerApp.allow_root = False
c.ServerApp.token = ''
c.ServerApp.password = ''
# Allow Colab connection if needed
c.ServerApp.allow_origin_pat = 'https://.*\.colab\.research\.google\.com'
EOF
fi

# Add local bin to PATH (for Jupyter)
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: bash start-jupyter.sh"
echo "2. Note the URL with token"
echo "3. Create SSH tunnel on local machine:"
echo "   Windows: .\\tunnel.ps1 -Host your-host -Port 8888"
echo "   Linux/Mac: bash tunnel.sh your-host 8888"
echo "4. Open browser to http://localhost:8888"

