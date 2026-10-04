---
name: toolkit-startup-python
description: Use when starting, preparing, testing, or stopping a Python application in a target worktree with uv, requirements.txt, Poetry, Pipenv, or a virtual environment.
---

# Python Toolkit Startup

This skill owns Python runtime selection for a target repository. It must be
used instead of running the global `python`, `pip`, `pytest`, or application
entrypoint directly.

## Resolution Rules

Resolve the target worktree first. Use `opencode.project.json` when present. If
it does not specify a manager, detect the first applicable manifest in this
order:

1. `uv.lock` -> `uv`
2. `poetry.lock` -> Poetry
3. `Pipfile.lock` or `Pipfile` -> Pipenv
4. `requirements.txt` or `requirements-*.txt` -> local virtual environment and pip
5. `pyproject.toml` -> local virtual environment and pip

The environment is local to the target worktree. Use `.venv` when available or
when no environment exists; respect an existing `venv` and explicit
`python.environment`/`pythonEnvironment` configuration. Never activate an
environment in the shell and never use a virtual environment from another
worktree.

## Entrypoints

Use this priority:

1. A selected profile service command.
2. `run` or `python.run` in `opencode.project.json`.
3. One declared `[project.scripts]`, `[project.gui-scripts]`, or
   `[tool.poetry.scripts]` entry in `pyproject.toml`.
4. An explicitly selected `--entrypoint`.

If there are multiple entrypoints, require `--entrypoint` or `--service`. Do
not infer a Flask, Django, FastAPI, Uvicorn, or custom command from filenames
or dependencies.

## Tool Commands

Use the resolver from the agentic OpenCode repository. Prefer the absolute
`OPENCODE_AUTOMATION_ROOT` environment variable when the current directory is
the target worktree. The command body should pass the target path explicitly:

```text
python <automation-root>/.opencode/scripts/python_runtime.py plan --project-root <target>
python <automation-root>/.opencode/scripts/python_runtime.py prepare --project-root <target>
python <automation-root>/.opencode/scripts/python_runtime.py run --project-root <target>
```

For a profile service or ambiguous entrypoint, add `--service <id>` or
`--entrypoint <name>`. The resolver returns the exact command, manager,
environment, evidence, preparation commands, and process id.

## Preparation

Preparation is deterministic:

- `uv`: `uv sync --locked` when `uv.lock` exists, otherwise `uv sync`.
- Poetry: `poetry install`.
- Pipenv: `pipenv sync` when `Pipfile.lock` exists, otherwise `pipenv install`.
- pip: create the worktree-local environment, then install
  `requirements.txt` (or the explicitly configured `python.requirements`
  file); for a package-only `pyproject.toml`, install it with `pip install -e .`.
  Multiple unconfigured `requirements-*.txt` files are an ambiguity and must
  be selected explicitly.

Do not silently install into the global interpreter. If the selected package
manager is unavailable, stop and report the missing executable.

## Execution

The resolver wraps commands as follows:

- uv: `uv run ...`
- Poetry: `poetry run ...`
- Pipenv: `pipenv run ...`
- pip/venv: the environment's `python` executable or its `Scripts`/`bin`
  directory on `PATH`.

Use `run` for long-running applications. It records the process, logs, working
directory, environment summary, and readiness result. Use `status` and `stop`
with the same target and service selection. HTTP, TCP, file, and process
readiness checks are supported only when declared in the profile.

## Profile Example

```json
{
  "version": 1,
  "projectType": "python",
  "root": ".",
  "python": {
    "manager": "uv",
    "run": ["python", "-m", "blobs"]
  },
  "services": [
    {
      "id": "api",
      "command": ["python", "-m", "uvicorn", "blobs.api:app"],
      "readiness": {
        "type": "http",
        "url": "http://127.0.0.1:8000/health",
        "timeoutSeconds": 60
      }
    }
  ]
}
```

The profile command is a payload. The resolver supplies the package-manager
wrapper, so do not write both `uv run` and `python.run` unless the command is
intentionally a fully managed command that the resolver should preserve.
