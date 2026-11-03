"""Each generated project passes its own checks, as its CI would run them."""

from pathlib import Path

from .conftest import run


def test_tests_pass(project: Path) -> None:
    run(["uv", "run", "pytest"], project)


def test_lint_and_format(project: Path) -> None:
    run(["uv", "run", "ruff", "check", "."], project)
    run(["uv", "run", "ruff", "format", "--check", "."], project)


def test_type_check_when_enabled(project: Path) -> None:
    if "use_ty: true" in (project / ".copier-answers.yml").read_text(encoding="utf-8"):
        run(["uv", "run", "ty", "check"], project)


def test_wheel_builds_and_imports_on_its_own(project: Path, tmp_path: Path) -> None:
    run(["uv", "build", "--out-dir", str(tmp_path)], project)
    wheel = next(tmp_path.glob("*.whl"))
    package = wheel.name.split("-")[0]
    import_it = f"import {package}; print({package}.__version__)"
    output = run(["uv", "run", "--isolated", "--no-project", "--with", str(wheel), "python", "-c", import_it], tmp_path)
    assert output.strip() == "0.1.0"


def test_git_hooks_pass(project: Path) -> None:
    run(["git", "add", "--all"], project)
    run(["prek", "run", "--all-files", "--show-diff-on-failure"], project)
