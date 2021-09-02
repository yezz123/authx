MONGODB_CONTAINER_NAME := AuthX-MongoDB

isort-src:
	isort ./AuthX ./tests

format: isort-src
	black ./AuthX ./tests

test:
	docker stop $(MONGODB_CONTAINER_NAME) || true
	docker run -d --rm --name $(MONGODB_CONTAINER_NAME) -p 27017:27017 mongo:4.2
	pytest --cov=AuthX/ --cov-report=term-missing --cov-fail-under=100
	docker stop $(MONGODB_CONTAINER_NAME)
