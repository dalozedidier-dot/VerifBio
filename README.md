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


## New in v0.2

- Audit modes: `--mode strict|lite`
- Weighted score in report (`weighted_score_0_100`)
- Draft YAML from raw text (heuristic):
  ```bash
  echobio draft --text abstract.txt --out claim.yaml
  ```
- Suggest independent predictions (heuristic):
  ```bash
  echobio suggest claim.yaml --out suggestions.json
  ```
- DAG export (Mermaid or Graphviz DOT):
  ```bash
  echobio dag claim.yaml --format mermaid --out dag.mmd
  echobio dag claim.yaml --format dot --out dag.dot
  ```
- Export report:
  ```bash
  echobio audit claim.yaml --out report.json
  echobio export report.json --format markdown --out report.md
  echobio export report.json --format latex --out report.tex
  ```

## Examples

```bash
echobio audit examples/brca1_parp.yaml --out _ci_out/brca1_report.json
echobio audit examples/mir21_crc.yaml --out _ci_out/mir21_report.json
```
