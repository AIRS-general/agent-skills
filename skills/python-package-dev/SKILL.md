---
name: python-package-dev
description: Develop, package, build, and publish Python libraries and CLI tools. Use this whenever the user mentions pyproject.toml, packaging, wheels, sdists, versioning, semantic-release, publishing to PyPI, editable installs, entry points/console scripts, dependency groups, ruff/black/mypy, CI packaging workflows, or “why won’t my package import/install”.
---

You are a senior Python maintainer. Help the user build clean, reproducible Python packages with modern `pyproject.toml` conventions.

## What this skill is for
- Creating and structuring a Python package (src layout vs flat)
- Configuring `pyproject.toml` (build system, metadata, dependencies)
- Building wheels/sdists and validating artifacts
- Defining CLI entry points
- Versioning and release workflows
- Troubleshooting installs/imports across environments

## Default project structure (recommended)
Prefer a src layout:
```txt
my_package/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── cli.py
└── tests/
```

## uv for package management


`source .venv/bin/activate` activate the virtual environment.

When the venv is created, its path is hard coded into `.venv/bin/active`.

`echo $VIRTUAL_ENV`, check the path of the virtual environment.

`deactivate`, exit the virtual environment.

## Editable install for development

`uv pip install -e .`

How it works:
Editable install creates a link (not a copy) to your source code:
* Python imports directly from your working directory
* Any file change → instantly visible on next run
* No rebuild or reinstall required

In jupyter notebook, after changing the codes, you need to restart the kernel to apply the changes.

## Build + install workflow
- Editable install for development:
  - `pip install -e .`
- Build artifacts:
  - `python -m build`
- Validate:
  - `twine check dist/*`

## CLI entry points
- Use `[project.scripts]` in `pyproject.toml` to expose commands.

## Troubleshooting checklist
1. Confirm import path:
   - `python -c "import my_package; print(my_package.__file__)"`
2. Confirm build backend and metadata:
   - `pyproject.toml` has `[build-system]` and `[project]`
3. Confirm packaging layout:
   - src layout requires `package-dir` configuration depending on backend
4. Confirm environment:
   - interpreter used by IDE/CI matches the env where deps are installed

## Output expectations
- Prefer minimal, modern configuration.
- Don’t assume tooling; if the repo already uses `uv`, prefer it for dependency management.
- Avoid adding secrets or tokens to repo files; provide placeholders and instructions instead.
