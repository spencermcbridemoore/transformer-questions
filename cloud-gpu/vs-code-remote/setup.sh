#!/bin/bash
# Setup script for VS Code Remote + Jupyter on remote GPU machine
# Run this on the remote machine after SSH'ing in

set -e

echo "Setting up VS Code Remote + Jupyter environment..."

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

# Install Jupyter
echo "Installing Jupyter..."
pip3 install jupyter jupyterlab

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other common ML libraries
echo "Installing additional dependencies..."
pip3 install numpy pandas matplotlib scipy scikit-learn

# Install pytest and testing tools
echo "Installing pytest..."
pip3 install pytest pytest-cov

# Add local bin to PATH (for Jupyter)
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure SSH on your local machine (see ssh-config.example)"
echo "2. Connect with VS Code Remote-SSH extension"
echo "3. Open this directory on the remote"
echo "4. Run tests: pytest tests/ -v"

