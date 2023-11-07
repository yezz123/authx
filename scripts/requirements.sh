#!/usr/bin/env bash

refresh-lockfiles() {
  echo "Updating requirements/*.txt files using pip-compile"
  find requirements/ -name '*.txt' ! -name 'all.txt' -type f -delete
  pip-compile -q --resolver backtracking -o requirements/linting.txt requirements/linting.in
  pip-compile -q --resolver backtracking -o requirements/testing.txt requirements/testing.in
  pip-compile -q --resolver backtracking -o requirements/docs.txt requirements/docs.in
  pip-compile -q --resolver backtracking -o requirements/optional.txt requirements/optional.in
  pip-compile -q --resolver backtracking --extra all -o requirements/pyproject.txt pyproject.toml
  pip install --dry-run -r requirements/all.txt
}

refresh-lockfiles
