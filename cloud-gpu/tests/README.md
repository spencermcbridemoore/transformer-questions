# Running Tests Locally

These tests are designed to work on **any system with a GPU**, including your local RTX 4090!

## Prerequisites

1. **NVIDIA GPU** (e.g., RTX 4090) with drivers installed
2. **CUDA Toolkit** (optional, but recommended)
3. **Python 3.8+**
4. **PyTorch with CUDA support**

## Quick Setup

1. **Install dependencies**:
   ```bash
   cd cloud-gpu
   pip install -r requirements.txt
   ```

2. **Verify GPU detection**:
   ```bash
   # Should show your RTX 4090
   nvidia-smi
   
   # Should show CUDA info
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
   ```

3. **Run all tests**:
   ```bash
   pytest tests/ -v
   ```

## Test Categories

- **GPU Detection Tests**: Tests `nvidia-smi` and GPU detection
- **CUDA Tests**: Tests CUDA compiler and version
- **PyTorch GPU Tests**: Tests PyTorch CUDA functionality and tensor operations
- **Library Module Tests**: Tests for cloud-gpu library modules
  - `test_vast_manager.py`: VastManager instance lifecycle management
  - `test_remote_executor.py`: RemoteExecutor SSH/SCP utilities
  - `test_model_evaluator.py`: ModelEvaluator helper utilities

## Running Specific Tests

```bash
# Only GPU detection tests
pytest tests/test_gpu_detection.py -v

# Only CUDA tests
pytest tests/test_cuda.py -v

# Only PyTorch GPU tests
pytest tests/test_pytorch_gpu.py -v

# Run with markers
pytest tests/ -m gpu -v        # All GPU tests
pytest tests/ -m pytorch -v    # All PyTorch tests
```

## Test Behavior

- Tests automatically **skip** if no GPU/CUDA/PyTorch is available (safe to run anywhere)
- Tests will **run** if GPU is detected (like your RTX 4090)
- All tests use skip decorators, so they're safe to run on systems without GPUs

## Expected Output on RTX 4090

You should see:
- GPU detection tests passing and showing your RTX 4090
- CUDA tests passing (if CUDA toolkit installed)
- PyTorch tests passing and using your GPU
- Device name showing: "NVIDIA GeForce RTX 4090" (or similar)

## Troubleshooting

**Tests skip unexpectedly:**
- Verify `nvidia-smi` works: `nvidia-smi`
- Check PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Install PyTorch with CUDA: See `requirements.txt` comments

**PyTorch not using GPU:**
- Install PyTorch with CUDA support matching your CUDA version
- Check CUDA version: `nvcc --version`
- Reinstall PyTorch with correct CUDA version

