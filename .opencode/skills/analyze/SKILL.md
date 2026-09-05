---
name: analyze
description: Converts runtime logs and errors into structured GitHub Issue analyses
license: MIT
compatibility: opencode
---

1. Parse only the errors present in the supplied logs.
2. Read the relevant source files in the active repository.
3. Create a GitHub Issue using `.opencode/templates/issue-analysis.md` as the
   Issue body. Set type to `bug` and include concrete file paths, line numbers,
   root cause, and possible fixes.
4. Never invent additional problems beyond what the logs evidence.
5. Report the Issue URL when done.
