help:
	@echo "Targets:"
	@echo "    make start"
	@echo "    make down"
	@echo "    make pull"
	@echo "    make clean"

start:
	docker-compose up -d

down:
	docker-compose down

pull:
	docker-compose pull

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
