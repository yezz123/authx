#!/usr/bin/env bash

set -e
set -x

pre-commit run --all-files --verbose --show-diff-on-failure
