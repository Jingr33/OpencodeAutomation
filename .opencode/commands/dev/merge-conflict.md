---
description: Resolve merge conflicts for a branch or PR (e.g. /dev.merge-conflict feature/xyz --force)
agent: dev
subtask: true
---

Resolve merge conflicts for branch or PR `$ARGUMENTS`.

## Arguments

- `<branch-or-pr>` (required): Branch name or PR number/name. If a PR is provided, it will be converted to the corresponding branch name.
- `--force` (optional): If present, automatically commit and push after conflict resolution. Without this flag, stop after implementation for user review.

## Steps

1. **Resolve argument**: Determine if the input is a PR number/name or a branch name.
   - If it's a PR (numeric or matches PR pattern), fetch the PR details with `gh pr view` and extract the head branch name.
   - Otherwise, treat it as a branch name directly.

2. **Switch to branch**: Check out the specified branch locally.
   - If the branch doesn't exist locally, fetch it from the remote: `git fetch origin <branch>`.
   - Switch to the branch: `git checkout <branch>`.

3. **Update branch**: Pull the latest changes: `git pull origin <branch>`.

4. **Find and update target branch**: Determine the target/base branch of the PR.
   - If a PR was provided, use `gh pr view` to get the base branch.
   - Otherwise, use the default branch (usually `main` or `master`).
   - Fetch and update the target branch: `git fetch origin <target>` and `git checkout <target> && git pull origin <target>`.

5. **Merge target into feature**: Switch back to the feature branch and merge the target:
   ```
   git checkout <branch>
   git merge <target>
   ```
   This will trigger merge conflicts if any.

6. **Resolve merge conflicts**:
   - List conflicted files: `git diff --name-only --diff-filter=U`.
   - For each conflicted file, read the file and understand the conflict.
   - If a PR was provided, read the PR description to understand the context and intent.
   - Think about potential risks and regression bugs when resolving.
   - Resolve conflicts by editing the files to keep the correct code.
   - Stage resolved files: `git add <file>`.

7. **Stop if not forced**: If `--force` was not provided, stop here and inform the user that conflicts are resolved but not committed. Ask the user to review and commit manually.

8. **If forced - Commit and push**:
   - Commit the merge: `git commit -m "Merge <target> into <branch> (resolve conflicts)"`.
   - Push to the PR branch: `git push origin <branch>`.
   - If it was a PR, add a comment summarizing the resolution.

## Error Handling

- If the branch doesn't exist locally or remotely, abort with an error.
- If the PR doesn't exist, abort with an error.
- If there are no conflicts after merging, report success and exit early.
- If unable to automatically resolve conflicts, ask the user for guidance.
- Always explain what conflicts were found and how they were resolved.
