# File: scripts/ci/test.sh

#!/bin/bash
set -e

echo "Running tests..."

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run linting
echo "Running linters..."
black .
isort .
flake8 .

# Run type checking
echo "Running type checking..."
mypy .

# Run unit tests
echo "Running unit tests..."
pytest tests/unit -v --cov=app --cov-report=xml

# Run integration tests
echo "Running integration tests..."
pytest tests/integration -v

# Run security checks
echo "Running security checks..."
bandit -r app
safety check

echo "All tests completed successfully!"

