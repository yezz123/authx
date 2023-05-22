#!/usr/bin/env bash

set -e
set -x

echo "ENV=${ENV}"
echo "REDIS_URL-${REDIS_URL}"

export PYTHONPATH=.
pytest --cov=authx -xv