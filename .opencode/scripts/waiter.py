"""Wait until a command succeeds without making the agent poll repeatedly."""

import argparse
import shlex
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait until a check command succeeds.")
    parser.add_argument("-c", "--check", required=True, help="Command that exits 0 when ready.")
    parser.add_argument("-i", "--interval", type=int, default=15)
    parser.add_argument("-t", "--timeout", type=int, default=0, help="Maximum seconds; 0 means unlimited.")
    args = parser.parse_args()
    start = time.monotonic()
    attempt = 0
    while True:
        attempt += 1
        result = subprocess.run(shlex.split(args.check), check=False)
        if result.returncode == 0:
            print(f"[waiter] Condition met after {attempt} check(s).")
            return 0
        elapsed = time.monotonic() - start
        if args.timeout > 0 and elapsed >= args.timeout:
            print(f"[waiter] Timeout reached ({args.timeout}s). Last exit code: {result.returncode}")
            return 1
        print(f"[waiter] Check {attempt} failed (exit {result.returncode}). Retrying in {args.interval}s...")
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
