#! /usr/bin/env bash

set -x
set -e

pushd "$(dirname $0)/../authx-extra"

pip install uv

uv sync

source .venv/bin/activate

pytest --cov=authx_extra --cov-report=xml

popd
