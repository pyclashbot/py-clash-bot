"""Offline unit tests for the emuctl-backed controller (fake facade, no hardware).

The real ``emuctl`` package is optional and lazily imported; every test here
injects a fake facade so the suite runs on a bare checkout.
"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
import time
import types
from typing import TYPE_CHECKING

import cv2
import numpy as np
import pytest

from pyclashbot.emulators import emuctl as emuctl_adapter
from pyclashbot.emulators.base import CLASH_ROYALE_PACKAGE, EmulatorNotReadyError
from pyclashbot.utils.logger import Logger

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

FRAME_WIDTH = 419
FRAME_HEIGHT = 633


class _RecordingLogger(Logger):
    """Real Logger that records the lines the adapter emits."""

    def __init__(self) -> None:
        super().__init__(stats=None, timed=False)
        self.statuses: list[str] = []
        self.lines: list[str] = []

    def change_status(self, status: str) -> None:
        self.statuses.append(status)
        super().change_status(status)

    def log(self, message: str) -> None:
        self.lines.append(message)
        super().log(message)


class _FakeProbe:
    def __init__(self, ok: bool, reason: str) -> None:
        self.ok = ok
        self.reason = reason


def _png(bgr: tuple[int, int, int] = (10, 20, 30), size: tuple[int, int] = (FRAME_WIDTH, FRAME_HEIGHT)) -> bytes:
    width, height = size
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = bgr
    ok, encoded = cv2.imencode(".png", frame)
    assert ok
    return encoded.tobytes()


class _FakeFacade:
    """Duck-typed emuctl sync facade: records calls, serves a PNG screenshot."""

    def __init__(
        self,
        *,
        png: bytes | None = None,
        reachable: bool = True,
        app_installed: bool = True,
    ) -> None:
        self._png = png if png is not None else _png()
        self._reachable = reachable
        self._app_installed = app_installed
        self.calls: list[tuple] = []
        self.close_calls = 0

    @property
    def features(self) -> frozenset[object]:
        return frozenset()

    def has_feature(self, flag: object) -> bool:
        return False

    def configure(self, spec: Mapping[str, str | int | float | None] | None = None) -> None:
        self.calls.append(("configure", spec))

    def screenshot(self) -> bytes:
        self.calls.append(("screenshot",))
        return self._png

    def click(self, x: int, y: int, *, count: int = 1, interval: float = 0.0) -> None:
        self.calls.append(("click", x, y, count, interval))

    def swipe(self, x1: int, y1: int, x2: int, y2: int, *, duration_ms: int = 300) -> None:
        self.calls.append(("swipe", x1, y1, x2, y2, duration_ms))

    def key(self, code: str | int) -> None:
        self.calls.append(("key", code))

    def text(self, value: str) -> None:
        self.calls.append(("text", value))

    def install_apk(self, apk_path: str) -> None:
        self.calls.append(("install_apk", apk_path))

    def start_app(self, package: str) -> None:
        self.calls.append(("start_app", package))

    def is_app_installed(self, package: str) -> bool:
        self.calls.append(("is_app_installed", package))
        return self._app_installed

    def is_reachable(self) -> _FakeProbe:
        return _FakeProbe(self._reachable, "ok" if self._reachable else "no-adb")

    def close(self) -> None:
        self.close_calls += 1
        self.calls.append(("close",))


def _controller(
    monkeypatch: pytest.MonkeyPatch,
    facade: _FakeFacade | None = None,
    *,
    ready_timeout: float = emuctl_adapter.DEFAULT_READY_TIMEOUT_SECONDS,
) -> tuple[emuctl_adapter.EmuctlController, _FakeFacade]:
    fake = facade if facade is not None else _FakeFacade()
    controller = emuctl_adapter.EmuctlController(_RecordingLogger(), facade=fake, ready_timeout=ready_timeout)
    return controller, fake


# ── lazy import ───────────────────────────────────────────────────────────────


def test_facade_injection_never_imports_emuctl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "emuctl", raising=False)
    _controller(monkeypatch)
    assert "emuctl" not in sys.modules


# ── screenshot ────────────────────────────────────────────────────────────────


def test_screenshot_decodes_png_to_bgr(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch, _FakeFacade(png=_png((10, 20, 30))))

    image = controller.screenshot()

    assert image.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3)
    assert image[0, 0].tolist() == [10, 20, 30]  # BGR preserved, no channel swap
    assert facade.calls.count(("screenshot",)) == 1


def test_wrong_frame_size_warns_once(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, _ = _controller(monkeypatch, _FakeFacade(png=_png(size=(100, 100))))
    logger = controller.logger
    assert isinstance(logger, _RecordingLogger)

    controller.screenshot()
    controller.screenshot()

    warnings = [line for line in logger.lines if "expected 419x633" in line]
    assert len(warnings) == 1
    assert "100x100" in warnings[0]


# ── input mapping ─────────────────────────────────────────────────────────────


def test_click_maps_clicks_and_keyword_coordinates(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch)

    controller.click(x_coord=12, y_coord=34, clicks=3, interval=0.25)
    controller.click(1, 2)

    assert ("click", 12, 34, 3, 0.25) in facade.calls
    assert ("click", 1, 2, 1, 0.0) in facade.calls  # emuctl default interval, not MEmu's 0.1


def test_swipe_key_text_and_install_map(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch)

    controller.swipe(1, 2, 3, 4)
    controller.key("KEYCODE_BACK")
    controller.text("hello")
    controller.install_apk("/tmp/clash.apk")

    assert ("swipe", 1, 2, 3, 4, 300) in facade.calls
    assert ("key", "KEYCODE_BACK") in facade.calls
    assert ("text", "hello") in facade.calls
    assert ("install_apk", "/tmp/clash.apk") in facade.calls


# ── restart ───────────────────────────────────────────────────────────────────


def test_restart_launches_clash_and_returns_on_main_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch)

    assert controller.restart(ready=lambda _emulator: True) is True
    assert ("start_app", CLASH_ROYALE_PACKAGE) in facade.calls


def test_restart_without_ready_falls_back_to_transport_liveness(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch)

    assert controller.restart() is True
    assert ("start_app", CLASH_ROYALE_PACKAGE) in facade.calls


def test_restart_timeout_raises_bot_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch, ready_timeout=0)

    with pytest.raises(EmulatorNotReadyError) as excinfo:
        controller.restart(ready=lambda _emulator: False)

    assert type(excinfo.value) is EmulatorNotReadyError  # the bot's class, not emuctl's
    assert ("start_app", CLASH_ROYALE_PACKAGE) in facade.calls


def test_start_app_missing_raises_bot_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch, _FakeFacade(app_installed=False))

    with pytest.raises(EmulatorNotReadyError):
        controller.start_app(CLASH_ROYALE_PACKAGE)

    assert ("start_app", CLASH_ROYALE_PACKAGE) not in facade.calls


# ── display geometry ─────────────────────────────────────────────────────────


def test_connect_default_passes_display_config(monkeypatch: pytest.MonkeyPatch) -> None:
    facade = _FakeFacade()
    captured: dict[str, object] = {}

    def fake_connect_sync(target: str, *, config: object = None) -> _FakeFacade:
        captured["target"] = target
        captured["config"] = config
        return facade

    fake_module = types.SimpleNamespace(
        AdbConfig=lambda **kwargs: ("adb", kwargs),
        DisplayConfig=lambda **kwargs: ("display", kwargs),
        EmuctlConfig=lambda **kwargs: ("config", kwargs),
        connect_sync=fake_connect_sync,
    )
    monkeypatch.setitem(sys.modules, "emuctl", fake_module)

    connected = emuctl_adapter._connect_default("adb:127.0.0.1:5555")

    assert connected is facade
    assert captured["config"] == (
        "config",
        {
            "adb": ("adb", {"path": None, "port": 5037}),
            "display": ("display", {"width": 419, "height": 633, "dpi": 160}),
        },
    )
    assert ("configure", None) in facade.calls


def test_stop_closes_facade_without_adb(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch)

    def _fail(*args: object, **kwargs: object) -> object:
        raise AssertionError("stop must not shell out to adb")

    monkeypatch.setattr(subprocess, "run", _fail)
    controller.stop()
    controller.stop()

    assert facade.close_calls == 1
    assert not hasattr(emuctl_adapter, "_WmGeometry")
    assert not hasattr(emuctl_adapter, "_run_adb")


def test_abort_delegates_to_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    controller, facade = _controller(monkeypatch)

    controller.abort()

    assert facade.close_calls == 1


# ── health / registration ─────────────────────────────────────────────────────


def test_is_reachable_maps_probe_result(monkeypatch: pytest.MonkeyPatch) -> None:
    reachable, _ = _controller(monkeypatch, _FakeFacade(reachable=True))
    unreachable, _ = _controller(monkeypatch, _FakeFacade(reachable=False))

    assert reachable.is_reachable() == (True, "")
    assert unreachable.is_reachable() == (False, "no-adb")


def test_registration_contains_emuctl_last_but_hides_it_from_picker(monkeypatch: pytest.MonkeyPatch) -> None:
    from pyclashbot.emulators import EmulatorType, get_available_emulators, get_emulator_registry

    registry = get_emulator_registry()
    assert registry[EmulatorType.EMUCTL] is emuctl_adapter.EmuctlController
    assert list(registry)[-1] is EmulatorType.EMUCTL  # existing default order preserved
    assert emuctl_adapter.EmuctlController.is_supported_on_current_platform() is False

    # The picker stays hidden unconditionally: the old env var must have no effect.
    for env_value in (None, "0", "1"):
        if env_value is None:
            monkeypatch.delenv("PYCLASHBOT_EMUCTL", raising=False)
        else:
            monkeypatch.setenv("PYCLASHBOT_EMUCTL", env_value)
        assert EmulatorType.EMUCTL not in get_available_emulators()


_ADB_SHIM = """#!{python}
import base64
import sys

PNG = base64.b64decode("{png}")
LOG = {log!r}


def device_argv(argv):
    index = 0
    while index < len(argv) and argv[index] in ("-H", "-P", "-s"):
        index += 2
    return argv[index:]


args = device_argv(sys.argv[1:])
with open(LOG, "a", encoding="utf-8") as handle:
    handle.write(" ".join(args) + "\\n")

if args[:1] == ["connect"]:
    print("connected")
elif args == ["get-state"]:
    print("device")
elif args == ["shell", "wm", "size"]:
    print("Physical size: 1080x2400")
elif args == ["shell", "wm", "density"]:
    print("Physical density: 420")
elif args[:3] == ["shell", "wm", "size"]:
    pass
elif args[:3] == ["shell", "wm", "density"]:
    pass
elif args == ["exec-out", "screencap", "-p"]:
    sys.stdout.buffer.write(PNG)
elif args[:3] == ["shell", "pm", "list"]:
    print("package:" + args[4])
elif args[:3] == ["shell", "am", "force-stop"]:
    pass
elif args[:2] in (["shell", "pidof"], ["shell", "monkey"]):
    print("1234" if args[1] == "pidof" else "Events injected: 1")
else:
    sys.stderr.write("unexpected adb args: " + " ".join(args) + "\\n")
    raise SystemExit(3)
"""


@pytest.mark.skipif(os.name == "nt", reason="the fake adb shim is a POSIX executable")
def test_real_facade_against_fake_adb_shim(tmp_path: Path) -> None:
    pytest.importorskip("emuctl")
    shim = tmp_path / "fake-adb"
    adb_log = tmp_path / "adb.log"
    shim.write_text(
        _ADB_SHIM.format(
            python=sys.executable,
            png=base64.b64encode(_png((10, 20, 30))).decode("ascii"),
            log=str(adb_log),
        ),
        encoding="utf-8",
    )
    shim.chmod(0o755)

    started = time.monotonic()
    controller = emuctl_adapter.EmuctlController(
        _RecordingLogger(),
        device_serial="127.0.0.1:5555",
        adb_path=str(shim),
        ready_timeout=5.0,
    )

    try:
        image = controller.screenshot()
        assert image.shape == (FRAME_HEIGHT, FRAME_WIDTH, 3)
        assert image[0, 0].tolist() == [10, 20, 30]
        assert controller.restart(ready=lambda _emulator: True) is True

        lines = adb_log.read_text(encoding="utf-8").splitlines()
        force_stop = lines.index(f"shell am force-stop {CLASH_ROYALE_PACKAGE}")
        launch = next(index for index, line in enumerate(lines) if line.startswith("shell monkey -p "))
        assert force_stop < launch
        assert time.monotonic() - started < 5.0

        before_stop = len(lines)
        controller.stop()
        assert len(adb_log.read_text(encoding="utf-8").splitlines()) == before_stop
    finally:
        controller.stop()
