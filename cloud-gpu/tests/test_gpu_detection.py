"""Tests for GPU detection."""
import subprocess
import pytest
from conftest import (
    gpu_available,
    skip_if_no_gpu,
    has_nvidia_smi
)


@pytest.mark.gpu
@skip_if_no_gpu
def test_nvidia_smi_exists(gpu_available):
    """Test that nvidia-smi command exists and works."""
    assert gpu_available, "nvidia-smi should be available"
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, check=True, timeout=10)
    assert result.returncode == 0
    assert 'NVIDIA-SMI' in result.stdout


@pytest.mark.gpu
@skip_if_no_gpu
def test_gpu_count(gpu_available):
    """Test that we can get GPU count."""
    assert gpu_available
    result = subprocess.run(
        ['nvidia-smi', '--list-gpus'],
        capture_output=True,
        text=True,
        check=True,
        timeout=10
    )
    assert result.returncode == 0
    gpu_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]
    assert len(gpu_lines) > 0, "Should detect at least one GPU"
    print(f"Detected {len(gpu_lines)} GPU(s)")


@pytest.mark.gpu
@skip_if_no_gpu
def test_gpu_info(gpu_available):
    """Test that we can get GPU information."""
    assert gpu_available
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
        capture_output=True,
        text=True,
        check=True,
        timeout=10
    )
    assert result.returncode == 0
    lines = result.stdout.strip().split('\n')
    assert len(lines) > 0, "Should get GPU information"
    
    for line in lines:
        parts = line.split(', ')
        assert len(parts) >= 2, f"GPU info should have name and memory: {line}"
        print(f"GPU: {parts[0]}, Memory: {parts[1]}")


def test_nvidia_smi_detection():
    """Test nvidia-smi detection (runs on all systems)."""
    # This test always runs, just checks detection logic
    has_gpu = has_nvidia_smi()
    print(f"nvidia-smi detected: {has_gpu}")
    # Test should pass regardless of GPU availability

