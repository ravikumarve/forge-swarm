# Contributing to Forge Swarm

Thank you for your interest in contributing to Forge Swarm! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.10+
- Ollama installed and running
- Git

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/forge-swarm.git
   cd forge-swarm
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

6. Run tests:
   ```bash
   python test_installation.py
   ```

7. Start the development server:
   ```bash
   streamlit run Home.py
   ```

## Submitting Changes

### Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes following our [Coding Standards](#coding-standards)

3. Test your changes thoroughly

4. Commit your changes with a clear message:
   ```bash
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue with agent pipeline"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request to the main repository

### Pull Request Guidelines

- Provide a clear description of what you're changing and why
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Commit Messages

Follow conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add memory export functionality

- Added export_memory() method to MemoryManager
- Added export button in sidebar
- Export format: JSON with full metadata
```

## Testing

### Running Tests

```bash
# Run all tests
python test_installation.py

# Run specific test
pytest tests/test_memory.py
```

### Writing Tests

- Write tests for all new features
- Aim for high test coverage
- Test both happy path and edge cases
- Use descriptive test names

## Documentation

### Updating Documentation

- Keep README.md up to date with new features
- Update inline code comments
- Add docstrings to new functions
- Update CHANGELOG.md for significant changes

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep it beginner-friendly

## Getting Help

If you need help:

- Check existing [Issues](https://github.com/ravikumarve/forge-swarm/issues)
- Join our [Discord community](https://discord.gg/forgeswarm)
- Email support@forgeswarm.com

## License

By contributing to Forge Swarm, you agree that your contributions will be licensed under the MIT License.
