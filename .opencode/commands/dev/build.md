---
description: Build and verify the active repository
agent: build
subtask: true
---

Inspect the active repository and run its existing dependency, compile, test, and
lint checks. Detect the language and package manager first. Do not install missing
dependencies or change files unless the user explicitly requests it. Report every
command and failure.
