#!/usr/bin/env bash

set -e
set -x

echo "ENV=${ENV}"
echo "REDIS_URL-${REDIS_URL}"

export PYTHONPATH=.

# run redis container
docker run -d -p 6379:6379 --name redis redis

# run tests
pytest --cov=authx --cov=tests -xv

# Shutdown and remove redis container
docker stop redis
docker rm redis