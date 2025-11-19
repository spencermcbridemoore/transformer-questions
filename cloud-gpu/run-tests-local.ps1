# PowerShell script to run tests on local GPU
# Usage: .\run-tests-local.ps1

Write-Host "Running GPU tests on local machine..." -ForegroundColor Cyan
Write-Host ""

# Check if nvidia-smi is available
Write-Host "Checking for GPU..." -ForegroundColor Yellow
try {
    $nvidiaSmi = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ GPU detected!" -ForegroundColor Green
        Write-Host $nvidiaSmi | Select-Object -First 5
        Write-Host ""
    }
} catch {
    Write-Host "✗ nvidia-smi not found" -ForegroundColor Red
    Write-Host ""
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check PyTorch CUDA
Write-Host "Checking PyTorch CUDA..." -ForegroundColor Yellow
try {
    $pytorchCheck = python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" 2>&1
    Write-Host $pytorchCheck
    Write-Host ""
} catch {
    Write-Host "✗ PyTorch not installed or error checking CUDA" -ForegroundColor Yellow
    Write-Host ""
}

# Check pytest
Write-Host "Checking pytest..." -ForegroundColor Yellow
try {
    $pytestVersion = python -m pytest --version 2>&1
    Write-Host "✓ $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ pytest not installed" -ForegroundColor Red
    Write-Host "Install with: pip install pytest" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Run tests
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

python -m pytest tests/ -v

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Tests complete!" -ForegroundColor Green

