# Cloud GPU Jupyter Setup

Complete setup for running Jupyter notebooks on remote H100 GPUs (like Hyperbolic). This project supports two different workflows:

1. **VS Code Remote + Jupyter**: Use VS Code/Cursor with Remote-SSH extension to connect and run notebooks
2. **Standalone Jupyter**: Use JupyterLab in your browser via SSH tunnel

## Prerequisites

- Access to a remote H100 GPU instance (e.g., from Hyperbolic)
- SSH access to the remote machine
- Local machine with SSH client installed
- Python 3.8+ on the remote machine

## Quick Start

### VS Code Remote + Jupyter

1. **Configure SSH** (on your local machine):
   ```bash
   # Copy the SSH config template and edit with your details
   cp cloud-gpu/vs-code-remote/ssh-config.example ~/.ssh/config
   # Edit ~/.ssh/config with your remote host details
   ```

2. **Setup Remote Environment**:
   ```bash
   # SSH into your remote machine
   ssh your-remote-host
   
   # Run the setup script
   cd cloud-gpu/vs-code-remote
   bash setup.sh
   ```

3. **Connect with VS Code**:
   - Install Remote-SSH extension in VS Code/Cursor
   - Open Command Palette (Ctrl+Shift+P)
   - Select "Remote-SSH: Connect to Host"
   - Choose your configured host
   - Open the `cloud-gpu` folder on the remote

4. **Run Tests**:
   ```bash
   pytest tests/
   ```

### Standalone Jupyter

1. **Setup Jupyter on Remote**:
   ```bash
   # SSH into your remote machine
   ssh your-remote-host
   
   # Run the setup script
   cd cloud-gpu/standalone-jupyter
   bash setup.sh
   ```

2. **Start JupyterLab**:
   ```bash
   bash start-jupyter.sh
   # Note the URL with token that appears
   ```

3. **Create SSH Tunnel** (on your local machine):
   
   **Windows (PowerShell):**
   ```powershell
   .\cloud-gpu\standalone-jupyter\tunnel.ps1 -Host your-remote-host -Port 8888
   ```
   
   **Linux/Mac:**
   ```bash
   bash cloud-gpu/standalone-jupyter/tunnel.sh your-remote-host 8888
   ```
   
   Or manually:
   ```bash
   ssh -L 8888:localhost:8888 your-remote-host
   ```

4. **Access Jupyter**:
   - Open browser to `http://localhost:8888`
   - Use the token from step 2

5. **Run Tests**:
   Create a new notebook and run:
   ```python
   !pytest /path/to/cloud-gpu/tests/ -v
   ```

## Testing

### Running Tests Locally (e.g., on your RTX 4090)

**Yes! These tests work perfectly on local GPUs** like your RTX 4090. They automatically detect and use any available GPU.

**Quick start for local testing:**

1. **Install dependencies**:
   ```bash
   cd cloud-gpu
   pip install -r requirements.txt
   ```

2. **Run tests**:
   ```bash
   # Windows (PowerShell)
   .\run-tests-local.ps1
   
   # Linux/Mac
   bash run-tests-local.sh
   
   # Or directly with pytest
   pytest tests/ -v
   ```

The tests will:
- ✓ Detect your RTX 4090 via `nvidia-smi`
- ✓ Test CUDA functionality (if CUDA toolkit installed)
- ✓ Test PyTorch GPU operations on your local GPU
- ✓ Skip gracefully if no GPU is available (safe anywhere)

See `tests/README.md` for detailed testing information.

### Running Tests on Remote GPU

All tests can be run with pytest:

```bash
pytest tests/ -v
```

Tests will automatically skip if no GPU is available, so they're safe to run on any machine.

## Examples

- `examples/gpu_info.py`: Script to display GPU information
- `examples/example-notebook.ipynb`: Sample Jupyter notebook with GPU detection

## Troubleshooting

### VS Code Remote Issues

- **Connection fails**: Check SSH config and ensure SSH keys are set up
- **Python not found**: Make sure Python is in PATH on remote, or set `python.defaultInterpreterPath` in workspace settings
- **Jupyter not found**: Run the setup script on the remote

### Standalone Jupyter Issues

- **Tunnel disconnects**: Keep the SSH tunnel terminal open
- **Can't connect**: Check that Jupyter is running and tunnel is active
- **Token expired**: Restart Jupyter and use the new token

### GPU Not Detected

- Verify NVIDIA drivers are installed: `nvidia-smi`
- Check CUDA is available: `nvcc --version`
- For PyTorch: `python -c "import torch; print(torch.cuda.is_available())"`

## Dependencies

See `requirements.txt` for all Python dependencies. Install with:

```bash
pip install -r requirements.txt
```

