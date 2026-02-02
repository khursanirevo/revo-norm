# Development Guide for Revo Norm

## Modern Python Tooling

This project uses modern Python tooling for faster development and better code quality:

- **uv** - Fast Python package manager (10-100x faster than pip)
- **ruff** - Fast Python linter and formatter (written in Rust)
- **pytest** - Testing framework with coverage

## Installation

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/revo-norm.git
cd revo-norm

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Install development dependencies
uv sync --all-extras
```

## Development Workflow

### 1. Make Changes

Edit code in `revo_norm/` or tests in `tests/`

### 2. Format Code

```bash
uv run ruff format revo_norm/ tests/
```

### 3. Check Linting

```bash
# Check all files
uv run ruff check revo_norm/ tests/

# Auto-fix linting issues
uv run ruff check --fix revo_norm/ tests/

# Show what would change (dry-run)
uv run ruff format --check revo_norm/ tests/
```

### 4. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_normalization_comprehensive.py -v

# Run specific test
uv run pytest tests/test_normalization_comprehensive.py::TestTemperature::test_english_celsius -v
```

### 5. Type Checking (Optional)

The project uses runtime type hints. For static type checking, ty is recommended:

```bash
# Install ty separately (not in dev dependencies due to version constraints)
uv add --dev ty

# Run type checker
uv run ty revo_norm/
```

## Common Commands

| Task | Command |
|------|---------|
| **Install dependencies** | `uv sync` |
| **Install dev deps** | `uv sync --all-extras` |
| **Format code** | `uv run ruff format revo_norm/ tests/` |
| **Check linting** | `uv run ruff check revo_norm/ tests/` |
| **Auto-fix linting** | `uv run ruff check --fix revo_norm/` |
| **Run tests** | `uv run pytest` |
| **Run tests with coverage** | `uv run pytest --cov` |
| **Run specific test** | `uv run pytest tests/test_file.py::TestName::test_name -v` |

## Ruff Configuration

The project uses `ruff` for both linting and formatting. Configuration is in `pyproject.toml`:

- **Line length**: 100 characters
- **Indent width**: 4 spaces
- **Quote style**: Double quotes
- **Python version**: 3.9+

### Ruff Rules Enabled

- `E` - pycodestyle errors
- `W` - pycodestyle warnings
- `F` - pyflakes
- `I` - isort (import sorting)
- `N` - pep8-naming
- `UP` - pyupgrade (modernize Python syntax)
- `B` - flake8-bugbear (find common bugs)
- `C4` - flake8-comprehensions (improve comprehensions)
- `SIM` - flake8-simplify (simplify code)

### Ruff Features

- **Ultra-fast**: Written in Rust, 10-100x faster than Python tools
- **All-in-one**: Replaces flake8, black, isort, pyupgrade
- **Auto-fix**: Can automatically fix many linting issues
- **IDE integration**: Works with VS Code, PyCharm, etc.

## Migration from Old Tools

| Old Tool | New Tool | Migration Guide |
|----------|----------|------------------|
| **pip** | **uv** | `pip install -e .[dev]` → `uv sync --all-extras` |
| **black** | **ruff format** | `black revo_norm/` → `uv run ruff format revo_norm/` |
| **flake8** | **ruff check** | `flake8 revo_norm/` → `uv run ruff check revo_norm/` |
| **isort** | **ruff check --select I** | Auto-handled by ruff |
| **mypy** | **ty** (optional) | Install separately: `uv add --dev ty` |

## Pre-commit Hooks (Optional)

To set up pre-commit hooks for automatic formatting and linting:

```bash
# Install pre-commit
uv add --dev pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]
        pass_filenames: false
EOF

# Install hooks
pre-commit install
```

## IDE Configuration

### VS Code

Install these extensions:
- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

Add to `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

### PyCharm

1. Go to Settings → Tools → External Tools
2. Add ruff format and ruff check as external tools
3. Enable "Enable ruff support" in Languages & Frameworks → Python

## Performance

uv is significantly faster than traditional tools:

| Operation | pip | uv | Speedup |
|-----------|-----|-----|---------|
| Install package | 1.5s | 0.1s | 15x faster |
| Install from source | 3.2s | 0.3s | 10x faster |
| Create virtual environment | 1.1s | 0.04s | 27x faster |

## Troubleshooting

### "uv: command not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "ruff: command not found"

Install dependencies:
```bash
uv sync --all-extras
```

### Tests failing after formatting

Make sure to run `uv run ruff format` before committing. If tests fail, check that no logic was accidentally changed.

### Import errors

Run `uv sync` to ensure all dependencies are installed.

## CI/CD

The project is configured to use uv and ruff in CI/CD pipelines. See `.github/workflows/` for example configurations.

## Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
