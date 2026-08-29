"""Manage a VS Code multi-root workspace file for worktrees and the agentic repo."""

import argparse
import json
import os
from pathlib import Path

WORKSPACE_FILE = "opencode-automation.code-workspace"
AGENTIC_NAME = "opencode-automation"


def workspace_path(root: Path) -> Path:
    return root / WORKSPACE_FILE


def load(root: Path) -> dict:
    wp = workspace_path(root)
    if wp.exists():
        return json.loads(wp.read_text(encoding="utf-8"))
    return {"folders": [], "settings": {}}


def save(root: Path, data: dict) -> None:
    wp = workspace_path(root)
    wp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def canonical(path: str, root: Path) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = root / p
    try:
        return str(p.resolve().relative_to(root))
    except ValueError:
        return str(p.resolve())


def ensure_agentic(args: argparse.Namespace) -> None:
    root = Path(args.repo or os.getcwd()).expanduser().resolve()
    data = load(root)
    agentic_entry = {"path": ".", "name": AGENTIC_NAME}
    existing = [f for f in data["folders"] if f.get("name") == AGENTIC_NAME or f.get("path") == "."]
    if not existing:
        data["folders"].insert(0, agentic_entry)
        save(root, data)
    print(json.dumps(data["folders"], indent=2))


def add(args: argparse.Namespace) -> None:
    root = Path(args.repo or os.getcwd()).expanduser().resolve()
    target = Path(args.path).expanduser().resolve()
    name = args.name or target.name
    rel = canonical(str(target), root)
    data = load(root)
    already = any(canonical(f.get("path", ""), root) == rel for f in data["folders"])
    if already:
        print(json.dumps({"status": "unchanged", "path": rel, "name": name}, indent=2))
        return
    data["folders"].append({"path": rel, "name": name})
    save(root, data)
    print(json.dumps({"status": "added", "path": rel, "name": name}, indent=2))


def remove(args: argparse.Namespace) -> None:
    root = Path(args.repo or os.getcwd()).expanduser().resolve()
    target = args.target
    data = load(root)
    before = len(data["folders"])
    data["folders"] = [
        f for f in data["folders"]
        if f.get("path") != target and f.get("name") != target
    ]
    removed = before != len(data["folders"])
    save(root, data)
    print(json.dumps({"removed": removed, "path": target}, indent=2))


def listing(args: argparse.Namespace) -> None:
    root = Path(args.repo or os.getcwd()).expanduser().resolve()
    data = load(root)
    print(json.dumps(data["folders"], indent=2))


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    sub = command.add_subparsers(dest="command", required=True)

    ea = sub.add_parser("ensure-agentic")
    ea.add_argument("--repo")
    ea.set_defaults(function=ensure_agentic)

    add_p = sub.add_parser("add")
    add_p.add_argument("path")
    add_p.add_argument("--name")
    add_p.add_argument("--repo")
    add_p.set_defaults(function=add)

    rm_p = sub.add_parser("remove")
    rm_p.add_argument("target")
    rm_p.add_argument("--repo")
    rm_p.set_defaults(function=remove)

    ls = sub.add_parser("list")
    ls.add_argument("--repo")
    ls.set_defaults(function=listing)

    return command


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.function(arguments)
