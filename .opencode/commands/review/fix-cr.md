---
description: Process unresolved review comments on the current pull request
agent: dev
subtask: true
---

Load `code-review`, `github-management`, and `github-issues`. Resolve the active PR and
its Issue dynamically. Fetch all review threads, classify each as a code fix,
question, acknowledgment, outdated comment, or skipped item, and process every
unresolved thread. Implement fixes and run relevant checks before replying.
Without `force`, stop before commit/push and ask for confirmation. With `force`,
commit and push only the requested branch. Write a review-fix summary using
`.opencode/templates/fix-cr.md` and never create a new PR.
