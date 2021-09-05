help:
	@echo "Targets:"
	@echo "    make test"
	@echo "    make start"
	@echo "    make down"
	@echo "    make pull"
	@echo "    make build"
	@echo "    make lint"

test:
	docker-compose run --rm authx pytest --cov=AuthX --cov-report=html

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
