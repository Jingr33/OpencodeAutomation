---
description: Update an existing GitHub Issue without implementing it
subtask: true
---

Load `github-issues`. The first argument is a required Issue number. Supported flags:
`--title`, `--status`, `--type`, `--scope`, `--description`,
`--acceptance-criteria`, `--out-of-scope`, and `--comment`. Validate that the
Issue exists first, fetch its current body, surgically update requested sections,
and use the optional Project only when configured. Never create an Issue or edit
source code. Stop with a confirmation of the changed fields.
