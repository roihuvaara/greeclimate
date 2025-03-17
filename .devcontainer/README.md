# Development Container for Gree Versati

This directory contains configuration for a development container that provides a consistent environment for working with the Gree Versati project.

## Requirements

To use this development container, you need:

1. [Visual Studio Code](https://code.visualstudio.com/)
2. [Docker Desktop](https://www.docker.com/products/docker-desktop)
3. [VS Code Remote - Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Getting Started

1. Clone the repository
2. Open the project folder in Visual Studio Code
3. VS Code will detect the devcontainer configuration and prompt you to reopen in a container. Click "Reopen in Container"
   - Alternatively, you can click the green button in the lower-left corner of VS Code and select "Reopen in Container"

## Features

This development container provides:

- Python 3.11 environment
- All required dependencies pre-installed
- Modern code quality tools:
  - [Ruff](https://github.com/charliermarsh/ruff) for linting and formatting
  - [Pyright](https://github.com/microsoft/pyright) for type checking
- Network tools for device discovery and debugging
- VS Code configuration with Python extensions and linting
- Host network mode for local network device discovery

## Code Quality Tools

This project uses:

- **Ruff**: A fast Python linter and formatter, replacing multiple tools like flake8, black, isort, etc.
  - Auto-formatting on save
  - Import sorting
  - Static analysis and error detection
- **Pyright**: Type checking for Python code
  - Static type checking
  - IntelliSense features
  - Auto-import suggestions

Configuration for these tools is in the `pyproject.toml` file at the project root.

## Dependencies

The project manages dependencies through:
- `requirements.txt` - Core project dependencies
- `requirements-test.txt` - Additional dependencies needed for testing

These are automatically installed when the devcontainer is created.

## Troubleshooting

If you encounter issues with the development container:

1. Try rebuilding the container: Click the green button in the lower-left corner and select "Rebuild Container"
2. Verify Docker is running correctly
3. Check Docker logs for any errors during container build

## Customization

You can customize the development environment by modifying:

- `devcontainer.json` - VS Code settings and container configuration
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Service configuration
- `pyproject.toml` - Ruff and Pyright configuration 