"""Process manager for toolkit startup skills."""

import argparse
import json
import os
import platform
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def state_path() -> Path:
    return Path(__file__).parent.parent / "state" / "processes.json"


def load_processes() -> dict[str, Any]:
    """Load process records."""
    path = state_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_processes(processes: dict[str, Any]) -> None:
    """Atomically save process records."""
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_fd, temp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(processes, f, indent=2)
        
        os.replace(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def check_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception:
        return False


def create_process_record(
    process_id: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None
) -> dict[str, Any]:
    """Create a process record."""
    return {
        "id": process_id,
        "command": command,
        "cwd": str(cwd),
        "env": {k: v for k, v in (env or {}).items() if "SECRET" not in k and "PASSWORD" not in k},
        "status": "starting",
        "pid": None,
        "processGroup": None,
        "startedAt": None,
        "stoppedAt": None,
        "logs": {
            "stdout": None,
            "stderr": None
        }
    }


def start_process(
    process_id: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    port: int | None = None,
    timeout: int = 30
) -> dict[str, Any]:
    """Start a process and track it."""
    processes = load_processes()
    
    # Check if process already exists
    if process_id in processes:
        existing = processes[process_id]
        if existing.get("status") == "running":
            # Check if process is still alive
            pid = existing.get("pid")
            if pid and is_process_alive(pid):
                return {
                    "success": False,
                    "error": f"Process {process_id} is already running with PID {pid}",
                    "process": existing
                }
    
    # Check port availability
    if port and not check_port_available(port):
        return {
            "success": False,
            "error": f"Port {port} is already in use",
            "process": None
        }
    
    # Create log files
    log_dir = Path(__file__).parent.parent / "state" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    stdout_log = log_dir / f"{process_id}_stdout.log"
    stderr_log = log_dir / f"{process_id}_stderr.log"
    
    # Create process record
    record = create_process_record(process_id, command, cwd, env)
    record["logs"]["stdout"] = str(stdout_log)
    record["logs"]["stderr"] = str(stderr_log)
    
    try:
        # Start process
        stdout_file = open(stdout_log, "w")
        stderr_file = open(stderr_log, "w")
        
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
        
        record["pid"] = process.pid
        record["processGroup"] = process.pid if platform.system() != "Windows" else None
        record["status"] = "running"
        record["startedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        processes[process_id] = record
        save_processes(processes)
        
        return {
            "success": True,
            "process": record,
            "message": f"Process {process_id} started with PID {process.pid}"
        }
    
    except Exception as e:
        record["status"] = "failed"
        record["error"] = str(e)
        processes[process_id] = record
        save_processes(processes)
        
        return {
            "success": False,
            "error": str(e),
            "process": record
        }


def is_process_alive(pid: int) -> bool:
    """Check if a process is alive."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False


def stop_process(process_id: str, force: bool = False) -> dict[str, Any]:
    """Stop a tracked process."""
    processes = load_processes()
    
    if process_id not in processes:
        return {
            "success": False,
            "error": f"Process {process_id} not found"
        }
    
    record = processes[process_id]
    pid = record.get("pid")
    
    if not pid:
        record["status"] = "stopped"
        record["stoppedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        processes[process_id] = record
        save_processes(processes)
        return {
            "success": True,
            "message": f"Process {process_id} has no PID"
        }
    
    # Check if process is alive
    if not is_process_alive(pid):
        record["status"] = "exited"
        record["stoppedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        processes[process_id] = record
        save_processes(processes)
        return {
            "success": True,
            "message": f"Process {process_id} already exited"
        }
    
    try:
        if platform.system() == "Windows":
            # On Windows, kill the process
            subprocess.run(["taskkill", "/PID", str(pid), "/F" if force else ""], check=True)
        else:
            # On POSIX, kill the process group
            if force:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            else:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
        
        record["status"] = "stopped"
        record["stoppedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        processes[process_id] = record
        save_processes(processes)
        
        return {
            "success": True,
            "message": f"Process {process_id} stopped"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_process_status(process_id: str) -> dict[str, Any]:
    """Get process status."""
    processes = load_processes()
    
    if process_id not in processes:
        return {
            "exists": False,
            "error": f"Process {process_id} not found"
        }
    
    record = processes[process_id]
    pid = record.get("pid")
    
    if pid:
        alive = is_process_alive(pid)
        if record["status"] == "running" and not alive:
            record["status"] = "exited"
            record["stoppedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            processes[process_id] = record
            save_processes(processes)
    
    return {
        "exists": True,
        "process": record
    }


def list_processes() -> dict[str, Any]:
    """List all tracked processes."""
    processes = load_processes()
    
    # Update status for all processes
    for process_id, record in processes.items():
        pid = record.get("pid")
        if pid and record["status"] == "running":
            if not is_process_alive(pid):
                record["status"] = "exited"
                record["stoppedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    save_processes(processes)
    return processes


def cleanup_exited() -> dict[str, Any]:
    """Clean up exited process records."""
    processes = load_processes()
    cleaned = []
    
    for process_id in list(processes.keys()):
        if processes[process_id]["status"] in ["exited", "stopped", "failed"]:
            del processes[process_id]
            cleaned.append(process_id)
    
    save_processes(processes)
    return {
        "cleaned": cleaned,
        "count": len(cleaned)
    }


def main():
    parser = argparse.ArgumentParser(description="Process manager for toolkit startup skills")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a process")
    start_parser.add_argument("id", help="Process ID")
    start_parser.add_argument("command", nargs="+", help="Command to execute")
    start_parser.add_argument("--cwd", help="Working directory")
    start_parser.add_argument("--port", type=int, help="Port to check availability")
    start_parser.add_argument("--timeout", type=int, default=30, help="Startup timeout")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a process")
    stop_parser.add_argument("id", help="Process ID")
    stop_parser.add_argument("--force", action="store_true", help="Force stop")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get process status")
    status_parser.add_argument("id", help="Process ID")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all processes")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up exited processes")
    
    args = parser.parse_args()
    
    if args.command == "start":
        cwd = Path(args.cwd) if args.cwd else Path.cwd()
        result = start_process(
            args.id,
            args.command,
            cwd,
            port=args.port,
            timeout=args.timeout
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)
    
    elif args.command == "stop":
        result = stop_process(args.id, force=args.force)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)
    
    elif args.command == "status":
        result = get_process_status(args.id)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("exists") else 1)
    
    elif args.command == "list":
        result = list_processes()
        print(json.dumps(result, indent=2))
    
    elif args.command == "cleanup":
        result = cleanup_exited()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
