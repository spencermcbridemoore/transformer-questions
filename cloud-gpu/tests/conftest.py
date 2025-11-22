"""Pytest configuration and fixtures for cloud-gpu tests."""
import pytest
import subprocess
import sys
import os
from pathlib import Path

# Add lib directory to path for imports
lib_path = Path(__file__).parent.parent / 'lib'
sys.path.insert(0, str(lib_path))


def has_nvidia_smi():
    """Check if nvidia-smi is available."""
    try:
        subprocess.run(['nvidia-smi'], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def has_cuda():
    """Check if CUDA is available."""
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def has_pytorch():
    """Check if PyTorch is installed."""
    try:
        import torch
        return True
    except ImportError:
        return False


def pytorch_cuda_available():
    """Check if PyTorch can access CUDA."""
    if not has_pytorch():
        return False
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def has_vast_api_key():
    """Check if Vast.ai API key is available."""
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('VAST_API_KEY')
    return api_key and api_key != 'your_vast_api_key_here'


@pytest.fixture(scope="session")
def gpu_available():
    """Fixture to check if GPU is available."""
    return has_nvidia_smi()


@pytest.fixture(scope="session")
def cuda_available():
    """Fixture to check if CUDA is available."""
    return has_cuda()


@pytest.fixture(scope="session")
def pytorch_available():
    """Fixture to check if PyTorch is available."""
    return has_pytorch()


@pytest.fixture(scope="session")
def pytorch_cuda_available_fixture():
    """Fixture to check if PyTorch can use CUDA."""
    return pytorch_cuda_available()


@pytest.fixture(scope="session")
def vast_api_key():
    """Fixture to get Vast.ai API key."""
    if not has_vast_api_key():
        pytest.skip("VAST_API_KEY not found in environment")
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('VAST_API_KEY')
    return api_key


# Skip decorators for convenience
skip_if_no_gpu = pytest.mark.skipif(not has_nvidia_smi(), reason="No GPU available")
skip_if_no_cuda = pytest.mark.skipif(not has_cuda(), reason="No CUDA available")
skip_if_no_pytorch = pytest.mark.skipif(not has_pytorch(), reason="PyTorch not installed")
skip_if_no_pytorch_cuda = pytest.mark.skipif(not pytorch_cuda_available(), reason="PyTorch CUDA not available")
skip_if_no_vast_api = pytest.mark.skipif(not has_vast_api_key(), reason="Vast.ai API key not found")

# Markers
vast_marker = pytest.mark.vast
