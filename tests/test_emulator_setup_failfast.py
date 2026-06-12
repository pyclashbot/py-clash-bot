"""Offline coverage for the construct-then-restart() boot contract (PR2).

Controllers construct cheaply and boot in restart(); a not-ready emulator raises
EmulatorNotReadyError from restart(). These tests pin how the two construction
sites react to that raise — without any hardware — by swapping the registry for a
fake controller whose restart() blows up.
"""

import pytest

from pyclashbot.emulators import EmulatorType
from pyclashbot.emulators.base import EmulatorNotReadyError


class _FakeNotReadyController:
    """Cheap to construct; restart() raises like a not-ready emulator."""

    constructed = 0

    def __init__(self, logger, **kwargs):
        type(self).constructed += 1
        self.logger = logger

    def restart(self):
        raise EmulatorNotReadyError("fake emulator is not ready")


class _RecordingLogger:
    def __init__(self):
        self.statuses: list[str] = []

    def change_status(self, status):
        self.statuses.append(status)

    def log(self, *args, **kwargs):
        pass


def test_attach_emulator_reraises_when_restart_not_ready(monkeypatch):
    import pyclashbot.emulators as emulators_pkg

    monkeypatch.setattr(
        emulators_pkg,
        "get_emulator_registry",
        lambda: {EmulatorType.ADB: _FakeNotReadyController},
    )

    from tests._emulator_support import attach_emulator

    with pytest.raises(EmulatorNotReadyError):
        attach_emulator("adb", _RecordingLogger())


def test_setup_emulator_returns_none_and_reports_when_restart_not_ready(monkeypatch):
    from pyclashbot.bot import worker as worker_module

    monkeypatch.setattr(
        worker_module,
        "get_emulator_registry",
        lambda: {EmulatorType.ADB: _FakeNotReadyController},
    )

    # _setup_emulator doesn't touch instance state; skip Process.__init__.
    worker = worker_module.WorkerProcess.__new__(worker_module.WorkerProcess)
    logger = _RecordingLogger()

    result = worker._setup_emulator({"emulator": EmulatorType.ADB}, logger)

    assert result is None
    assert logger.statuses, "expected a user-facing status explaining the abort"
    assert any("not ready" in status.lower() for status in logger.statuses)
