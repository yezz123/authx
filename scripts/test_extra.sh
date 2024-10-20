#! /usr/bin/env bash

set -x
set -e

pushd "$(dirname $0)/../authx-extra"

pip install uv

source ../venv/bin/activate

uv sync

pytest --cov=authx_extra --cov-report=xml

popd
