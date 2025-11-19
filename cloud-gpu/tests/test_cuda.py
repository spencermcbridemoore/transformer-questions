"""Tests for CUDA installation."""
import subprocess
import pytest
from conftest import (
    cuda_available,
    skip_if_no_cuda,
    has_cuda
)


@pytest.mark.cuda
@skip_if_no_cuda
def test_nvcc_exists(cuda_available):
    """Test that nvcc (CUDA compiler) exists."""
    assert cuda_available, "nvcc should be available"
    result = subprocess.run(
        ['nvcc', '--version'],
        capture_output=True,
        text=True,
        check=True,
        timeout=10
    )
    assert result.returncode == 0
    assert 'release' in result.stdout.lower() or 'version' in result.stdout.lower()


@pytest.mark.cuda
@skip_if_no_cuda
def test_cuda_version(cuda_available):
    """Test that we can get CUDA version."""
    assert cuda_available
    result = subprocess.run(
        ['nvcc', '--version'],
        capture_output=True,
        text=True,
        check=True,
        timeout=10
    )
    assert result.returncode == 0
    # Extract version number
    output = result.stdout.lower()
    assert 'release' in output or 'version' in output
    print(f"CUDA version info:\n{result.stdout}")


def test_cuda_detection():
    """Test CUDA detection (runs on all systems)."""
    # This test always runs, just checks detection logic
    has_cuda_installed = has_cuda()
    print(f"CUDA detected: {has_cuda_installed}")
    # Test should pass regardless of CUDA availability

