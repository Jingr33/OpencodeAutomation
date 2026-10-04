"""Register and manage external Git repositories for the automation workspace."""

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def framework_root() -> Path:
    return Path(__file__).resolve().parents[2]


def source_root() -> Path:
    configured = os.environ.get("OPENCODE_SOURCE_ROOT", "./source")
    return Path(configured).expanduser().resolve()


def registry_path() -> Path:
    return framework_root() / ".opencode" / "state" / "repositories.json"


def load_registry() -> dict[str, Any]:
    path = registry_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(registry: dict[str, Any]) -> None:
    """Atomically save the registry using a temporary file and rename."""
    path = registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to a temporary file first
    temp_fd, temp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            f.write(json.dumps(registry, indent=2, sort_keys=True) + "\n")
        
        # Atomic rename
        os.replace(temp_path, path)
    except Exception:
        # Clean up on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def validate_repository_name(name: str) -> str:
    """Validate and sanitize repository name."""
    # Check for path traversal
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError(f"Invalid repository name (path traversal detected): {name}")
    
    # Sanitize
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    if not value:
        raise ValueError("cannot derive repository name")
    return value


def redact_remote_url(url: str) -> str:
    """Redact credentials from remote URL."""
    # Redact tokens and passwords
    url = re.sub(r'https://[^@/]+:([^@/]+)@', 'https://***:***@', url)
    url = re.sub(r'git@[^:]+:([^@]+)@', 'git@***@', url)
    return url


def repository_name(source: str) -> str:
    value = source.rstrip("/").rsplit("/", 1)[-1]
    value = value.removesuffix(".git")
    value = validate_repository_name(value)
    return value


def add_repository(args: argparse.Namespace) -> None:
    """Add a repository to the registry."""
    name = args.name or repository_name(args.source)
    name = validate_repository_name(name)
    
    # Determine if managed or external
    managed = not args.path
    target = Path(args.path).expanduser().resolve() if args.path else source_root() / f"{name}_slot0"
    
    # Validate path traversal
    try:
        target.resolve().relative_to(source_root())
    except ValueError:
        if not args.path:
            raise SystemExit(f"Managed path must be under source root: {source_root()}")
    
    if target.exists() and not (target / ".git").exists():
        raise SystemExit(f"target exists and is not a Git repository: {target}")
    
    # Clone if not exists
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        source = args.source if "://" in args.source or args.source.startswith("git@") else f"https://github.com/{args.source}.git"
        try:
            run(["git", "clone", source, str(target)])
        except subprocess.CalledProcessError as e:
            # Cleanup on clone failure
            if target.exists():
                shutil.rmtree(target)
            raise SystemExit(f"Failed to clone repository: {e}")
    
    # Get repository info
    remote = run(["git", "remote", "get-url", "origin"], cwd=target)
    branch = run(["git", "branch", "--show-current"], cwd=target)
    
    # Get default branch
    default_branch = None
    try:
        remote_info = run(["git", "remote", "show", "origin"], cwd=target)
        match = re.search(r"^\s*HEAD branch:\s*(\S+)", remote_info, re.MULTILINE)
        if match:
            default_branch = match.group(1)
    except subprocess.CalledProcessError:
        pass
    
    # Atomic registry update
    registry = load_registry()
    registry[name] = {
        "path": str(target),
        "remote": redact_remote_url(remote),
        "branch": branch,
        "defaultBranch": default_branch,
        "managed": managed,
        "createdAt": __import__('datetime').datetime.utcnow().isoformat() + "Z"
    }
    save_registry(registry)
    
    print(json.dumps({
        "name": name,
        "path": str(target),
        "remote": redact_remote_url(remote),
        "branch": branch,
        "defaultBranch": default_branch,
        "managed": managed
    }, indent=2))


def list_repositories(_: argparse.Namespace) -> None:
    """List all registered repositories."""
    registry = load_registry()
    known: dict[str, dict[str, Any]] = {}
    
    for name, entry in registry.items():
        path = Path(entry["path"])
        if path.exists() and (path / ".git").exists():
            remote = run(["git", "remote", "get-url", "origin"], cwd=path)
            branch = run(["git", "branch", "--show-current"], cwd=path)
            known[name] = {
                "path": str(path),
                "remote": redact_remote_url(remote),
                "branch": branch,
                "managed": entry.get("managed", False)
            }
    
    print(json.dumps(known, indent=2, sort_keys=True))


def remove_repository(args: argparse.Namespace) -> None:
    """Remove a repository from the registry."""
    registry = load_registry()
    entry = registry.get(args.name)
    target = Path(entry["path"]) if entry else source_root() / args.name
    target = target.expanduser().resolve()
    
    if not args.confirm:
        raise SystemExit("removal requires --confirm")
    
    if not target.exists():
        registry.pop(args.name, None)
        save_registry(registry)
        return
    
    # Check if managed
    managed = entry.get("managed", False) if entry else False
    if not managed and not args.force:
        raise SystemExit(f"External repositories cannot be removed without --force: {target}")
    
    dirty = bool(run(["git", "status", "--porcelain"], cwd=target))
    if dirty and not args.force:
        raise SystemExit(f"repository is dirty; use --force only after confirmation: {target}")
    
    worktrees = run(["git", "worktree", "list", "--porcelain"], cwd=target)
    if worktrees.count("worktree ") > 1:
        raise SystemExit("repository has linked worktrees; remove them first")
    
    shutil.rmtree(target)
    registry.pop(args.name, None)
    save_registry(registry)


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    subparsers = command.add_subparsers(dest="command", required=True)
    
    add = subparsers.add_parser("add")
    add.add_argument("source")
    add.add_argument("--name")
    add.add_argument("--path")
    add.add_argument("--managed", action="store_true", default=True)
    add.set_defaults(function=add_repository)
    
    listing = subparsers.add_parser("list")
    listing.set_defaults(function=list_repositories)
    
    remove = subparsers.add_parser("remove")
    remove.add_argument("name")
    remove.add_argument("--confirm", action="store_true")
    remove.add_argument("--force", action="store_true")
    remove.set_defaults(function=remove_repository)
    
    return command


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.function(arguments)
