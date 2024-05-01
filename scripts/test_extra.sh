#! /usr/bin/env bash

set -x
set -e

pushd "$(dirname $0)/../authx-extra"

uv pip install -r requirements/all.txt

uv pip install -e ../

pytest --cov=authx_extra --cov-report=xml

popd
