"""Pytest configuration and fixtures for GPU tests."""
import pytest
import subprocess
import sys


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


# Skip decorators for convenience
skip_if_no_gpu = pytest.mark.skipif(not has_nvidia_smi(), reason="No GPU available")
skip_if_no_cuda = pytest.mark.skipif(not has_cuda(), reason="No CUDA available")
skip_if_no_pytorch = pytest.mark.skipif(not has_pytorch(), reason="PyTorch not installed")
skip_if_no_pytorch_cuda = pytest.mark.skipif(not pytorch_cuda_available(), reason="PyTorch CUDA not available")

