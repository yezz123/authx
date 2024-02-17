#!/usr/bin/env bash

set -e
set -x

export PATH=".venv/bin:$PATH"

# run tests
pytest --cov-report=term-missing --cov-fail-under=80
