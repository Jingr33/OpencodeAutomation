"""Target context resolver for OpenCode Automation."""

import argparse
import json
import os
import subprocess
from pathlib import Path


def run(command: list[str], cwd: Path, check: bool = True) -> str:
    result = subprocess.run(command, cwd=cwd, check=check, text=True, capture_output=True)
    return result.stdout.strip()


def resolve_target(args: argparse.Namespace) -> dict:
    """Resolve target repository context."""
    agentic_root = Path(__file__).parent.parent.parent.resolve()
    source_root = Path(args.source_root or os.environ.get("OPENCODE_SOURCE_ROOT", str(agentic_root / "source"))).resolve()
    state_root = Path(args.state_root or os.environ.get("OPENCODE_STATE_ROOT", str(agentic_root / ".opencode" / "state"))).resolve()
    support_root = Path(args.support_root or os.environ.get("OPENCODE_SUPPORT_ROOT", str(agentic_root / "dev_support"))).resolve()
    
    # Resolution order
    target = None
    config_source = None
    
    # 1. Explicit --repo argument
    if args.repo:
        target = Path(args.repo).expanduser().resolve()
        config_source = "explicit_argument"
    
    # 2. OPENCODE_TARGET_REPO environment variable
    elif os.environ.get("OPENCODE_TARGET_REPO"):
        target = Path(os.environ["OPENCODE_TARGET_REPO"]).expanduser().resolve()
        config_source = "environment_variable"
    
    # 3. Current checkout (only if not agentic repository)
    else:
        current_dir = Path.cwd().resolve()
        git_top = None
        
        try:
            git_top = Path(run(["git", "rev-parse", "--show-toplevel"], current_dir))
        except subprocess.CalledProcessError:
            pass
        
        if git_top and git_top != agentic_root:
            target = current_dir
            config_source = "current_checkout"
        else:
            # 4. Fail closed when current checkout is agentic repository
            return {
                "error": "target_required",
                "message": "An explicit target repository is required when the current checkout is the agentic repository.",
                "phase": "resolve",
                "retryable": False,
                "action": "Select a repository with --repo or OPENCODE_TARGET_REPO."
            }
    
    # Validate target
    if not target or not target.exists():
        return {
            "error": "target_not_found",
            "message": f"Target path does not exist: {target}",
            "phase": "resolve",
            "retryable": False,
            "action": "Verify the target path exists and is accessible."
        }
    
    # Validate target is a directory
    if not target.is_dir():
        return {
            "error": "target_not_a_directory",
            "message": f"Target path is not a directory: {target}",
            "phase": "resolve",
            "retryable": False,
            "action": "Provide a directory path, not a file path."
        }
    
    # Get Git top-level directory
    try:
        git_top = Path(run(["git", "rev-parse", "--show-toplevel"], target))
    except subprocess.CalledProcessError:
        return {
            "error": "not_a_git_repository",
            "message": f"Target is not a Git repository: {target}",
            "phase": "resolve",
            "retryable": False,
            "action": "Ensure the target is a valid Git repository."
        }
    
    # Check if managed or external
    managed = False
    slot = None
    repo_name = git_top.name
    
    try:
        source_root.resolve().relative_to(agentic_root)
        if git_top.is_relative_to(source_root):
            managed = True
            # Extract slot from path name (e.g., repo_name_slot0)
            parts = git_top.name.split("_slot")
            if len(parts) == 2:
                try:
                    slot = int(parts[1])
                except ValueError:
                    pass
    except ValueError:
        pass
    
    # Get branch information
    branch = None
    detached = False
    try:
        branch = run(["git", "branch", "--show-current"], target)
        if not branch:
            branch = run(["git", "rev-parse", "--short", "HEAD"], target)
            detached = True
    except subprocess.CalledProcessError:
        pass
    
    # Get remote information
    remote = None
    try:
        remote_url = run(["git", "remote", "get-url", "origin"], target, check=False)
        if remote_url:
            remote = {
                "name": "origin",
                "url": remote_url
            }
    except subprocess.CalledProcessError:
        pass
    
    # Get worktree path
    worktree_path = str(target)
    
    # Build context record
    context = {
        "canonicalPath": str(target),
        "managed": managed,
        "gitTopLevel": str(git_top),
        "branch": branch,
        "detached": detached,
        "worktreePath": worktree_path,
        "slot": slot,
        "repositoryName": repo_name,
        "remote": remote,
        "configurationSource": config_source,
        "agenticRoot": str(agentic_root),
        "sourceRoot": str(source_root),
        "stateRoot": str(state_root),
        "supportRoot": str(support_root)
    }
    
    return context


def main():
    parser = argparse.ArgumentParser(description="Resolve target repository context")
    parser.add_argument("--repo", help="Explicit target repository path")
    parser.add_argument("--source-root", help="Source root path")
    parser.add_argument("--state-root", help="State root path")
    parser.add_argument("--support-root", help="Support root path")
    
    args = parser.parse_args()
    context = resolve_target(args)
    print(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
