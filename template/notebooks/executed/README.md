# Executed notebooks

Each teaching notebook in `notebooks/`, run end to end with blank answers, as a member first sees
it. Regenerate them after changing a notebook:

```sh
uv run scripts/run_notebooks.py
```

CI runs the same script on every change and uploads its copies as the `executed-notebooks`
artifact.
