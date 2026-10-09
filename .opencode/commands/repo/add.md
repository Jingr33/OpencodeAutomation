---
description: Clone and register an arbitrary Git repository for development
subtask: true
---

Load the `repository` skill. Parse `$ARGUMENTS` as `<url-or-owner/name>`, with
optional `--name <name>`.

Clone the repository into `.worktrees/<name>`, never into `source/`. `<name>` is
the value of `--name`, or the repository name derived from `<url-or-owner/name>`:

```bash
python .opencode/scripts/repository.py add <url-or-owner/name> [--name <name>] --path .worktrees/<name>
```

Only pass `--path` when the user explicitly requested a different location; that
location must still be `.worktrees/<name>` unless stated otherwise.

Verify the clone, remote URL, and default branch. Do not add the clone to this
framework repository's Git history. Report the absolute path and how to target it.
