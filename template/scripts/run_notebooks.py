"""Execute every teaching notebook headless and save the executed copies in notebooks/executed/.

    uv run scripts/run_notebooks.py              # all notebooks
    uv run scripts/run_notebooks.py 01 03        # the ones whose names start with 01 or 03

Runs from the notebooks/ folder, so files a notebook writes land there. The committed notebooks
carry no outputs; the executed copies keep theirs. Exits 1 if any cell raised an error.
"""

import os
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

NOTEBOOKS = Path(__file__).resolve().parent.parent / "notebooks"
EXECUTED = NOTEBOOKS / "executed"
TEACHING_NOTEBOOKS = "[0-9][0-9]_*.ipynb"
CELL_TIMEOUT_SECONDS = 900


def error_count(notebook: nbformat.NotebookNode) -> int:
    """Count the code cells whose outputs end in an error."""
    return sum(
        any(output.get("output_type") == "error" for output in cell.get("outputs", []))
        for cell in notebook.cells
        if cell.cell_type == "code"
    )


def execute(path: Path) -> int:
    """Execute one notebook, save its executed copy, print one line and return its error count."""
    notebook = nbformat.read(path, as_version=4)
    started = time.monotonic()
    client = NotebookClient(
        notebook,
        timeout=CELL_TIMEOUT_SECONDS,
        kernel_name="python3",
        allow_errors=True,
        resources={"metadata": {"path": str(NOTEBOOKS)}},
    )
    client.execute()
    errors = error_count(notebook)
    nbformat.write(notebook, EXECUTED / path.name.replace(".ipynb", ".executed.ipynb"))
    print(f"{path.name:50s} {time.monotonic() - started:6.1f} s   errors: {errors}", flush=True)
    return errors


def main(prefixes: list[str]) -> int:
    """Execute the selected notebooks (all of them without prefixes) and return the exit code."""
    # Headless runs never sign in to Rakiura; the kernels inherit this (see the package's portal module).
    os.environ.setdefault("RAKIURA_LIVE", "0")
    EXECUTED.mkdir(parents=True, exist_ok=True)
    paths = sorted(NOTEBOOKS.glob(TEACHING_NOTEBOOKS))
    if prefixes:
        paths = [path for path in paths if path.name.startswith(tuple(prefixes))]
    if not paths:
        print("No notebooks to execute.", file=sys.stderr)
        return 1
    errors = [execute(path) for path in paths]
    return 1 if any(errors) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
