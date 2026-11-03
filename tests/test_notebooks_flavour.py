"""The notebooks flavour: a helper package, notebooks that run headless, a committed uv.lock."""

import json
from pathlib import Path

from .conftest import run

EXPECTED_FILES = (
    "demotrain/__init__.py",
    "demotrain/_version.py",
    "demotrain/checks.py",
    "demotrain/portal.py",
    "notebooks/01_getting_started.ipynb",
    "notebooks/executed/README.md",
    "notebooks/rakiura_steps.json",
    "scripts/run_notebooks.py",
    "tests/test_notebooks.py",
    ".python-version",
    "uv.lock",
)
LIBRARY_ONLY_FILES = (".github/workflows/release.yml", "src")


def test_expected_files(notebooks: Path) -> None:
    for name in EXPECTED_FILES:
        assert (notebooks / name).exists(), f"{name} is missing"
    for name in LIBRARY_ONLY_FILES:
        assert not (notebooks / name).exists(), f"{name} should not be generated"


def test_uv_lock_is_committed(notebooks: Path) -> None:
    ignored = (notebooks / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "uv.lock" not in ignored
    run(["uv", "lock", "--check"], notebooks)


def test_executed_notebooks_are_kept_out_of_the_hooks(notebooks: Path) -> None:
    hooks = (notebooks / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "id: nbstripout" in hooks
    assert "exclude: ^notebooks/executed/" in hooks


def test_ci_executes_the_notebooks_on_colab_python(notebooks: Path) -> None:
    workflow = (notebooks / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert "notebooks-execute.yml@" in workflow
    assert 'python-version: "3.13"' in workflow


def test_the_notebooks_execute(project: Path) -> None:
    if not (project / "notebooks").exists():
        return
    output = run(["uv", "run", "scripts/run_notebooks.py"], project)
    assert "errors: 0" in output
    executed = json.loads(
        (project / "notebooks/executed/01_getting_started.executed.ipynb").read_text(encoding="utf-8")
    )
    outputs = [output for cell in executed["cells"] for output in cell.get("outputs", [])]
    assert any("not answered yet" in "".join(output.get("text", "")) for output in outputs)
