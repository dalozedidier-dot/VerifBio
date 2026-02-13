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
	mkdir -p _ci_out
	echobio audit examples/brca1_parp.yaml --out _ci_out/echobio_report.json
	echobio export _ci_out/echobio_report.json --format markdown --out _ci_out/echobio_report.md

ci: check test audit
