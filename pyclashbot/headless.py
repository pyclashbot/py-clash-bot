"""Run py-clash-bot without a GUI.

Usage::

    python -m pyclashbot.headless --adb-serial 127.0.0.1:5555 --adb-path /opt/platform-tools/adb

This exists so the bot can run on a headless Linux host: the GUI entry point imports
``tkinter``/``ttkbootstrap`` and needs an X display, while the bot core does not. The
worker loop, logging and state machine are reused unchanged — only job construction and
the emulator selection are supplied here.

The emulator defaults to the ``emuctl`` backend, which drives any ``adb:<serial>``
target through the emuctl library. ``--emulator adb`` selects this repo's built-in ADB
controller instead.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import signal
import sys
import tempfile
import threading
from multiprocessing import Event, Queue
from typing import Any

from pyclashbot.bot.worker import WorkerProcess
from pyclashbot.emulators import EmulatorType
from pyclashbot.interface.enums import UIField


def _env_int(name: str) -> int | None:
    """Read an optional integer environment variable."""
    value = os.environ.get(name)
    if value is None or not value.strip():
        return None
    return int(value)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="pyclashbot.headless",
        description="Run py-clash-bot without a GUI (headless Linux).",
    )
    parser.add_argument(
        "--emulator",
        choices=("emuctl", "adb"),
        default=os.environ.get("PYCLASHBOT_HEADLESS_EMULATOR", "emuctl"),
        help="Backend to drive the device with (default: emuctl).",
    )
    parser.add_argument(
        "--adb-serial",
        default=os.environ.get("ADB_SERIAL"),
        help="ADB serial, e.g. 127.0.0.1:5555 (default: $ADB_SERIAL).",
    )
    parser.add_argument(
        "--adb-path",
        default=os.environ.get("ADB_PATH"),
        help="Path to the adb executable (default: $ADB_PATH, else emuctl's discovery).",
    )
    parser.add_argument(
        "--adb-server-port",
        type=int,
        default=_env_int("ADB_SERVER_PORT"),
        help="ADB server port for --adb-path (default: $ADB_SERVER_PORT, else adb's 5037).",
    )
    parser.add_argument(
        "--jobs",
        metavar="FILE",
        help="JSON file of job overrides keyed by UIField values.",
    )
    parser.add_argument(
        "--classic-1v1",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Play classic 1v1 battles (default: on).",
    )
    parser.add_argument(
        "--record-fights",
        action="store_true",
        default=False,
        help="Record fights to the configured folder.",
    )
    parser.add_argument(
        "--log-path",
        default=os.path.join(tempfile.gettempdir(), "pyclashbot-headless.log"),
        help="Worker log file (default: %(default)s).",
    )
    return parser.parse_args(argv)


def build_jobs(args: argparse.Namespace) -> dict[str, Any]:
    """Build the job dictionary the worker loop expects."""
    emulator = EmulatorType.EMUCTL if args.emulator == "emuctl" else EmulatorType.ADB
    jobs: dict[str, Any] = {
        "emulator": emulator,
        UIField.ADB_SERIAL.value: args.adb_serial,
        "adb_path": args.adb_path,
        "adb_server_port": args.adb_server_port,
        UIField.CLASSIC_1V1_USER_TOGGLE.value: args.classic_1v1,
        UIField.RECORD_FIGHTS_TOGGLE.value: args.record_fights,
    }
    if args.jobs:
        with open(args.jobs, encoding="utf-8") as handle:
            overrides = json.load(handle)
        if not isinstance(overrides, dict):
            raise ValueError(f"{args.jobs}: expected a JSON object of job overrides")
        jobs.update(overrides)
    return jobs


def _drain_stats(stats: Queue, stop: threading.Event) -> None:
    """Print worker stats as they arrive so the run is observable without a GUI."""
    while not stop.is_set():
        try:
            item = stats.get(timeout=0.5)
        except queue.Empty:
            continue
        except (EOFError, OSError):
            return
        print(f"[stats] {item}", flush=True)


def main(argv: list[str] | None = None) -> int:
    """Run the bot loop in this process."""
    args = parse_args(argv)
    if not args.adb_serial:
        print("error: --adb-serial (or $ADB_SERIAL) is required", file=sys.stderr)
        return 2

    jobs = build_jobs(args)
    stats: Queue = Queue()
    shutdown = Event()
    worker = WorkerProcess(jobs, stats, shutdown, args.log_path)

    def _request_shutdown(signum: int, _frame: object) -> None:
        print(f"[headless] signal {signum} received, stopping...", flush=True)
        shutdown.set()

    signal.signal(signal.SIGINT, _request_shutdown)
    signal.signal(signal.SIGTERM, _request_shutdown)

    stop_drain = threading.Event()
    drain = threading.Thread(target=_drain_stats, args=(stats, stop_drain), daemon=True)
    drain.start()

    print(
        f"[headless] emulator={jobs['emulator']} serial={args.adb_serial} log={args.log_path}",
        flush=True,
    )
    try:
        worker.run()
    finally:
        shutdown.set()
        stop_drain.set()
    print("[headless] stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
