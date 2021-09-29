help:
	@echo "Targets:"
	@echo "    make test"
	@echo "    make start"
	@echo "    make down"
	@echo "    make pull"
	@echo "    make build"
	@echo "    make lint"
	@echo "    make clean"
	@echo "    make clean-test"
	@echo "    make bumpversion-major"
	@echo "    make bumpversion-minor"
	@echo "    make bumpversion-patch"
test:
	docker-compose run --rm authx pytest --cov=./  --cov-report=xml

start:
	docker-compose up -d

down:
	docker-compose down

pull:
	docker-compose pull

build:
	docker-compose build

lint:
	docker-compose run --rm authx pre-commit run --all-files

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
