#!/usr/bin/env python3
"""
Setup environment on remote instance.

This script is uploaded to and executed on the remote Vast.ai instance
to set up the Python environment for model evaluation.
"""
import subprocess
import sys

def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    
    packages = [
        "transformers",
        "torch",
        "accelerate",
        "datasets",
        "sentencepiece",  # For some tokenizers
        "protobuf",       # Often needed
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", package],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  [WARNING] Failed to install {package}: {result.stderr}")
        else:
            print(f"  [OK] {package} installed")

def verify_cuda():
    """Verify CUDA is available."""
    print("\nVerifying CUDA...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  [OK] CUDA available")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  GPU count: {torch.cuda.device_count()}")
            return True
        else:
            print("  [WARNING] CUDA not available - using CPU")
            return False
    except ImportError:
        print("  [ERROR] PyTorch not installed")
        return False

def verify_transformers():
    """Verify transformers library is available."""
    print("\nVerifying transformers...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("  [OK] transformers library available")
        return True
    except ImportError as e:
        print(f"  [ERROR] transformers not available: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Remote Environment Setup")
    print("=" * 60)
    
    install_dependencies()
    cuda_ok = verify_cuda()
    transformers_ok = verify_transformers()
    
    print("\n" + "=" * 60)
    if cuda_ok and transformers_ok:
        print("[OK] Environment setup complete!")
    else:
        print("[WARNING] Environment setup completed with warnings")
        sys.exit(1)

