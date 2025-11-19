# transformer-questions

A collection of pet projects and experiments. This repository serves as a playground for trying out ideas, and when a project matures, it can be extracted to its own repository.

## Structure

Each project lives in its own directory:

```
transformer-questions/
├── cloud-gpu/          # Remote GPU Jupyter setup
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

## Extracting a Project

When a project is ready to stand on its own:

```bash
./scripts/extract-project.sh <project-name>
```

This will help you move the project directory to its own git repository while preserving history.
