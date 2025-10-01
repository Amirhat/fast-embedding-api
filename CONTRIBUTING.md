# Contributing to Fast Embedding API

Thank you for your interest in contributing to Fast Embedding API! We welcome contributions from the community.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/Amirhat/fast-embedding-api.git
   cd fast-embedding
   ```

3. **Create a branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov ruff black isort

# Run the server
python -m src.main
```

### Docker Development

```bash
# Build and run development container
docker-compose --profile dev up fast-embedding-dev

# The container has hot-reload enabled
```

## 📝 Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **Ruff** for linting
- **isort** for import sorting

### Format Your Code

```bash
# Format with black
black src/ tests/

# Sort imports
isort src/ tests/

# Lint with ruff
ruff check src/ tests/ --fix
```

### Pre-commit Checks

Before committing, ensure your code passes all checks:

```bash
# Run all checks
black --check src/ tests/
isort --check-only src/ tests/
ruff check src/ tests/
pytest tests/ -v
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/test_api.py -v

# With coverage
pytest tests/test_api.py --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
```

### Run Benchmarks

```bash
# Start the server
docker-compose up -d

# Run benchmarks
python benchmarks/benchmark.py
```

### Add New Tests

When adding new features, please include:

- Unit tests for new functions/classes
- Integration tests for API endpoints
- Update `tests/test_api.py` accordingly

## 📚 Documentation

- Update relevant documentation in `docs/`
- Add docstrings to new functions/classes
- Update README.md if adding new features
- Add examples to `tests/example_client.py` if relevant

## 🔄 Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update CHANGELOG.md

2. **Run All Checks**

   ```bash
   black src/ tests/
   isort src/ tests/
   ruff check src/ tests/
   pytest tests/ -v
   ```

3. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "feat: Add amazing feature"
   ```

   Use conventional commits:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for tests
   - `refactor:` for refactoring
   - `perf:` for performance improvements

4. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub and create a PR
   - Fill in the PR template
   - Link any relevant issues

## 🐛 Reporting Bugs

When reporting bugs, please include:

- **Description** of the bug
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Python version, Docker version)
- **Logs** if available

## 💡 Suggesting Features

We love feature suggestions! Please:

- Check existing issues first
- Describe the use case
- Explain why it would be useful
- Consider providing a PR if possible

## 📋 Coding Guidelines

### Python

- Follow PEP 8 style guide
- Use type hints where possible
- Write descriptive docstrings
- Keep functions focused and small
- Use async/await for I/O operations

### Example

```python
async def get_embedding(
    model_name: str,
    text: str,
    timeout: Optional[float] = None
) -> List[float]:
    """
    Generate embedding for text using specified model.
    
    Args:
        model_name: Name of the embedding model
        text: Text to embed
        timeout: Optional timeout in seconds
        
    Returns:
        List of embedding values
        
    Raises:
        TimeoutError: If embedding generation times out
        ValueError: If text is empty or too long
    """
    # Implementation
```

### Project Structure

```tree
fast-embedding/
├── src/                 # Source code
├── tests/              # Tests
├── benchmarks/         # Benchmarks
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── .github/            # GitHub workflows
```

## 🔒 Security

If you discover a security vulnerability:

- **Do not** open a public issue
- Email `a.h.amani.t@gmail.com`
- Include detailed steps to reproduce

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Your contributions make this project better for everyone!

## 📞 Questions?

- Open an issue for questions
- Join our discussions on GitHub
- Check existing documentation

---

Happy coding! 🚀
