---
description: Stage, commit, push, and create a pull request for reviewed changes
agent: sync
subtask: true
---

Run the full synchronization workflow for the active branch. Load
`github-management` when review metadata is involved. Use a summary from the
configured local support directory when available; otherwise write a concise PR
body from the diff. Confirm the final branch and PR URL.
