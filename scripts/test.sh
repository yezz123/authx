#!/usr/bin/env bash

set -e
set -x

export PYTHONPATH=./authx
pytest --cov=authx --cov=tests