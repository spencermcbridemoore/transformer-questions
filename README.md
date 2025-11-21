# transformer-questions

A collection of pet projects and experiments. This repository serves as a playground for trying out ideas, and when a project matures, it can be extracted to its own repository.

## Structure

Each project lives in its own directory:

```
transformer-questions/
├── cloud-gpu/          # Remote GPU Jupyter setup
├── model-library/      # Base and SFT/Instruct model pairs library
├── project-2/          # Future project...
└── project-3/          # Future project...
```

## Workflow

1. **Start a project**: Create a new directory and start building
2. **Iterate**: Develop, test, and experiment within this repo
3. **Extract when ready**: Use the `scripts/extract-project.sh` utility to move a project to its own repository when it becomes mature enough

## Projects

### [cloud-gpu](./cloud-gpu/)

Complete setup for running Jupyter notebooks on remote H100 GPUs (like Hyperbolic). Supports both VS Code Remote and Standalone Jupyter workflows, with pytest for testing GPU functionality.

### [model-library](./model-library/)

Curated library of base and SFT/Instruct model pairs (Qwen, Llama, DeepSeek, NVIDIA). Includes utilities for filtering by size, family, and getting model information.

## Environment Setup

This repository uses environment variables for API keys and secrets. Never commit these directly to the repository.

### Setup API Keys

1. **Copy the template file**:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. **Edit `.env`** and add your actual API keys:
   ```
   VAST_API_KEY=your_actual_vast_api_key_here
   GITHUB_TOKEN=your_actual_github_token_here
   ```

3. **The `.env` file is gitignored** - it will never be committed to the repository.

### Available API Keys

- **VAST_API_KEY**: For vast.ai API access (used by vastai-sdk)
  - Get your key from: https://vast.ai/console/account
  - The vastai-sdk automatically reads this from environment variables

- **GITHUB_TOKEN**: For GitHub API access (optional)
  - Get from: https://github.com/settings/tokens
  - Used for creating repositories programmatically

### Using Environment Variables

Most tools (like vastai-sdk) will automatically read environment variables. You can also set them manually:

**Windows (PowerShell):**
```powershell
$env:VAST_API_KEY = "your_key_here"
```

**Linux/Mac:**
```bash
export VAST_API_KEY="your_key_here"
```

## Testing

This repository uses pytest for testing. Tests are located in the `tests/` directory.

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_vast_ai.py -v        # Vast.ai API tests
pytest cloud-gpu/tests/ -v              # GPU tests
```

### Test Categories

- **Vast.ai API Tests** (`tests/test_vast_ai.py`): Tests for Vast.ai API connection, account info, and instance search
- **GPU Tests** (`cloud-gpu/tests/`): Tests for GPU detection, CUDA, and PyTorch functionality

Tests automatically skip if required dependencies (API keys, GPU, etc.) are not available, so they're safe to run on any machine.

## Extracting a Project

When a project is ready to stand on its own:

```bash
./scripts/extract-project.sh <project-name>
```

This will help you move the project directory to its own git repository while preserving history.
