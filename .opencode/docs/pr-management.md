# GitHub Pull Request Management

This document defines deterministic pull request resolution and review-thread handling.

## PR Resolution

### Resolution Order

1. Explicit `--pr <number>` argument
2. Current branch's pull request
3. Search by branch name
4. Fail closed if multiple PRs found

### Repository Precedence

1. Explicit `--repo <path>` argument
2. `OPENCODE_TARGET_REPO` environment variable
3. Current checkout (only if not agentic repository)
4. Fail closed when target is ambiguous

## Review Thread Retrieval

### Paginated Retrieval

Retrieve all review threads using pagination:

```bash
gh pr view <number> --json reviews,comments
```

### Data Collection

For each review thread:
1. Review author
2. Review state (APPROVED, CHANGES_REQUESTED, COMMENTED)
3. Review body
4. Comments in thread
5. Resolution status

### Thread Classification

Classify threads as:
- **Actionable**: Requires code changes
- **Informational**: No action needed
- **Obsolete**: Outdated feedback
- **Resolved**: Already addressed

## Action Classification

### Actionable Feedback

- Code change requests
- Bug reports
- Security concerns
- Performance issues

### Informational Feedback

- Questions
- Suggestions
- Documentation requests
- Style preferences

### Obsolete Feedback

- Outdated comments
- Superseded requests
- Already addressed issues

## Confirmation Requirements

### Before Replying

1. Show thread content
2. Show proposed reply
3. Require confirmation

### Before Resolution

1. Show thread status
2. Show resolution action
3. Require confirmation

## Thread Revalidation

### Before Mutation

Immediately before any mutation:
1. Re-fetch thread state
2. Check if thread was modified
3. Verify resolution status
4. Abort if state changed

### State Change Detection

If thread state changed:
1. Report current state
2. Show what changed
3. Require re-confirmation

## Per-Thread Action Results

### Result Schema

```json
{
  "threadId": "12345",
  "action": "resolve",
  "status": "succeeded",
  "timestamp": "2026-09-04T16:00:00Z",
  "details": "Thread resolved successfully"
}
```

### Partial Failure Handling

When some threads fail:
1. Continue with independent threads
2. Report each thread's status
3. Provide retry instructions
4. Never silently skip failures

## PR Operations

### Create PR

**Syntax:**
```
pr-create [--title <title>] [--body <body>] [--base <branch>]
```

**Preconditions:**
- Branch has commits
- No existing PR for branch
- Base branch exists

**Side Effects:**
- Creates pull request
- Adds labels

### Update PR

**Syntax:**
```
pr-update <number> [--title <title>] [--body <body>]
```

**Preconditions:**
- PR exists
- User has permission

**Side Effects:**
- Updates PR fields

### Review PR

**Syntax:**
```
pr-review <number> [--comment <comment>] [--approve | --request-changes]
```

**Preconditions:**
- PR exists
- User has permission

**Side Effects:**
- Adds review to PR

### Resolve Thread

**Syntax:**
```
pr-resolve <pr-number> <thread-id>
```

**Preconditions:**
- PR exists
- Thread exists
- Thread is actionable

**Side Effects:**
- Marks thread as resolved

## Error Handling

### Common Errors

1. **PR not found**: Verify PR number
2. **Thread not found**: Verify thread ID
3. **Permission denied**: Check GitHub authentication
4. **Rate limited**: Wait and retry
5. **State changed**: Revalidate and retry

### Recovery

1. Log error details
2. Provide actionable message
3. Suggest recovery steps
4. Report partial success

## Best Practices

1. **Always preview**: Show changes before applying
2. **Revalidate state**: Check state before mutation
3. **Handle failures**: Report partial failures
4. **Use pagination**: Retrieve all review data
5. **Classify feedback**: Categorize review threads
