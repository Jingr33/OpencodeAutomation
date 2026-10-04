---
description: Start the active repository's backend or service process
subtask: true
---

Detect the backend entrypoint and documented command from the active repository.
If it is a Python project, load `toolkit-startup-python` and use
`python_runtime.py` with the explicit target path for plan, preparation, and
run. Report the selected manager, environment, and command before running it.
For other technologies preserve their declared package manager. Report the
command before running it if the repository has multiple candidates. Never
invent framework-specific flags or ports.
