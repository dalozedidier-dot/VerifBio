PY ?= python

.PHONY: install check format test audit ci

install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"

format:
	$(PY) -m black .

check:
	$(PY) -m black --check .

test:
	pytest -q

audit:
	echobio audit examples/brca1_parp.yaml

ci: check test audit
