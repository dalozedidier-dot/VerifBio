# EchoBio

EchoBio audits the **quality of specification** of a biological claim/hypothesis (not its truth).

## Install

```bash
python -m pip install -e ".[dev]"
```

## Run an audit

```bash
echobio audit examples/brca1_parp.yaml
```

## CI

This repo includes a GitHub Actions CI workflow (`.github/workflows/ci.yml`) with:
- `workflow_dispatch` (manual **Run workflow** button)
- `black --check .`
- `pytest -q`


## Quick install & test (local)

### Linux / macOS

```bash
bash scripts/bootstrap_venv.sh
source .venv/bin/activate
make ci
```

### Any OS (manual)

```bash
python -m venv .venv
# activate your venv
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m black --check .
pytest -q
echobio audit examples/brca1_parp.yaml --out _ci_out/echobio_report.json
```

The output report will be written to `_ci_out/echobio_report.json`.
