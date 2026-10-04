"""Bounded cross-platform command runner for OpenCode Automation."""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


def run_command(
    command: list[str] | str,
    cwd: Path | None = None,
    timeout: int = 300,
    shell: bool = False,
    env: dict[str, str] | None = None,
    capture_output: bool = True,
    max_output_bytes: int = 1024 * 1024  # 1MB
) -> dict:
    """
    Run a command with bounded execution and output capture.
    
    Args:
        command: Command to execute as argument list or string
        cwd: Working directory
        timeout: Maximum execution time in seconds
        shell: Whether to use shell execution
        env: Environment variables to set
        capture_output: Whether to capture stdout/stderr
        max_output_bytes: Maximum bytes to capture from output
    
    Returns:
        Dictionary with execution results
    """
    start_time = time.monotonic()
    
    # Prepare command
    if isinstance(command, str):
        if shell:
            cmd = command
        else:
            cmd = command.split()
    else:
        cmd = command
    
    # Prepare environment
    if env:
        full_env = os.environ.copy()
        full_env.update(env)
    else:
        full_env = None
    
    # Validate timeout
    if timeout <= 0:
        timeout = 300  # Default to 5 minutes
    
    # Run command
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                timeout=timeout,
                shell=shell,
                env=full_env,
                capture_output=True,
                text=True
            )
            stdout = result.stdout[:max_output_bytes] if result.stdout else ""
            stderr = result.stderr[:max_output_bytes] if result.stderr else ""
        else:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                timeout=timeout,
                shell=shell,
                env=full_env
            )
            stdout = ""
            stderr = ""
        
        duration = time.monotonic() - start_time
        
        return {
            "exitCode": result.returncode,
            "durationMs": int(duration * 1000),
            "timeout": False,
            "stdout": stdout,
            "stderr": stderr,
            "command": cmd,
            "cwd": str(cwd) if cwd else None,
            "platform": platform.system().lower()
        }
    
    except subprocess.TimeoutExpired as e:
        duration = time.monotonic() - start_time
        stdout = e.stdout[:max_output_bytes] if e.stdout else ""
        stderr = e.stderr[:max_output_bytes] if e.stderr else ""
        
        return {
            "exitCode": -1,
            "durationMs": int(duration * 1000),
            "timeout": True,
            "stdout": stdout,
            "stderr": stderr,
            "command": cmd,
            "cwd": str(cwd) if cwd else None,
            "platform": platform.system().lower(),
            "error": f"Command timed out after {timeout} seconds"
        }
    
    except Exception as e:
        duration = time.monotonic() - start_time
        
        return {
            "exitCode": -1,
            "durationMs": int(duration * 1000),
            "timeout": False,
            "stdout": "",
            "stderr": str(e),
            "command": cmd,
            "cwd": str(cwd) if cwd else None,
            "platform": platform.system().lower(),
            "error": str(e)
        }


def wait_for_condition(
    check_command: list[str] | str,
    timeout: int = 300,
    interval: int = 5,
    cwd: Path | None = None,
    shell: bool = False
) -> dict:
    """
    Wait for a condition to be met by running a check command.
    
    Args:
        check_command: Command that exits 0 when condition is met
        timeout: Maximum wait time in seconds
        interval: Time between checks in seconds
        cwd: Working directory
        shell: Whether to use shell execution
    
    Returns:
        Dictionary with wait results
    """
    start_time = time.monotonic()
    attempt = 0
    
    while True:
        attempt += 1
        result = run_command(
            check_command,
            cwd=cwd,
            timeout=interval,
            shell=shell
        )
        
        if result["exitCode"] == 0:
            return {
                "success": True,
                "attempts": attempt,
                "durationMs": result["durationMs"],
                "message": f"Condition met after {attempt} check(s)"
            }
        
        elapsed = time.monotonic() - start_time
        if timeout > 0 and elapsed >= timeout:
            return {
                "success": False,
                "attempts": attempt,
                "durationMs": int(elapsed * 1000),
                "message": f"Timeout reached ({timeout}s) after {attempt} attempts",
                "lastExitCode": result["exitCode"]
            }
        
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Bounded cross-platform command runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a command with bounded execution")
    run_parser.add_argument("command", nargs="+", help="Command to execute")
    run_parser.add_argument("--cwd", help="Working directory")
    run_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    run_parser.add_argument("--shell", action="store_true", help="Use shell execution")
    run_parser.add_argument("--no-capture", action="store_true", help="Don't capture output")
    run_parser.add_argument("--env", nargs="*", help="Environment variables (KEY=VALUE)")
    
    # Wait for condition
    wait_parser = subparsers.add_parser("wait", help="Wait for a condition to be met")
    wait_parser.add_argument("check", nargs="+", help="Check command")
    wait_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    wait_parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds")
    wait_parser.add_argument("--cwd", help="Working directory")
    wait_parser.add_argument("--shell", action="store_true", help="Use shell execution")
    
    args = parser.parse_args()
    
    if args.command == "run":
        cwd = Path(args.cwd) if args.cwd else None
        env = {}
        if args.env:
            for e in args.env:
                key, _, value = e.partition("=")
                env[key] = value
        
        result = run_command(
            args.command,
            cwd=cwd,
            timeout=args.timeout,
            shell=args.shell,
            capture_output=not args.no_capture,
            env=env if env else None
        )
        
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["exitCode"] == 0 else 1)
    
    elif args.command == "wait":
        cwd = Path(args.cwd) if args.cwd else None
        
        result = wait_for_condition(
            args.check,
            timeout=args.timeout,
            interval=args.interval,
            cwd=cwd,
            shell=args.shell
        )
        
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
