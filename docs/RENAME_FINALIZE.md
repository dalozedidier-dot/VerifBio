# VerifBio rename finalize pack

This pack aligns the project name "VerifBio" with the Python package and CI.

It includes:
- CI workflow importing `verifbio`
- A smoke test that validates the report `tool` id is `verifbio`
- Rename scripts to move `src/echobio` -> `src/verifbio` and rewrite text references

Apply:

```bash
unzip -o VerifBio_rename_finalize_pack_v2.zip
bash scripts/rename_to_verifbio.sh
git add -A
git commit -m "chore: finalize rename to VerifBio (package + CI + tests)"
git push
```

Then verify:

```bash
python -m pip install -e ".[dev]"
python -c "import verifbio; print('import-ok')"
pytest -q
python -m black --check src scripts tests
```
