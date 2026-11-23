"""Offline coverage for the construct-then-restart() boot contract (PR2).

Controllers construct cheaply and boot in restart(); a not-ready emulator raises
EmulatorNotReadyError from restart(). These tests pin how the two construction
sites react to that raise — without any hardware — by swapping the registry for a
fake controller whose restart() blows up.
"""

import pytest

from pyclashbot.emulators import EmulatorType
from pyclashbot.emulators.base import BaseEmulatorController, EmulatorNotReadyError
from pyclashbot.utils.logger import Logger


class _FakeNotReadyController:
    """Cheap to construct; restart() raises like a not-ready emulator."""

    constructed = 0
    aborted = False

    def __init__(self, logger, **kwargs):
        type(self).constructed += 1
        self.logger = logger

    def restart(self, *, ready=None):
        raise EmulatorNotReadyError("fake emulator is not ready")

    def abort(self):
        type(self).aborted = True


class _RecordingLogger(Logger):
    """Test double that inherits from Logger but records change_status calls.

    Lightweight to construct (Logger.__init__ only sets instance attrs + locks,
    doesn't spawn threads), and reuses all real Logger behavior without needing
    to duplicate its interface.
    """

    def __init__(self):
        super().__init__(stats=None, timed=False)
        self.statuses: list[str] = []

    def change_status(self, status) -> None:
        """Override to record calls for assertions."""
        self.statuses.append(status)
        # Still call parent to maintain contract (calls _update_log)
        super().change_status(status)


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

    _FakeNotReadyController.aborted = False
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
    assert _FakeNotReadyController.aborted


@pytest.mark.parametrize(
    "emulator_type",
    [EmulatorType.ADB, EmulatorType.EMUCTL, EmulatorType.BLUESTACKS, EmulatorType.GOOGLE_PLAY],
)
def test_setup_failure_aborts_for_any_backend(monkeypatch, emulator_type):
    """Setup failure calls the generic abort() hook, not a backend-specific path."""
    from pyclashbot.bot import worker as worker_module

    aborted: list[int] = []

    class _FakeController:
        def __init__(self, **kwargs):
            pass

        def restart(self, *, ready=None):
            raise EmulatorNotReadyError("fake emulator is not ready")

        def abort(self):
            aborted.append(1)

    monkeypatch.setattr(worker_module, "get_emulator_registry", lambda: {emulator_type: _FakeController})
    worker = worker_module.WorkerProcess.__new__(worker_module.WorkerProcess)

    assert worker._setup_emulator({"emulator": emulator_type}, _RecordingLogger()) is None
    assert aborted == [1]


def test_base_abort_is_a_noop():
    class _MinimalController(BaseEmulatorController):
        _auto_stop_on_del = False

        def __init__(self):
            pass

    _MinimalController().abort()
