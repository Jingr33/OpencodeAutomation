---
description: Start the active repository's documented development processes
subtask: true
---

Inspect the repository's canonical startup instructions and manifests. For a
Python service, load `toolkit-startup-python` and use `python_runtime.py` so the
declared uv, Poetry, Pipenv, or worktree-local venv is prepared before the
service starts. Use the same process manager for status, logs, readiness, and
stop. Start only explicitly declared services; do not assume `main.py`, React,
ports, or a particular directory, and do not use separate unmanaged terminals.
