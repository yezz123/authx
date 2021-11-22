help:
	@echo "Targets:"
	@echo "    make test"
	@echo "    make lint"
	@echo "    make mkdocs"
	@echo "    make clean"
	@echo "    make clean-test"
	@echo "    make bumpversion-major"
	@echo "    make bumpversion-minor"
	@echo "    make bumpversion-patch"

test:
	pytest --cov=authx/ --cov-report=html

lint:
	pre-commit run --all-files

mkdocs:
	mkdocs serve --livereload

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

bumpversion-major:
	bumpversion major --allow-dirty

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch
