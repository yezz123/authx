PYTHON ?= python3
VENV ?= venv
PY ?= $(VENV)/bin/python
PIP ?= $(VENV)/bin/pip
EXTRA_FLAGS ?= ''
BIN ?= $(VENV)/bin


run: venv
	${BIN}/uvicorn --factory app:get_app --host=0.0.0.0 --port=8000

test_client: venv
	${BIN}/python test_client.py