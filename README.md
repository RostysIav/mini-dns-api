# Mini DNS API

A simple DNS record management API built with FastAPI and SQLModel.

## Features

- RESTful API for managing DNS records
- SQLite database with SQLModel ORM
- Async support with FastAPI
- Input validation with Pydantic
- Type hints and static type checking with mypy
- Code formatting with Black and Ruff
- Pre-commit hooks for code quality

## Development Setup

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone git@github.com:rostysIav/mini-dns-api.git
   cd mini-dns-api
   ```

2. **Set up virtual environment**:
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # On macOS/Linux
   # python3 -m venv .venv
   # source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   # Install project in development mode with all dependencies
   pip install -e ".[dev]"
   ```

   Alternatively, install from requirements files:
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Running the Application

1. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   - API documentation will be available at: http://localhost:8000/docs
   - Alternative documentation (ReDoc): http://localhost:8000/redoc

2. **Run tests**:
   ```bash
   # Run all tests
   pytest
   
   # Run tests with coverage report
   pytest --cov=app --cov-report=term-missing
   
   # Run a specific test file
   pytest tests/test_module.py -v
   ```

3. **Code Quality Checks**:
   ```bash
   # Format code with Black
   black .
   
   # Lint code with Ruff
   ruff check .
   
   # Type checking with mypy
   mypy .
   ```

### Managing Dependencies

- To add a new dependency:
  1. Add it to `requirements.in`
  2. Run `pip-compile requirements.in` to update `requirements.txt`
  3. Install with `pip install -r requirements.txt`

- To update all dependencies:
  ```bash
  pip-compile --upgrade
  pip install -r requirements.txt
  ```

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database
SQLALCHEMY_DATABASE_URI=sqlite:///./sql_app.db

# Application
PROJECT_NAME="Mini DNS API"
API_V1_STR=/api/v1
```

## Project Structure

```
mini-dns-api/
├── app/
│   ├── api/           # FastAPI routers
│   ├── models/        # SQLModel entities
│   ├── schemas/       # Pydantic models
│   ├── services/      # Business logic
│   ├── crud/          # Database operations
│   └── core/          # Application configuration
├── tests/             # Test files
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

## Running Tests

```bash
pytest
```

## Code Quality

- Format code with Black:
  ```bash
  black .
  ```

- Lint code with Ruff:
  ```bash
  ruff check .
  ```

- Type checking with mypy:
  ```bash
  mypy .
  ```

## License

MIT
