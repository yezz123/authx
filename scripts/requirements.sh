#!/usr/bin/env bash

refresh-lockfiles() {
  echo "Updating requirements/*.txt files using uv"
  find requirements/ -name '*.txt' ! -name 'all.txt' -type f -delete
  uv pip compile requirements/linting.in -o requirements/linting.txt
  uv pip compile requirements/testing.in -o requirements/testing.txt
  uv pip compile requirements/docs.in -o requirements/docs.txt
  uv pip compile pyproject.toml -o requirements/pyproject.txt
  uv pip install -r requirements/all.txt
}

refresh-lockfiles
