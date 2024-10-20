#! /usr/bin/env bash

set -x
set -e

pushd "$(dirname $0)/../authx-extra"

pip install uv

uv sync

pytest --cov=authx_extra --cov-report=xml

popd
