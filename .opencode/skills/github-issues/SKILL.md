---
name: github-issues
description: GitHub Issue creation, project sync, and Issue conventions (never implements)
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
Issue, and optionally add it to the configured project with status `Backlog`.
**Stop after reporting the Issue URL. Do not implement the task.**

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

1. **NEVER implement the task.** This skill is exclusively for Issue creation
   and project management. Stop after creating the Issue, optionally adding it
   to the GitHub Project, and reporting the Issue URL.
2. Always read the complete Issue body before creating it.
3. Respect `Blocked`, `In progress`, and `Done` unless the user explicitly asks
   to take over or reopen work.
4. Do not write code, run tests, or perform any implementation work.
