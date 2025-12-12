# Contributing to Wikipedia 1.0 Engine

Thank you for your interest in contributing to the Wikipedia 1.0 Engine! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Documentation](#documentation)
- [License](#license)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Code Style

### Python Code

- We use **Black** for Python code formatting
- We use **YAPF** for additional formatting (configuration in `.style.yapf`)
- Follow PEP 8 style guidelines
- Pre-commit hooks will automatically format your code

### JavaScript/Vue Code

- We use **Prettier** for JavaScript/Vue code formatting
- Configuration is in `.pre-commit-config.yaml`
- Use single quotes for strings
- Use trailing commas

### Running Code Formatters Manually

```bash
# Format Python code
pipenv run black .

# Check all pre-commit hooks
pipenv run pre-commit run --all-files
```

## Testing

### Backend (Python) Tests

The project uses pytest for backend testing:

```bash
# Run all tests
pipenv run pytest

# Run specific test file
pipenv run pytest wp1/api_test.py

# Run with coverage report
pipenv run pytest --cov=wp1
```

**Important:** Backend tests require a test database. Use the provided docker-compose setup:

```bash
docker compose -f docker-compose-test.yml up -d
```

### Frontend (Cypress) Tests

Frontend integration tests require a running development environment:

```bash
cd wp1-frontend
$(yarn bin)/cypress run
```

### Writing Tests

- Write tests for all new features and bug fixes
- Maintain or improve code coverage
- Follow existing test patterns in the codebase
- Place tests in files named `*_test.py` for Python

## Pull Request Process

### Before Submitting

1. **Update documentation** if you've changed APIs or added features
2. **Run the full test suite** and ensure all tests pass
3. **Run pre-commit hooks** to ensure code formatting
4. **Update the README.md** if necessary with details of changes
5. **Add or update tests** for your changes

### Submitting a Pull Request

1. **Push your changes** to your fork
2. **Create a Pull Request** against the `main` branch
3. **Fill out the PR template** with:
   - A clear description of the changes
   - The issue number(s) this PR addresses (if applicable)
   - Any breaking changes
   - Screenshots for UI changes
4. **Wait for review** - maintainers will review your PR and may request changes
5. **Address feedback** and push additional commits if needed
6. **Squash commits** if requested by maintainers

### PR Review Criteria

Your PR will be reviewed for:

- **Code quality** - Clean, readable, maintainable code
- **Tests** - Adequate test coverage for changes
- **Documentation** - Clear documentation for new features
- **Style** - Adherence to project code style
- **Functionality** - Changes work as intended
- **Breaking changes** - Proper handling and documentation

## Reporting Bugs

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Test on the latest version** to ensure the bug still exists
3. **Gather information** about your environment

### Creating a Bug Report

Include the following in your bug report:

- **Clear title** describing the issue
- **Steps to reproduce** the bug
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, Docker version)
- **Error messages** or screenshots if applicable
- **Relevant logs** from the application

Use the bug report template when creating an issue.

## Suggesting Enhancements

We welcome enhancement suggestions! When suggesting an enhancement:

1. **Check existing issues** to see if it's already suggested
2. **Provide a clear use case** for the enhancement
3. **Describe the proposed solution** in detail
4. **Consider alternatives** and explain why your solution is best
5. **Be open to discussion** and feedback

## Documentation

Good documentation is crucial for the project:

### Updating Documentation

- Update relevant documentation when changing code
- Documentation lives in the `docs/` directory
- Built with [MkDocs](https://www.mkdocs.org/)
- Hosted on [Read the Docs](https://wp1.readthedocs.io)

### Building Documentation Locally

```bash
cd docs
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
mkdocs serve
```

View at `http://localhost:8000`

### API Documentation

API documentation is maintained in `openapi.yml` using the OpenAPI specification.

## Getting Help

- **Issues**: Open an issue on GitHub
- **Documentation**: Check [Read the Docs](https://wp1.readthedocs.io)
- **README**: Review the [README.md](README.md) for development setup and workflow details

## Recognition

Contributors are recognized in the project's commit history and may be added to a CONTRIBUTORS file in the future.

## License

By contributing to this project, you agree that your contributions will be licensed under the GPLv2 or later license. See the [LICENSE](LICENSE) file for details.

---

Thank you for contributing to the Wikipedia 1.0 Engine! Your efforts help improve Wikipedia content organization and accessibility.
