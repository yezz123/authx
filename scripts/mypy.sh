#!/usr/bin/env bash

set -e
set -x

mypy --show-error-codes authx --disable-recursive-aliases