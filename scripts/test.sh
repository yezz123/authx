#!/usr/bin/env bash

set -e
set -x

export PYTHONPATH= .
pytest --cov=authx --cov=tests