#!/bin/bash
# Bash script to run tests on local GPU
# Usage: bash run-tests-local.sh

echo "Running GPU tests on local machine..."
echo ""

# Check if nvidia-smi is available
echo "Checking for GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ GPU detected!"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
    echo ""
else
    echo "✗ nvidia-smi not found"
    echo ""
fi

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    echo ""
else
    echo "✗ Python not found"
    exit 1
fi

# Check PyTorch CUDA
echo "Checking PyTorch CUDA..."
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>/dev/null || echo "✗ PyTorch not installed or error checking CUDA"
echo ""

# Check pytest
echo "Checking pytest..."
if python3 -m pytest --version &> /dev/null; then
    python3 -m pytest --version
else
    echo "✗ pytest not installed"
    echo "Install with: pip install pytest"
    exit 1
fi
echo ""

# Run tests
echo "Running tests..."
echo "============================================================"
echo ""

python3 -m pytest tests/ -v

echo ""
echo "============================================================"
echo "Tests complete!"

