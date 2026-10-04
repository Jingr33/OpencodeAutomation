---
description: Resolve, prepare, run, inspect, or stop a Python application using its worktree toolchain
subtask: true
---

Follow these steps:

1. Load the `toolkit-startup-python` skill.
2. Resolve the target working repository. Do not operate on the agentic
   OpenCode repository unless it is explicitly selected as the target.
3. Parse `$ARGUMENTS` as `[plan|prepare|run|status|stop|check]` followed by
   optional `--project-root <path>`, `--service <id>`,
   `--entrypoint <name>`, and `--no-prepare`.
4. Use `plan` when no action is provided.
5. Locate `python_runtime.py` in the agentic OpenCode repository. Prefer
   `OPENCODE_AUTOMATION_ROOT` when it is set.
6. Execute the resolver with the target path explicitly:

   ```text
   python <automation-root>/.opencode/scripts/python_runtime.py <action> --project-root <target> [options]
   ```

7. For `plan`, report the selected manager, environment, command, evidence,
   preparation commands, and readiness configuration without changing files.
8. For `prepare`, create or synchronize only the target project's declared
   environment and dependencies.
9. For `run`, show the resolved plan before starting. Start only when the
   entrypoint is declared and unambiguous.
10. For `status`, `stop`, or `check`, use the same target and service
    selection so the correct environment and process record are used.
11. Never use a global Python executable, shell activation, a guessed
    framework command, or an unmanaged separate terminal.
12. Report the JSON result, including preparation status, process ID, log
    paths, readiness status, and any failure.
