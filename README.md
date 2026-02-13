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

## What it does

It produces a JSON report with `pass/partial/fail` across 5 levels:

- **B1** Variables & domain explicit
- **B2** Scale & biological context declared
- **B3** Causal mechanism / DAG declared
- **B4** Closure / boundary conditions (controls, blinding, power, anti-circularity)
- **B5** Independent predictions

This repo includes a GitHub Actions CI workflow (`.github/workflows/ci.yml`) with:
- `workflow_dispatch` (manual "Run workflow" button)
- `black --check .`
- `pytest`
