---
name: windows-credential-manager
description: Resolves configured Windows Credential Manager entries for remote authentication without exposing passwords
license: MIT
compatibility: opencode
---

# Windows Credential Manager Workflow

Run these steps only when
`OPENCODE_CLUSTER_AUTH=windows-credential-manager` is configured.

1. Load the cluster env file without executing or printing it.
2. Require `OPENCODE_CLUSTER_CREDENTIAL_TARGET`. If it is missing, ask the
   user for the credential target, never for the password.
3. Resolve the target through the available Windows Credential Manager
   integration and retain the result as a secure credential object.
4. Do not print, log, serialize, put the credential in command arguments, put it
   in environment variables, or write it to a file. Do not use
   `cmdkey /list` to retrieve passwords.
5. Require `OPENCODE_CLUSTER_SSH_COMMAND` for SSH operations and
   `OPENCODE_CLUSTER_SCP_COMMAND` for SCP operations. Each helper must consume
   the credential object without exposing its password.
6. If a supported helper is unavailable, stop with:
   `a supported Credential Manager helper or SSH key/agent is required`.
   Never fall back to password interpolation.
