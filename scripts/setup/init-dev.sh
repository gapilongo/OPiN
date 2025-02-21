

#!/bin/bash
set -e

echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Create .env file
cp .env.example .env

# Initialize database
python scripts/db/init_db.py

# Start development services
docker-compose -f docker-compose.dev.yml up -d

echo "Development environment setup completed!"

# Create alias for convenience
echo 'alias opin-dev="source venv/bin/activate && export ENVIRONMENT=development"' >> ~/.bashrc

echo "Use 'opin-dev' command to activate the development environment"