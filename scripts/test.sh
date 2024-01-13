#!/usr/bin/env bash

set -e
set -x

echo "ENV=${ENV}"

export PYTHONPATH=.
pytest --cov-report=term-missing --cov-fail-under=80
