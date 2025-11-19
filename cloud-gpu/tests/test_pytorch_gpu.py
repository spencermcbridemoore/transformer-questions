"""Tests for PyTorch GPU functionality."""
import pytest
from conftest import (
    pytorch_available,
    pytorch_cuda_available_fixture,
    skip_if_no_pytorch,
    skip_if_no_pytorch_cuda,
    has_pytorch,
    pytorch_cuda_available
)


@pytest.mark.pytorch
@skip_if_no_pytorch
def test_pytorch_import(pytorch_available):
    """Test that PyTorch can be imported."""
    assert pytorch_available
    import torch
    assert torch is not None
    print(f"PyTorch version: {torch.__version__}")


@pytest.mark.pytorch
@skip_if_no_pytorch
def test_pytorch_cuda_available_check(pytorch_available):
    """Test that we can check if CUDA is available to PyTorch."""
    assert pytorch_available
    import torch
    cuda_available = torch.cuda.is_available()
    print(f"PyTorch CUDA available: {cuda_available}")
    # Test passes regardless of CUDA availability
    assert isinstance(cuda_available, bool)


@pytest.mark.pytorch
@skip_if_no_pytorch_cuda
def test_pytorch_cuda_device_count(pytorch_cuda_available_fixture):
    """Test that PyTorch can detect GPU count."""
    assert pytorch_cuda_available_fixture
    import torch
    assert torch.cuda.is_available()
    device_count = torch.cuda.device_count()
    assert device_count > 0, "Should detect at least one GPU"
    print(f"PyTorch detected {device_count} GPU(s)")


@pytest.mark.pytorch
@skip_if_no_pytorch_cuda
def test_pytorch_cuda_device_name(pytorch_cuda_available_fixture):
    """Test that PyTorch can get GPU device name."""
    assert pytorch_cuda_available_fixture
    import torch
    assert torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0)
    assert device_name is not None
    assert len(device_name) > 0
    print(f"GPU 0: {device_name}")


@pytest.mark.pytorch
@skip_if_no_pytorch_cuda
def test_pytorch_tensor_on_gpu(pytorch_cuda_available_fixture):
    """Test that we can create and move tensors to GPU."""
    assert pytorch_cuda_available_fixture
    import torch
    
    # Create a tensor
    x = torch.randn(3, 3)
    assert x.device.type == 'cpu'
    
    # Move to GPU
    x_gpu = x.cuda()
    assert x_gpu.device.type == 'cuda'
    assert x_gpu.device.index == 0
    
    # Verify it's on GPU
    y = x_gpu + 1.0
    assert y.device.type == 'cuda'
    
    print("Successfully created and manipulated tensors on GPU")


@pytest.mark.pytorch
@skip_if_no_pytorch_cuda
def test_pytorch_gpu_computation(pytorch_cuda_available_fixture):
    """Test a simple computation on GPU."""
    assert pytorch_cuda_available_fixture
    import torch
    
    # Create matrices on GPU
    a = torch.randn(1000, 1000, device='cuda')
    b = torch.randn(1000, 1000, device='cuda')
    
    # Matrix multiplication on GPU
    c = torch.matmul(a, b)
    
    assert c.device.type == 'cuda'
    assert c.shape == (1000, 1000)
    
    print("Successfully performed matrix multiplication on GPU")


def test_pytorch_detection():
    """Test PyTorch detection (runs on all systems)."""
    # This test always runs, just checks detection logic
    has_pytorch_installed = has_pytorch()
    print(f"PyTorch detected: {has_pytorch_installed}")
    
    if has_pytorch_installed:
        pytorch_cuda = pytorch_cuda_available()
        print(f"PyTorch CUDA available: {pytorch_cuda}")
    # Test should pass regardless of PyTorch availability

