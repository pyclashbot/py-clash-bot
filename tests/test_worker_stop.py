"""Tests for OS-level worker stop orchestration (``stop_worker_process``).

The orchestration tests use lightweight fakes to assert the signal → terminate →
hard-kill escalation and its ordering. The final test spawns a real process running a
plain ``time.sleep`` to prove the kernel interrupts blocking calls on terminate — the
reason plain ``time.sleep`` is safe to use for waits throughout the bot.
"""

import multiprocessing as mp
import time

from pyclashbot.bot.worker import stop_worker_process


class _FakeEvent:
    """Records ``set()`` into a shared ordered log."""

    def __init__(self, log: list[str]) -> None:
        self._log = log
        self.is_set_flag = False

    def set(self) -> None:
        self._log.append("set")
        self.is_set_flag = True


class _FakeProcess:
    """Fake process whose ``is_alive()`` follows a scripted sequence.

    ``terminate``/``join``/``kill`` are recorded into the shared log so call order
    across the event and process can be asserted.
    """

    def __init__(self, log: list[str], alive_sequence: list[bool]) -> None:
        self._log = log
        self._alive = list(alive_sequence)

    def is_alive(self) -> bool:
        return self._alive.pop(0) if self._alive else False

    def terminate(self) -> None:
        self._log.append("terminate")

    def join(self, timeout: float | None = None) -> None:
        self._log.append("join")

    def kill(self) -> None:
        self._log.append("kill")


def test_terminates_alive_process_and_skips_kill() -> None:
    log: list[str] = []
    event = _FakeEvent(log)
    # alive at the guard, dead after terminate+join
    process = _FakeProcess(log, [True, False])

    stop_worker_process(process, event)

    assert event.is_set_flag
    assert "terminate" in log
    assert "kill" not in log
    assert log.index("set") < log.index("terminate") < log.index("join")


def test_hard_kills_when_terminate_does_not_exit() -> None:
    log: list[str] = []
    event = _FakeEvent(log)
    # still alive at the guard and after terminate+join → must escalate to kill
    process = _FakeProcess(log, [True, True])

    stop_worker_process(process, event)

    assert "kill" in log
    assert log.index("set") < log.index("terminate") < log.index("kill")


def test_skips_terminate_when_already_dead() -> None:
    log: list[str] = []
    event = _FakeEvent(log)
    process = _FakeProcess(log, [False])

    stop_worker_process(process, event)

    assert event.is_set_flag  # event is still signalled
    assert "terminate" not in log


def test_handles_none_process() -> None:
    log: list[str] = []
    event = _FakeEvent(log)

    stop_worker_process(None, event)  # must not raise

    assert event.is_set_flag


def test_works_without_an_event() -> None:
    log: list[str] = []
    process = _FakeProcess(log, [True, False])

    stop_worker_process(process)  # shutdown_event omitted

    assert "terminate" in log


def _sleeper() -> None:
    """Spawn target: block in a plain sleep so terminate has to interrupt it."""
    time.sleep(30)  # proving plain sleep is interruptible by terminate


def test_terminate_interrupts_plain_sleep() -> None:
    """A real process blocked in plain ``time.sleep`` dies promptly on terminate."""
    ctx = mp.get_context("spawn")  # match production start method
    process = ctx.Process(target=_sleeper)
    process.start()
    try:
        assert process.is_alive()
        start = time.monotonic()
        stop_worker_process(process, graceful_timeout=0.5)
        elapsed = time.monotonic() - start

        assert not process.is_alive()
        assert elapsed < 0.5, f"termination took {elapsed:.3f}s"
    finally:
        if process.is_alive():
            process.kill()
            process.join(timeout=1)
