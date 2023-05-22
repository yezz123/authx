#!/usr/bin/env bash

set -e
set -x

echo "ENV=${ENV}"
echo "REDIS_URL=${REDIS_URL}"

export PYTHONPATH=.

# Check if Redis container is already running
if [[ "$(docker inspect -f '{{.State.Running}}' redis 2>/dev/null)" == "true" ]]; then
  echo "Redis container is already running. Running tests again..."
  # Run tests
  pytest --cov=authx --cov=tests -xv
else
  # Remove any existing Redis container
  docker rm -f redis || true
  # Start Redis container
  docker run -d -p 6379:6379 --name redis redis
  # Run tests
  pytest --cov=authx --cov=tests -xv
  # Shutdown Redis container
  docker stop redis
  docker rm redis
fi