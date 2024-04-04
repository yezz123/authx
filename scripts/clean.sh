#!/usr/bin/env bash

rm -f `find . -type f -name '*.py[co]' `
rm -f `find . -type f -name '*~' `
rm -f `find . -type f -name '.*~' `
rm -f `find . -type f -name .coverage`
rm -f `find . -type f -name coverage.xml`
rm -f `find . -type f -name ".coverage.*"`
rm -rf `find . -name __pycache__`
rm -rf `find . -type d -name '*.egg-info' `
rm -rf `find . -type d -name 'pip-wheel-metadata' `
rm -rf `find . -type d -name .pytest_cache`
rm -rf `find . -type d -name .cache`
rm -rf `find . -type d -name .mypy_cache`
rm -rf `find . -type d -name htmlcov`
rm -rf `find . -type d -name "*.egg-info"`
rm -rf `find . -type d -name build`
rm -rf `find . -type d -name dist`
rm -rf `find . -type d -name authx_extra`
rm -rf `find . -type d -name .pytest_cache`
rm -rf `find . -type d -name .mypy_cache`
