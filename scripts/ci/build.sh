# File: scripts/ci/build.sh

#!/bin/bash
set -e

# Configuration
PROJECT_NAME="opin"
ENVIRONMENT=${ENVIRONMENT:-"production"}
DOCKER_TAG=${DOCKER_TAG:-"latest"}

# Load environment variables
source .env.${ENVIRONMENT}

echo "Building ${PROJECT_NAME} for ${ENVIRONMENT}..."

# Build backend
docker build \
  --build-arg ENVIRONMENT=${ENVIRONMENT} \
  -t ${PROJECT_NAME}-backend:${DOCKER_TAG} \
  -f backend/Dockerfile \
  backend/

# Build frontend
docker build \
  --build-arg ENVIRONMENT=${ENVIRONMENT} \
  -t ${PROJECT_NAME}-frontend:${DOCKER_TAG} \
  -f frontend/Dockerfile \
  frontend/

echo "Build completed successfully!"

