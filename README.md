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
