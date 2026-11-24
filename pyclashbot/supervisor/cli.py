"""Offline-first supervisor CLI: plan, validate, and a guarded run skeleton."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyclashbot.supervisor.alloc import AllocationConflictError, GuestAllocator, validate_plan
from pyclashbot.supervisor.guest import DEFAULT_DOCKER_IMAGE, DockerRuntime, GuestManager
from pyclashbot.supervisor.metrics import MetricsRegistry
from pyclashbot.supervisor.runner import (
    DEFAULT_LOCK_PATH,
    Supervisor,
    guest_child_argv,
    guest_child_env,
)
from pyclashbot.supervisor.spec import GuestSpec, GuestSpecError

if TYPE_CHECKING:
    from collections.abc import Sequence


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pyclashbot.supervisor.cli",
        description="Plan, validate, and (optionally) run isolated py-clash-bot guests.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Print the deterministic guest plan as JSON.")
    plan.add_argument("--count", type=int, default=2)
    plan.add_argument("--start", type=int, default=0)

    validate = sub.add_parser("validate", help="Admission-check a JSON plan.")
    validate.add_argument("file", type=Path)

    run = sub.add_parser("run", help="Dry-run the child argv/env, or execute when asked.")
    run.add_argument("--count", type=int, default=2)
    run.add_argument("--start", type=int, default=0)
    run.add_argument("--execute", action="store_true", help="Actually spawn guests (live docker).")
    run.add_argument("--image", default=DEFAULT_DOCKER_IMAGE)
    run.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    run.add_argument("--ready-timeout", type=float, default=300.0)
    run.add_argument("--max-restarts", type=int, default=3)
    return parser


def _dump(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _plan(count: int, start: int) -> list[GuestSpec]:
    if count < 0:
        raise GuestSpecError(f"count must be >= 0, got {count}")
    return list(GuestAllocator().allocate_range(start, count))


def _load_plan(path: Path) -> list[GuestSpec]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw: Any = payload.get("guests") if isinstance(payload, dict) else payload
    if not isinstance(raw, list):
        raise GuestSpecError("plan must be a JSON list or an object with a 'guests' list")
    return [GuestSpec.from_dict(item) for item in raw]


def cmd_plan(args: argparse.Namespace) -> int:
    specs = _plan(args.count, args.start)
    _dump({"guests": [spec.to_dict() for spec in specs]})
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        specs = _load_plan(args.file)
        validate_plan(specs)
    except (OSError, json.JSONDecodeError, GuestSpecError, KeyError, TypeError) as exc:
        _dump({"ok": False, "error": str(exc)})
        return 2
    _dump({"ok": True, "count": len(specs), "guests": [spec.to_dict() for spec in specs]})
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    try:
        specs = _plan(args.count, args.start)
    except (AllocationConflictError, GuestSpecError) as exc:
        _dump({"ok": False, "error": str(exc)})
        return 2

    if not args.execute:
        _dump(
            {
                "dry_run": True,
                "guests": [
                    {
                        "serial": spec.serial,
                        "argv": guest_child_argv(spec),
                        "env": guest_child_env(spec),
                    }
                    for spec in specs
                ],
            }
        )
        return 0

    metrics = MetricsRegistry()
    manager = GuestManager(DockerRuntime(image=args.image), ready_timeout=args.ready_timeout)
    supervisor = Supervisor(
        manager,
        lock_path=args.lock_file,
        max_restarts=args.max_restarts,
    )
    supervisor.lock.acquire()
    try:
        for spec in specs:
            supervisor.start(spec)
            metrics.for_guest(spec.serial, index=spec.index)
            if manager.wait_ready(spec):
                metrics.update(spec.serial, ready=True)
            else:
                metrics.update(spec.serial, ready=False)
        _dump({"ok": True, "metrics": metrics.to_dict()})
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    finally:
        supervisor.shutdown()


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "plan":
        return cmd_plan(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "run":
        return cmd_run(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
