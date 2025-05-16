# Mini DNS API - Development Guide

This guide provides essential information for developers working on the Mini DNS API project.

## Prerequisites

- Python 3.13+
- pip (Python package manager)
- Git

## Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:rostysIav/mini-dns-api.git
   cd mini-dns-api
   ```

2. **Set up virtual environment**
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Running the development server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API docs will be available at: http://localhost:8000/docs

2. **Running tests**
   ```bash
   # Run all tests
   pytest
   
   # Run tests with coverage
   pytest --cov=app --cov-report=term-missing
   ```

3. **Code formatting and linting**
   ```bash
   # Format code with Black
   black .
   
   # Check code style with Ruff
   ruff check .
   
   # Type checking with mypy
   mypy .
   ```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function/method signatures
- Keep lines under 88 characters (Black's default)
- Use docstrings for all public modules, classes, and functions

## Git Workflow

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with a descriptive message:
   ```bash
   git add .
   git commit -m "Add feature: brief description of changes"
   ```

3. Push your changes to the remote repository:
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. Create a pull request on GitHub for review.

## Testing

- Write tests for all new functionality
- Maintain at least 90% test coverage
- Use descriptive test names that explain what's being tested
- Group related tests in classes when appropriate

## Documentation

- Update the relevant documentation when making changes
- Add docstrings to all new functions and classes
- Update the README.md if there are changes to setup or usage

## Code Review

- All code must be reviewed before merging to main
- Be respectful and constructive in code reviews
- Address all review comments before merging
- Keep PRs focused and reasonably sized
