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
   checkout and keep its current branch. For any other repository:
   - Resolve the registered repository checkout with
     `python .opencode/scripts/repository.py list` and use its exact path as
     `<repo>`. The registered checkout is the repository's main clone even when
     it lives under `.worktrees/`; never pass a task worktree (a linked checkout
     of a feature branch) or the current directory as `<repo>`, and never create
     a worktree from another worktree.
   - Check whether a worktree already exists for this Issue branch with
     `python .opencode/scripts/worktree.py list --repo <repo>`. If a clean
     existing worktree matches, reuse it. If the matching worktree path is
     nested (its path contains `/.worktrees/` below the worktree root or it is
     inside a repository checkout), do not reuse it silently; stop and report it
     as a nested worktree that must be migrated or removed first.
   - Otherwise create the new worktree with
     `python .opencode/scripts/worktree.py create <branch> --repo <repo>`. It
     MUST land directly under the framework worktree root
     (`OPENCODE_WORKTREE_ROOT` or this automation repository's `.worktrees/`)
     as `<worktree-root>/<sanitized-branch>`, at the first level. A path like
     `.worktrees/<repo>/.worktrees/<branch>` is forbidden. Verify the reported
     path is a direct child of the worktree root; if it is nested, stop and
     report the problem instead of continuing. Use the repository's actual
     default branch as the base.
   - Add the worktree to the VS Code workspace with
     `python .opencode/scripts/workspace.py add <worktree-path> --name <slug>`.
5. Set the optional GitHub Project status to `In progress`.
6. Inspect the repository and implement the Issue using its conventions. Work
   in explicit, named stages and record a short note per stage. Run relevant
   tests/builds and update documentation only when needed.
7. Render `.opencode/templates/summary.md` following
   `.opencode/instructions/reporting.md` and write the result to the configured
   support root (`OPENCODE_SUPPORT_ROOT`, default `dev_support/`) as
   `<issue-number>-summary.md`. Never write generated summaries into
   `.opencode/templates/`.
8. Post the structured summary as an Issue comment when possible.
9. Set the optional status to `Done` only after verification. Do not commit or
   push unless the user explicitly requests that part.
