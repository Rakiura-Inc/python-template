# Rakiura-Inc/python-template

[![Tests](https://github.com/Rakiura-Inc/python-template/actions/workflows/tests.yml/badge.svg)](https://github.com/Rakiura-Inc/python-template/actions/workflows/tests.yml)
[![Git Hooks](https://github.com/Rakiura-Inc/python-template/actions/workflows/git-hooks.yml/badge.svg)](https://github.com/Rakiura-Inc/python-template/actions/workflows/git-hooks.yml)

A [Copier](https://copier.readthedocs.io/) template for every Rakiura-Inc Python repository. Each
repository it generates calls the same [shared CI workflows](https://github.com/Rakiura-Inc/.github)
and can pull later fixes to this template with `copier update`.

Built on [ulgens/python-anything](https://github.com/ulgens/python-anything) by Ülgen Sarıkavak
(MIT licence): its tooling choices, ruff rule set, formatter settings and Copier layout are his.
Thank you, Ülgen. The differences are ours: two Rakiura flavours, the shared workflows, the
security and contributor files, and the Renovate preset.

## Two flavours

| | `library` | `notebooks` |
|---|---|---|
| For | a package others install, like [rakiura-py](https://github.com/Rakiura-Inc/rakiura-py) | teaching notebooks with a small helper package, like [morning-star-nmr](https://github.com/Rakiura-Inc/morning-star-nmr) |
| Layout | `src/<package>/`, tests in `src/tests/` | `<package>/`, `notebooks/`, `notebooks/executed/`, `scripts/run_notebooks.py`, `tests/` |
| `uv.lock` | gitignored (a library is resolved fresh by whoever installs it) | committed (the notebooks and CI run from it) |
| CI | tests on every supported Python, then the wheel alone is imported and tested again | tests, then every notebook is executed headless on Colab's Python |
| Extra | `release.yml`: a `v*` tag builds, attests and attaches the files to a GitHub Release | `nbstripout` hook, `notebooks/rakiura_steps.json`, the Rakiura helper as a dependency group |

Both are built with hatchling, because something installs them: `pip install git+https://...` in
a notebook's setup cell, or a user's install.

## What every generated repository gets

- `pyproject.toml` (uv, exact dev-tool pins in `[dependency-groups]`, Python 3.11 to 3.15),
  `ruff.toml` (the python-anything rule set plus complexity limits: C901 at 10, PLR branch,
  argument, return and statement limits), `pytest.toml` (pytest-xdist in parallel, pytest-randomly
  order), `.pre-commit-config.yaml`, `.editorconfig`, `yamlfmt.yaml`, `pyproject-fmt.toml`,
  `renovate.json5` (extends the Rakiura-Inc preset).
- Git hooks: pre-commit-hooks, pyproject-fmt, uv-lock, nbstripout, ruff check and format,
  yamlfmt, check-jsonschema (workflows, required timeouts, Renovate config), zizmor
  (`--persona=auditor`) and codespell.
- `.github/workflows/`: `tests.yml`, `git-hooks.yml`, `pip-audit.yml` (also weekly),
  `scorecard.yml`, and `release.yml` for a library. Each is a few lines that call a shared
  workflow pinned to a commit SHA.
- `README.md`, `LICENSE` (MIT, BSD-3-Clause, Apache-2.0, GPL-3.0-or-later or none),
  `CITATION.cff`, `SECURITY.md` (private reporting through GitHub security advisories),
  `CONTRIBUTING.md`, `docs/teaching-code-style.md` (a placeholder until the guide is written),
  `CHANGELOG.md` and `.github/CODEOWNERS`.
- `.copier-answers.yml`, which records the answers and the template version for `copier update`.

## Use it

You need [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
uvx copier copy --trust gh:Rakiura-Inc/python-template my-repo
```

`--trust` lets the template run its two tasks: `git init` and, for notebooks, `uv lock`. Copier
asks:

| Question | Default |
|---|---|
| `flavour` | `library` |
| `project_name`: the repository name | `my-project` |
| `package_name`: the import name | the project name with underscores |
| `project_description` | empty |
| `github_org` | `Rakiura-Inc` |
| `author_name` | `Rakiura Inc.` |
| `license` | `MIT` |
| `copyright_year` | this year |
| `min_python` | `3.11` (tested up to 3.15) |
| `colab_python` (notebooks): the Python CI runs the notebooks on | `3.13`, Colab's runtime 2026.10 |
| `use_ty`: type check with ty | yes for a library |
| `codeowners` | `@Rakiura-Inc/maintainers` |

Then follow the steps it prints: `uv sync`, `uvx prek install`, `uvx prek run --all-files`,
commit and push.

### Pull in template fixes later

```sh
uvx copier update --trust
```

Copier compares the template version in `.copier-answers.yml` with the latest tag, and applies
only what changed in the template, keeping the repository's own edits. Review the diff, fix any
conflicts, run `uvx prek run --all-files` and open a pull request.

### Adopt the template in an existing repository

1. From a clean checkout, on a new branch: `uvx copier copy --trust gh:Rakiura-Inc/python-template .`
   and answer to match the repository (name, package, flavour, licence).
2. Review every file Copier offers to overwrite. Keep the repository's own code, README and
   dependencies; take the template's config, workflows and policy files.
3. Commit `.copier-answers.yml` with the rest. From then on, `copier update` works as above.

## Change the template

```sh
uv sync
uv run pytest          # generates both flavours and runs each one's own checks; tests copier update
uvx prek run --all-files
```

The tests generate a project of each flavour and run, inside it, what its CI runs: `uv sync`,
pytest, ruff, ty (library), the wheel build and an isolated import, the notebook execution
(notebooks) and every git hook, zizmor included. Another test makes a tagged copy of the template,
generates from it, changes the template and checks that `copier update` brings the change in.
CI runs them on Python 3.11 and 3.15.

Renovate updates the pins inside the template too: the pre-commit hooks, the dev-tool versions in
`template/pyproject.toml.jinja` and the shared-workflow SHAs in `template/.github/workflows/`.

To release: merge to `main`, then tag it (`git tag v0.2.0 && git push origin v0.2.0`). Copier
uses the latest tag.

## Licence

MIT. Copyright 2026 Rakiura Inc., and copyright 2026 Ülgen Sarıkavak for the parts that come from
python-anything. See [LICENSE](LICENSE).
