# Finalize rename to VerifBio

Your CI is currently green, but the install still reports `verifbio==...` and the import path in CI selects `verifbio`.
That means the repository name is VerifBio, but the Python distribution and package are still `verifbio`.

This pack provides a single script to finalize the rename in a reproducible way.

Apply

```bash
unzip -o VerifBio_finalize_rename_pack_v1.zip
python scripts/finalize_rename_to_verifbio.py --root .
git diff
python -c "import verifbio; print('import-ok', verifbio.__file__)"
pytest -q
python -m black --check src scripts tests
git add -A
git commit -m "chore: finalize rename to verifbio (package + pyproject + refs)"
git push
```

After the rename is complete, you can remove the transitional dual import logic in CI and in tests, and require only `verifbio`.
