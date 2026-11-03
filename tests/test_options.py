"""Answers other than the defaults: licences, Python range, invalid names."""

import tomllib
from pathlib import Path

import pytest

from .conftest import generate

LICENCE_FIRST_LINES = {
    "MIT": "MIT License",
    "BSD-3-Clause": "BSD 3-Clause License",
    "Apache-2.0": "Apache License",
    "GPL-3.0-or-later": "GNU GENERAL PUBLIC LICENSE",
}


@pytest.mark.parametrize("licence", LICENCE_FIRST_LINES)
def test_licence(tmp_path: Path, licence: str) -> None:
    path = generate(tmp_path / "project", license=licence)
    assert (path / "LICENSE").read_text(encoding="utf-8").strip().startswith(LICENCE_FIRST_LINES[licence])
    pyproject = tomllib.loads((path / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["license"] == licence


def test_no_licence(tmp_path: Path) -> None:
    path = generate(tmp_path / "project", license="None")
    assert not (path / "LICENSE").exists()
    assert "license" not in tomllib.loads((path / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def test_minimum_python_narrows_the_test_matrix(tmp_path: Path) -> None:
    path = generate(tmp_path / "project", min_python="3.13")
    pyproject = tomllib.loads((path / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["requires-python"] == ">=3.13"
    assert "Programming Language :: Python :: 3.12" not in pyproject["project"]["classifiers"]
    tests = (path / ".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert 'python-versions: "[\\"3.13\\", \\"3.14\\", \\"3.15\\"]"' in tests


@pytest.mark.parametrize(
    "answers",
    [
        {"project_name": "Not_A_Repo_Name"},
        {"package_name": "not-an-identifier"},
        {"project_description": 'Has "quotes"'},
    ],
)
def test_invalid_answers_are_refused(tmp_path: Path, answers: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="Validation error"):
        generate(tmp_path / "project", **answers)
