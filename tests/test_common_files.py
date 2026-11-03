"""Files every generated repository gets, whatever its flavour."""

import re
from pathlib import Path

import pytest

COMMON_FILES = (
    ".copier-answers.yml",
    ".editorconfig",
    ".github/CODEOWNERS",
    ".github/workflows/git-hooks.yml",
    ".github/workflows/pip-audit.yml",
    ".github/workflows/scorecard.yml",
    ".github/workflows/tests.yml",
    ".gitignore",
    ".pre-commit-config.yaml",
    "CHANGELOG.md",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "docs/teaching-code-style.md",
    "pyproject-fmt.toml",
    "pyproject.toml",
    "pytest.toml",
    "renovate.json5",
    "ruff.toml",
    "yamlfmt.yaml",
)
FULL_SHA_PIN = re.compile(r"^\s+uses: [\w.-]+/[\w./-]+@[0-9a-f]{40}  # v\d+\.\d+\.\d+$")


@pytest.fixture(params=["library", "notebooks"])
def generated(request: pytest.FixtureRequest) -> Path:
    return request.getfixturevalue(request.param)


def test_common_files(generated: Path) -> None:
    for name in COMMON_FILES:
        assert (generated / name).is_file(), f"{name} is missing"


def test_answers_file_records_the_template_version(generated: Path) -> None:
    answers = (generated / ".copier-answers.yml").read_text(encoding="utf-8")
    assert "_src_path:" in answers
    assert "_commit:" in answers


def test_workflows_call_the_shared_workflows_pinned_to_a_sha(generated: Path) -> None:
    for workflow in (generated / ".github/workflows").glob("*.yml"):
        lines = [line for line in workflow.read_text(encoding="utf-8").splitlines() if "uses:" in line]
        assert lines, f"{workflow.name} calls no shared workflow"
        for line in lines:
            assert "Rakiura-Inc/.github/.github/workflows/" in line
            assert FULL_SHA_PIN.match(line), f"{workflow.name}: not pinned to a full SHA: {line}"


def test_security_policy_points_to_private_reporting(generated: Path) -> None:
    security = (generated / "SECURITY.md").read_text(encoding="utf-8")
    assert "/security/advisories/new" in security


def test_contributing_links_the_teaching_code_style(generated: Path) -> None:
    contributing = (generated / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "docs/teaching-code-style.md" in contributing
    assert "uv sync" in contributing
    assert "prek install" in contributing
    assert "coming" in (generated / "docs/teaching-code-style.md").read_text(encoding="utf-8")


def test_codeowners_names_the_maintainers_team(generated: Path) -> None:
    assert "* @Rakiura-Inc/maintainers" in (generated / ".github/CODEOWNERS").read_text(encoding="utf-8")


def test_ruff_limits_complexity(generated: Path) -> None:
    ruff = (generated / "ruff.toml").read_text(encoding="utf-8")
    assert '"C90",' in ruff
    assert '"PLR",' in ruff
    assert "max-complexity = 10" in ruff


def test_pytest_runs_in_parallel_and_random_order(generated: Path) -> None:
    assert '"-n", "auto"' in (generated / "pytest.toml").read_text(encoding="utf-8")
    pyproject = (generated / "pyproject.toml").read_text(encoding="utf-8")
    assert "pytest-xdist==" in pyproject
    assert "pytest-randomly==" in pyproject


def test_renovate_extends_the_org_preset(generated: Path) -> None:
    renovate = (generated / "renovate.json5").read_text(encoding="utf-8")
    assert "github>Rakiura-Inc/.github:renovate-config.json5" in renovate


def test_readme_licence_line_reads_cleanly(generated: Path) -> None:
    # The default author, "Rakiura Inc.", already ends in a full stop.
    readme = (generated / "README.md").read_text(encoding="utf-8")
    assert "Rakiura Inc. See [LICENSE](LICENSE)." in readme
    assert ".." not in readme
