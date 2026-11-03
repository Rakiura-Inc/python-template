"""The library flavour: src layout, hatchling, releases on tags, no committed uv.lock."""

import tomllib
from pathlib import Path

EXPECTED_FILES = (
    ".github/workflows/release.yml",
    "CHANGELOG.md",
    "src/demo_lib/__init__.py",
    "src/demo_lib/_version.py",
    "src/demo_lib/py.typed",
    "src/tests/test_demo_lib.py",
)
NOTEBOOKS_ONLY_FILES = ("notebooks", "scripts", "tests", "demo_lib", ".python-version", "uv.lock")


def test_expected_files(library: Path) -> None:
    for name in EXPECTED_FILES:
        assert (library / name).exists(), f"{name} is missing"
    for name in NOTEBOOKS_ONLY_FILES:
        assert not (library / name).exists(), f"{name} should not be generated"


def test_uv_lock_is_gitignored(library: Path) -> None:
    assert "uv.lock" in (library / ".gitignore").read_text(encoding="utf-8").splitlines()


def test_pyproject(library: Path) -> None:
    pyproject = tomllib.loads((library / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["build-system"]["build-backend"] == "hatchling.build"
    assert pyproject["project"]["name"] == "demo-lib"
    assert pyproject["project"]["requires-python"] == ">=3.11"
    assert pyproject["project"]["license"] == "MIT"
    assert "Programming Language :: Python :: 3.15" in pyproject["project"]["classifiers"]
    assert "Programming Language :: Python :: 3.10" not in pyproject["project"]["classifiers"]
    assert pyproject["tool"]["hatch"]["version"]["path"] == "src/demo_lib/_version.py"


def test_release_uses_the_shared_workflow_with_least_permissions(library: Path) -> None:
    release = (library / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "Rakiura-Inc/.github/.github/workflows/release.yml@" in release
    assert "contents: write" in release
    assert "attestations: write" in release


def test_readme_verifies_the_attestation_against_the_shared_workflow(library: Path) -> None:
    readme = (library / "README.md").read_text(encoding="utf-8")
    assert "--signer-workflow Rakiura-Inc/.github/.github/workflows/release.yml" in readme


def test_ci_tests_every_supported_python(library: Path) -> None:
    tests = (library / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert 'python-versions: "[\\"3.11\\", \\"3.12\\", \\"3.13\\", \\"3.14\\", \\"3.15\\"]"' in tests
    assert "wheel-tests: src/tests" in tests
