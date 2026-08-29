"""Register and manage external Git repositories for the automation workspace."""

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def run(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def framework_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repository_root() -> Path:
    configured = os.environ.get("OPENCODE_REPO_ROOT")
    return Path(configured).expanduser().resolve() if configured else framework_root() / "repositories"


def registry_path() -> Path:
    return framework_root() / ".opencode" / "state" / "repositories.json"


def load_registry() -> dict[str, Any]:
    path = registry_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(registry: dict[str, Any]) -> None:
    path = registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def repository_name(source: str) -> str:
    value = source.rstrip("/").rsplit("/", 1)[-1]
    value = value.removesuffix(".git")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-")
    if not value:
        raise ValueError("cannot derive repository name")
    return value


def add_repository(args: argparse.Namespace) -> None:
    name = args.name or repository_name(args.source)
    target = Path(args.path).expanduser().resolve() if args.path else repository_root() / name
    if target.exists() and not (target / ".git").exists():
        raise SystemExit(f"target exists and is not a Git repository: {target}")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        source = args.source if "://" in args.source or args.source.startswith("git@") else f"https://github.com/{args.source}.git"
        run(["git", "clone", source, str(target)])
    remote = run(["git", "remote", "get-url", "origin"], cwd=target)
    branch = run(["git", "branch", "--show-current"], cwd=target)
    registry = load_registry()
    registry[name] = {"path": str(target), "remote": remote, "branch": branch}
    save_registry(registry)
    print(json.dumps(registry[name], indent=2))


def list_repositories(_: argparse.Namespace) -> None:
    registry = load_registry()
    known: dict[str, dict[str, str]] = {}
    for name, entry in registry.items():
        path = Path(entry["path"])
        if path.exists() and (path / ".git").exists():
            known[name] = {
                "path": str(path),
                "remote": run(["git", "remote", "get-url", "origin"], cwd=path),
                "branch": run(["git", "branch", "--show-current"], cwd=path),
            }
    root = repository_root()
    if root.exists():
        for path in root.iterdir():
            if path.is_dir() and (path / ".git").exists() and path.name not in known:
                known[path.name] = {
                    "path": str(path),
                    "remote": run(["git", "remote", "get-url", "origin"], cwd=path),
                    "branch": run(["git", "branch", "--show-current"], cwd=path),
                }
    print(json.dumps(known, indent=2, sort_keys=True))


def remove_repository(args: argparse.Namespace) -> None:
    registry = load_registry()
    entry = registry.get(args.name)
    target = Path(entry["path"]) if entry else repository_root() / args.name
    target = target.expanduser().resolve()
    if not args.confirm:
        raise SystemExit("removal requires --confirm")
    if not target.exists():
        registry.pop(args.name, None)
        save_registry(registry)
        return
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
