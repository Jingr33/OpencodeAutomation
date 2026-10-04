# GitHub Issue Lifecycle and Migration

This document defines the hardened GitHub Issue lifecycle and migration process.

## Repository Precedence

### Resolution Order

1. Explicit `--repo <path>` argument
2. `OPENCODE_TARGET_REPO` environment variable
3. Current checkout (only if not agentic repository)
4. Fail closed when current checkout is agentic repository

### Fail-Closed Behavior

When target repository is ambiguous:
- Return error with clear message
- Require explicit repository specification
- Do not guess or use defaults

## Issue Task Schema

### Required Fields

```yaml
---
metadata:
  type: feature|bug|hotfix
  scope: repository
description: Task description
acceptance_criteria:
  - Criterion 1
  - Criterion 2
out_of_scope:
  - What this task will NOT include
---
```

### Optional Fields

```yaml
priority: low|medium|high|critical
labels: [label1, label2]
assignees: [user1, user2]
milestone: milestone-name
```

## Branch Naming

### Deterministic Branch Names

Branch names must follow the pattern:
```
<type>/<number>-<slug>
```

Where:
- `type`: Issue type (feature, bug, hotfix)
- `number`: Issue number
- `slug`: Kebab-case description

### Example

Issue #42: "Add user authentication"
Branch: `feature/42-add-user-authentication`

### Slug Generation

1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters
4. Limit to 50 characters
5. Ensure uniqueness

## Issue Creation

### Preview Before Creation

Before creating an Issue:
1. Validate Issue body against schema
2. Check for duplicate Issues
3. Preview branch name
4. Show creation details

### Duplicate Prevention

Before creating:
1. Search for existing Issues with same title
2. Check for open Issues with similar description
3. Report potential duplicates
4. Require confirmation if duplicate found

### Creation Process

```bash
# Preview
gh issue create --title "Feature: Add authentication" --body "..." --dry-run

# Create
gh issue create --title "Feature: Add authentication" --body "..."
```

## Project Synchronization

### Status Values

- `Backlog`: Not yet planned
- `Ready`: Planned and ready for work
- `In progress`: Currently being worked on
- `Blocked`: Cannot proceed
- `Done`: Completed

### Synchronization Rules

1. Set status to `Ready` when Issue is created
2. Set status to `In progress` when work begins
3. Set status to `Done` when PR is merged
4. Never mutate Issue to compensate for missing fields

### Preview Before Mutation

Before changing Project status:
1. Show current status
2. Show target status
3. Require confirmation

## Issue Migration

### Idempotent Migration

Migration must be idempotent:
1. Check if Issue already exists
2. Check if Issue is already in target state
3. Skip if already migrated
4. Report what was migrated

### Migration Process

1. Read source Issue
2. Validate target repository
3. Check for duplicates
4. Create or update target Issue
5. Update Project status
6. Report results

### Partial Failure Handling

When migration partially fails:
1. Continue with independent items
2. Report each item's status
3. Provide retry instructions
4. Never silently skip failures

## Issue Updates

### Preview Before Update

Before updating an Issue:
1. Show current state
2. Show proposed changes
3. Require confirmation

### Update Process

1. Validate changes
2. Apply changes
3. Verify changes
4. Report results

## Issue Closure

### Closure Rules

1. Link to merged PR
2. Set Project status to `Done`
3. Add closure comment
4. Archive Issue

### Auto-Closure

Issues auto-close when:
1. PR is merged with "Closes #<number>" in body
2. PR is merged with "Fixes #<number>" in body
3. PR is merged with "Resolves #<number>" in body

## Error Handling

### Common Errors

1. **Repository not found**: Verify repository path
2. **Issue not found**: Verify Issue number
3. **Permission denied**: Check GitHub authentication
4. **Rate limited**: Wait and retry
5. **Duplicate detected**: Review and confirm

### Recovery

1. Log error details
2. Provide actionable message
3. Suggest recovery steps
4. Report partial success

## Best Practices

1. **Always preview**: Show changes before applying
2. **Check duplicates**: Prevent duplicate Issues
3. **Use deterministic names**: Follow naming conventions
4. **Handle failures**: Report partial failures
5. **Idempotent operations**: Make operations rerunnable
