#! /usr/bin/env bash

set -x
set -e

pushd "$(dirname $0)/../authx-extra"

pip install -r requirements/pyproject.txt && pip install -r requirements/testing.txt

pip install -e ../

pytest --cov=authx_extra --cov-report=xml

popd
