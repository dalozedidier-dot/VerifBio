# Rename EchoBio -> VerifBio

This pack renames the tool at 3 levels:

1) Package directory:
- `src/echobio` -> `src/verifbio`

2) CLI:
- `echobio ...` -> `verifbio ...` (console script entry in `pyproject.toml`)

3) Documentation and workflows:
- README, examples, CI workflows updated to the new name

## How to apply

From repo root:

```bash
bash scripts/rename_to_verifbio.sh
git status
git diff
git add -A
git commit -m "chore: rename EchoBio to VerifBio"
git push
```

## Notes

- This is a textual rename plus directory move.
- If you already renamed the GitHub repo, you still need to rename the Python package and CLI to keep installs/imports consistent.
- After the rename, test:

```bash
python -m pip install -e ".[dev]"
python -m verifbio --help || verifbio --help
pytest -q
python -m black --check .
```
