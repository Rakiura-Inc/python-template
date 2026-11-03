"""Generate projects from the template, once per flavour and test session."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from copier import run_copy

TEMPLATE = Path(__file__).resolve().parent.parent
FLAVOURS = ("library", "notebooks")
ANSWERS = {
    "library": {"project_name": "demo-lib", "project_description": "A demo library."},
    "notebooks": {
        "project_name": "demo-notebooks",
        "package_name": "demotrain",
        "project_description": "Demo teaching notebooks.",
    },
}


def generate(destination: Path, src_path: Path = TEMPLATE, **answers: str) -> Path:
    """Generate a project with the template's defaults for every answer not given."""
    run_copy(src_path=str(src_path), dst_path=str(destination), data=answers, defaults=True, unsafe=True, quiet=True)
    return destination


def run(command: list[str], cwd: Path) -> str:
    """Run a command in a generated project with this test's Python; fail the test on a non-zero exit."""
    env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
    env["UV_PYTHON"] = f"{sys.version_info.major}.{sys.version_info.minor}"
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, f"{' '.join(command)} failed:\n{result.stdout}\n{result.stderr}"
    return result.stdout


@pytest.fixture(scope="session", params=FLAVOURS)
def project(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A freshly generated project of each flavour, its dependencies installed."""
    flavour = request.param
    path = generate(tmp_path_factory.mktemp(flavour) / "project", flavour=flavour, **ANSWERS[flavour])
    run(["uv", "sync"], path)
    return path


@pytest.fixture(scope="session")
def library(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A generated library, without its dependencies installed."""
    return generate(tmp_path_factory.mktemp("library") / "project", flavour="library", **ANSWERS["library"])


@pytest.fixture(scope="session")
def notebooks(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A generated notebooks repository, without its dependencies installed."""
    return generate(tmp_path_factory.mktemp("notebooks") / "project", flavour="notebooks", **ANSWERS["notebooks"])
