---
name: github-issues
description: GitHub Issue lifecycle, project sync, and Issue conventions
license: MIT
compatibility: opencode
---

# Skill: github-issues

## Resolve Repository

Prefer the active checkout:

```bash
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Use `OPENCODE_GITHUB_REPO` when the active checkout is the framework repository
and the task targets a registered repository.

## Fetch An Issue

```bash
gh issue view <number> --repo "$OPENCODE_GITHUB_REPO" --json number,title,body,state,url
```

If the variable is unset, omit `--repo`. Extract metadata from the Issue body,
not from a hard-coded project. A branch name matching `<type>/<number>-<slug>`
is the fallback when no Issue number is supplied.

## Create An Issue

Use `.opencode/templates/issue-task.md`, derive a kebab-case slug, create the
Issue, and optionally add it to the configured project. Do not create a branch
or worktree here; branch and worktree creation is the responsibility of the
dev and CR commands that operate on the Issue.

## Optional Project

Only run project commands when `OPENCODE_GITHUB_PROJECT` is set:

```bash
gh project item-add "$OPENCODE_GITHUB_PROJECT" --owner "$OPENCODE_GITHUB_PROJECT_OWNER" --url <issue-url>
gh project item-edit "$OPENCODE_GITHUB_PROJECT" --owner "$OPENCODE_GITHUB_PROJECT_OWNER" --url <issue-url> --field Status --value "<status>"
```

The owner defaults to the repository owner. If a project field or status does
not exist, do not mutate the Issue to compensate; report the limitation.

## Issue Structure

Issues created by this workflow use:

```markdown
## Metadata
- **Type**: feature
- **Scope**: repository

## Description
...

## Acceptance Criteria
- [ ] ...

## Out of Scope
...
```

Use `bug` or `hotfix` to include reproduction, expected behavior, and actual
behavior sections. Scope is free text unless the target repository defines an
enum.

## Status Lifecycle

Use GitHub Project statuses `Backlog`, `Ready`, `In progress`, `Blocked`, and
`Done` when that project has a compatible Status field. If no project exists,
the Issue remains the source of truth and the skipped project operation must be
reported.

## Rules

1. Always read the complete Issue body before implementing it.
2. Respect `Blocked`, `In progress`, and `Done` unless the user explicitly asks
   to take over or reopen work.
3. Create one branch and one worktree per concurrent task. The dev and CR
   commands own this; Issue creation must not create branches or worktrees.
   Prefer reusing an existing clean worktree for the same branch.
4. Record implementation summaries in the configured local support directory and
   post the summary to the Issue when GitHub access is available.
