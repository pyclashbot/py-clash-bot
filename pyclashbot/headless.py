"""Run py-clash-bot without a GUI."""

from __future__ import annotations

import argparse
import json
import os
import queue
import signal
import sys
import threading
from multiprocessing import Event, Queue
from typing import Any

from pyclashbot.bot.jobs import make_job_dictionary
from pyclashbot.bot.worker import WorkerProcess, stop_worker_process
from pyclashbot.emulators import EmulatorType
from pyclashbot.interface.enums import UIField
from pyclashbot.utils.logger import log_name


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    adb_server_port = os.environ.get("ADB_SERVER_PORT")
    if adb_server_port is not None and not adb_server_port.strip():
        adb_server_port = None
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
        default=int(adb_server_port) if adb_server_port is not None else None,
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
        default=log_name,
        help="Worker log file (default: %(default)s).",
    )
    return parser.parse_args(argv)


def build_jobs(args: argparse.Namespace) -> dict[str, Any]:
    values: dict[str, Any] = {
        UIField.CLASSIC_1V1_USER_TOGGLE.value: args.classic_1v1,
        UIField.RECORD_FIGHTS_TOGGLE.value: args.record_fights,
    }
    if args.jobs:
        with open(args.jobs, encoding="utf-8") as handle:
            overrides = json.load(handle)
        if not isinstance(overrides, dict):
            raise ValueError(f"{args.jobs}: expected a JSON object of job overrides")
        known = {field.value for field in UIField}
        unknown = sorted(set(overrides) - known)
        if unknown:
            raise ValueError(f"{args.jobs}: unknown job key(s): {', '.join(unknown)}")
        values.update(overrides)

    jobs = make_job_dictionary(values)
    jobs["emulator"] = EmulatorType.EMUCTL if args.emulator == "emuctl" else EmulatorType.ADB
    jobs[UIField.ADB_SERIAL.value] = args.adb_serial
    jobs["adb_path"] = args.adb_path
    jobs["adb_server_port"] = args.adb_server_port
    return jobs


def _drain_stats(stats: Queue, stop: threading.Event) -> None:
    while not stop.is_set():
        try:
            item = stats.get(timeout=0.5)
        except queue.Empty:
            continue
        except (EOFError, OSError):
            return
        print(f"[stats] {item}", flush=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.adb_serial:
        print("error: --adb-serial (or $ADB_SERIAL) is required", file=sys.stderr)
        return 2

    jobs = build_jobs(args)
    stats: Queue = Queue()
    shutdown = Event()
    worker = WorkerProcess(jobs, stats, shutdown, args.log_path, cleanup_on_exit=True)

    signal_count = 0

    def _request_shutdown(signum: int, _frame: object) -> None:
        nonlocal signal_count
        signal_count += 1
        if signal_count == 1:
            print(f"[headless] signal {signum} received, stopping...", flush=True)
            stop_worker_process(worker, shutdown)
            return
        print(f"[headless] signal {signum} received again, hard exit", flush=True)
        os._exit(130)

    stop_drain = threading.Event()
    drain = threading.Thread(target=_drain_stats, args=(stats, stop_drain), daemon=True)
    drain.start()

    print(
        f"[headless] emulator={jobs['emulator']} serial={args.adb_serial} log={args.log_path}",
        flush=True,
    )
    worker.start()
    signal.signal(signal.SIGINT, _request_shutdown)
    signal.signal(signal.SIGTERM, _request_shutdown)
    try:
        while worker.is_alive():
            worker.join(timeout=0.5)
    finally:
        stop_drain.set()
        if worker.is_alive():
            stop_worker_process(worker, shutdown)

    if signal_count:
        print("[headless] stopped", flush=True)
        return 0

    exit_code = worker.exitcode
    print(f"[headless] stopped (exit {exit_code})", flush=True)
    return 0 if exit_code in (0, None) else 1


if __name__ == "__main__":
    raise SystemExit(main())
