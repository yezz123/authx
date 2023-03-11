#!/usr/bin/env bash

set -e
set -x

echo "ENV=${ENV}"
echo "REDIS_URL-${REDIS_URL}"
echo "CODSPEED_TOKEN-${CODSPEED_TOKEN}"

export PYTHONPATH=.
pytest --cov=tests --codspeed