---
description: Analyze runtime logs and create numbered local issue analysis files
subtask: true
---

Load the `analyze` skill. Parse only problems present in the supplied log output,
inspect relevant active-repository source files, and create sequential
`issues/<NNN>-<slug>/issue.md` files from `.opencode/templates/issue-analysis.md`.
Do not create GitHub Issues and do not invent additional problems.
