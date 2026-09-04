---
description: Analyze runtime logs and create a GitHub Issue from the findings
subtask: true
---

Load the `analyze` skill and `github-issues`. Parse only problems present in the
supplied log output, inspect relevant active-repository source files, and create
a GitHub Issue from `.opencode/templates/issue-analysis.md`. Include concrete
file paths, line numbers, root cause, and possible fixes in the Issue body. Set
the Issue type to `bug`. Report the Issue URL.
Do not invent additional problems.
