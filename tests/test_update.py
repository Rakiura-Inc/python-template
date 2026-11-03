"""`copier update` brings a later template version into a generated project and keeps its own edits."""

import shutil
from pathlib import Path

from copier import run_update

from .conftest import TEMPLATE, generate, run

IGNORED = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache")


def commit_and_tag(repository: Path, tag: str) -> None:
    """Commit everything in a repository and tag it."""
    run(["git", "add", "--all"], repository)
    identity = ["-c", "user.name=Test", "-c", "user.email=test@example.com"]
    run(["git", *identity, "commit", "--quiet", "--message", tag], repository)
    run(["git", "tag", tag], repository)


def test_update_pulls_template_changes_and_keeps_local_edits(tmp_path: Path) -> None:
    template = tmp_path / "template"
    shutil.copytree(TEMPLATE, template, ignore=IGNORED)
    run(["git", "init", "--quiet", "--initial-branch", "main"], template)
    commit_and_tag(template, "v0.0.1")

    project = generate(tmp_path / "project", src_path=template, flavour="library", project_name="demo-lib")
    assert "_commit: v0.0.1" in (project / ".copier-answers.yml").read_text(encoding="utf-8")
    with (project / "README.md").open("a", encoding="utf-8") as readme:
        readme.write("\nA line the project added.\n")
    commit_and_tag(project, "generated")

    security = template / "template/SECURITY.md.jinja"
    security.write_text(security.read_text(encoding="utf-8") + "\nA line the template added.\n", encoding="utf-8")
    commit_and_tag(template, "v0.0.2")

    run_update(dst_path=str(project), defaults=True, overwrite=True, unsafe=True, quiet=True)

    assert "_commit: v0.0.2" in (project / ".copier-answers.yml").read_text(encoding="utf-8")
    assert "A line the template added." in (project / "SECURITY.md").read_text(encoding="utf-8")
    assert "A line the project added." in (project / "README.md").read_text(encoding="utf-8")
