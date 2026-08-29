---
description: Implement a GitHub Issue in an isolated worktree (e.g. /dev.implement 42)
agent: dev
subtask: true
---

Implement GitHub Issue `$ARGUMENTS` in the active repository.

1. Load `github-issues`, and `worktree` skills.
2. Resolve the target repository from the current checkout or explicit local
   repository path. Fetch the complete Issue body with `gh issue view`.
3. Stop for `Blocked` or `Done`; do not take over an existing `In progress` task
   without user approval.
4. Create or select a dedicated branch and worktree with
   `.opencode/scripts/worktree.py`. Use the repository's actual default branch.
5. Set the optional GitHub Project status to `In progress`.
6. Inspect the repository and implement the Issue using its conventions. Run
   relevant tests/builds and update documentation only when needed.
7. Write `.opencode/templates/summary.md` to the configured local support
   location and post the summary as an Issue comment when possible.
8. Set the optional status to `Done` only after verification. Do not commit or
   push unless the user explicitly requests that part.
