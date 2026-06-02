"""Run every standalone test_*.py under tests/, optionally filtered by subdir.

Each test file is invoked as a script (each has its own `if __name__ == "__main__"`
block that exits 0 on PASS, 1 on FAIL). Aggregates the results and exits non-zero
if any test failed.

Usage:
    python scripts/run_tests.py                       # run all tests
    python scripts/run_tests.py --emulator memu       # only tests/memu/
    python scripts/run_tests.py --emulator clash-royale
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--emulator",
        default=None,
        help="Only run tests under tests/<emulator>/ (e.g. memu, clash-royale)",
    )
    args = parser.parse_args()

    base = REPO_ROOT / "tests"
    if args.emulator:
        base = base / args.emulator
        if not base.is_dir():
            print(f"no test directory: {base}", file=sys.stderr)
            return 2

    test_files = sorted(base.rglob("test_*.py"))
    if not test_files:
        print(f"no test files found under {base}", file=sys.stderr)
        return 2

    print(f"discovered {len(test_files)} test file(s) under {base.relative_to(REPO_ROOT)}:")
    for f in test_files:
        print(f"  - {f.relative_to(REPO_ROOT)}")

    failed: list[Path] = []
    for f in test_files:
        rel = f.relative_to(REPO_ROOT)
        print(f"\n===== {rel} =====")
        result = subprocess.run([sys.executable, str(f)], check=False)
        if result.returncode != 0:
            failed.append(rel)

    print("\n===== summary =====")
    print(f"  ran:    {len(test_files)}")
    print(f"  passed: {len(test_files) - len(failed)}")
    print(f"  failed: {len(failed)}")
    for f in failed:
        print(f"    - {f}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
