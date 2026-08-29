---
description: Clone and register an arbitrary Git repository for development
subtask: true
---

Load the `repository` skill. Parse `$ARGUMENTS` as `<url-or-owner/name>`, with
optional `--name <name>` and `--path <path>`. Run:

```bash
python .opencode/scripts/repository.py add <url-or-owner/name> [--name <name>] [--path <path>]
```

Verify the clone, remote URL, and default branch. Do not add the clone to this
framework repository's Git history. Report the absolute path and how to target it.
