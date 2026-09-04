---
description: Implement a GitHub Issue in the active repository (e.g. /dev.implement 42)
agent: dev
subtask: true
---

Implement GitHub Issue `$ARGUMENTS` in the active repository.

1. Load `github-issues`, and `worktree` skills.
2. Resolve the target repository from the current checkout or explicit local
   repository path. Fetch the complete Issue body with `gh issue view`.
3. Stop for `Blocked` or `Done`; do not take over an existing `In progress` task
   without user approval.
4. If the resolved target is this agentic repository, do not create or select a
   worktree or change the current checkout; implement directly in the active
   checkout and keep its current branch. For any other repository, check whether
   a worktree already exists for this Issue branch with
   `python .opencode/scripts/worktree.py list --repo <path>`. If a clean
   existing worktree matches, reuse it. Otherwise create a new one with
   `.opencode/scripts/worktree.py`. Then add it to the VS Code workspace with
   `python .opencode/scripts/workspace.py add <worktree-path> --name <slug>`.
   Use the repository's actual default branch as the base.
5. Set the optional GitHub Project status to `In progress`.
6. Inspect the repository and implement the Issue using its conventions. Run
   relevant tests/builds and update documentation only when needed.
7. Write `.opencode/templates/summary.md` to the configured local support
   location and post the summary as an Issue comment when possible.
8. Set the optional status to `Done` only after verification. Do not commit or
   push unless the user explicitly requests that part.
