help:
	@echo "Targets:"
	@echo "    make up"
	@echo "    make down"
	@echo "    make build"
	@echo "    make clean"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
