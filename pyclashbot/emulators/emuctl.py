"""emuctl-backed emulator controller.

Drives an ``adb:<serial>`` target through the emuctl sync facade instead of the
built-in ADB layer.

Install the optional headless extra (which carries the emuctl dependency)::

    pip install -e ".[headless]"
    uv sync --extra headless

emuctl is imported lazily, so the GUI and the normal test suite run without it;
the adapter tests inject a fake facade. emuctl is a pre-release git dependency
(not on PyPI), so installing the headless extra currently requires access to its
source repository.

The adapter does not call emuctl's BOOT-gated ``restart()``. App restart here is
``start_app`` plus a bounded caller-supplied readiness predicate (falling back to
transport liveness).
"""

from __future__ import annotations

import re
import subprocess
import time
from typing import TYPE_CHECKING, Protocol

import cv2
import numpy as np

from pyclashbot.emulators.adb_base import validate_device_serial
from pyclashbot.emulators.base import (
    CLASH_ROYALE_PACKAGE,
    BaseEmulatorController,
    EmulatorNotReadyError,
    ReadyCheck,
)
from pyclashbot.utils.platform import Platform

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from pyclashbot.utils.logger import Logger

DEFAULT_ADB_SERIAL = "127.0.0.1:5555"
DEFAULT_READY_TIMEOUT_SECONDS = 240.0
REQUIRED_WIDTH = 419
REQUIRED_HEIGHT = 633
REQUIRED_DENSITY = 160
_REQUIRED_SIZE = f"{REQUIRED_WIDTH}x{REQUIRED_HEIGHT}"


class _Probe(Protocol):
    """Structural view of emuctl's ``ProbeResult`` (never truth-test the NamedTuple)."""

    @property
    def ok(self) -> bool: ...

    @property
    def reason(self) -> str: ...


class _Facade(Protocol):
    """The subset of emuctl's sync ``EmulatorController`` this adapter drives."""

    @property
    def features(self) -> Iterable[object]: ...

    def has_feature(self, flag: object) -> bool: ...

    def configure(self, spec: Mapping[str, object] | None = None) -> None: ...

    def screenshot(self) -> bytes: ...

    def click(self, x: int, y: int, *, count: int = 1, interval: float = 0.0) -> None: ...

    def swipe(self, x1: int, y1: int, x2: int, y2: int, *, duration_ms: int = 300) -> None: ...

    def key(self, code: str | int) -> None: ...

    def text(self, value: str) -> None: ...

    def install_apk(self, apk_path: str) -> None: ...

    def start_app(self, package: str) -> None: ...

    def is_app_installed(self, package: str) -> bool: ...

    def is_reachable(self) -> _Probe: ...

    def close(self) -> None: ...


def _connect_default(target: str) -> tuple[_Facade, bool]:
    """Connect through emuctl's sync facade, asking for display geometry.

    Returns ``(facade, display_configured)``. ``adb`` does not declare
    ``CONFIGURE``, so the expected path is a typed ``FeatureNotSupportedError``
    from ``connect_sync(config=...)``; we reconnect plain and let the quarantined
    ``wm`` fallback install the frame. Any other typed emuctl error propagates to
    the worker's existing handler.
    """
    from emuctl import (  # optional dependency, lazy by design
        DisplayConfig,
        EmuctlConfig,
        FeatureNotSupportedError,
        connect_sync,
    )

    config = EmuctlConfig(display=DisplayConfig(width=REQUIRED_WIDTH, height=REQUIRED_HEIGHT, dpi=REQUIRED_DENSITY))
    try:
        facade = connect_sync(target, config=config)
    except FeatureNotSupportedError:
        return connect_sync(target), False
    facade.configure()  # apply the non-None display section bound at connect
    return facade, True


def _declares_configure(facade: _Facade) -> bool:
    return any(getattr(feature, "value", feature) == "configure" for feature in facade.features)


def _run_adb(adb_path: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run one raw ADB command (list argv, never a shell) for the wm fallback."""
    return subprocess.run([adb_path, *args], capture_output=True, text=True, check=False)


class _WmGeometry:
    """TODO(CONFIGURE): quarantined raw-ADB size/density fallback.

    emuctl's adb backend does not declare CONFIGURE yet (amendment pending), so
    until it does we install the bot's fixed frame with two ``wm`` commands and
    restore the device's originals on ``stop()``. Delete this class once the
    amendment lands; nothing else in the adapter should shell out to ADB.

    Verification: the achieved size is checked from the first screenshot with
    emuctl's ``png_dimensions`` (never by parsing ``wm size`` output). Density is
    not observable through emuctl's public surface — verifying it stays blocked
    on the headless POC (compare a reference frame).
    """

    def __init__(self, adb_path: str, serial: str) -> None:
        self._adb_path = adb_path
        self._serial = serial
        self._original_size: str | None = None
        self._original_density: str | None = None

    def _adb(self, *args: str) -> subprocess.CompletedProcess[str]:
        return _run_adb(self._adb_path, "-s", self._serial, *args)

    def _current_size(self) -> str | None:
        result = self._adb("shell", "wm", "size")
        matches = re.findall(r"(?:Physical|Override) size: (\d+x\d+)", result.stdout or "")
        return matches[-1] if matches else None

    def _current_density(self) -> str | None:
        result = self._adb("shell", "wm", "density")
        match = re.search(r"(?:Physical|Override) density: (\d+)", result.stdout or "")
        return match.group(1) if match else None

    def force_frame(self) -> None:
        size = self._current_size()
        if size != _REQUIRED_SIZE:
            self._original_size = size
            self._adb("shell", "wm", "size", _REQUIRED_SIZE)

        density = self._current_density()
        if density != str(REQUIRED_DENSITY):
            self._original_density = density
            self._adb("shell", "wm", "density", str(REQUIRED_DENSITY))

    def restore(self) -> None:
        if self._original_size is not None:
            self._adb("shell", "wm", "size", self._original_size)
            self._original_size = None
        if self._original_density is not None:
            self._adb("shell", "wm", "density", self._original_density)
            self._original_density = None


class EmuctlController(BaseEmulatorController):
    """Drive an Android target through emuctl's sync facade.

    Subclasses ``BaseEmulatorController`` directly: emuctl owns the ADB transport,
    so none of ``AdbBasedController``'s mechanics apply. Construction is cheap
    discovery/connect plus the display-geometry gate; ``restart()`` is the boot
    primitive and leaves Clash on a detectable main menu.
    """

    supported_platforms = [Platform.WINDOWS, Platform.MACOS, Platform.LINUX]

    @classmethod
    def is_supported_on_current_platform(cls) -> bool:
        # TODO(emuctl): hide the picker until the real UIField round-trip exists.
        # get_all_values() does not map a fifth combobox value yet, so listing it
        # would silently fall back to MEmu (Windows) or refuse (Linux). Construct
        # this controller programmatically until interface/enums.py + config.py +
        # ui.py are wired together.
        return False

    def __init__(
        self,
        logger: Logger,
        device_serial: str | None = None,
        *,
        facade: _Facade | None = None,
        adb_path: str = "adb",
        ready_timeout: float = DEFAULT_READY_TIMEOUT_SECONDS,
    ) -> None:
        self.logger = logger
        self._auto_stop_on_del = False
        self._ready_timeout = ready_timeout
        self._stopped = False
        self._frame_size_checked = False

        self.target = self._resolve_target(device_serial)
        self._connected_via_emuctl = facade is None

        self.logger.change_status(f"Connecting to emuctl target {self.target}...")
        if facade is None:
            self._facade, display_configured = _connect_default(self.target)
        else:
            self._facade = facade
            display_configured = False
        self.logger.log(f"Connected to emuctl target {self.target}.")

        # 419x633 is the only supported frame; there is no consumer-side scaling.
        serial = self.target.split(":", 1)[1]
        self._wm = _WmGeometry(adb_path, serial)
        if display_configured:
            self.logger.log("Display geometry configured through emuctl.")
        elif _declares_configure(self._facade):
            self._facade.configure()
            self.logger.log("Display geometry configured through emuctl.")
        else:
            self._wm.force_frame()
            self.logger.log(f"Display forced to {_REQUIRED_SIZE} @ {REQUIRED_DENSITY}dpi via adb wm.")

    @staticmethod
    def _resolve_target(device_serial: str | None) -> str:
        serial = (device_serial or DEFAULT_ADB_SERIAL).strip()
        if not validate_device_serial(serial):
            raise ValueError(f"Invalid device serial format: {serial!r}")
        return f"adb:{serial}"

    # ── lifecycle ──

    def create(self) -> None:
        """emuctl owns provisioning; not wired in this pass."""
        self.logger.log("Create is not supported by the emuctl adb backend.")

    def configure(self) -> None:
        """Display geometry is handled in construction; backend config is emuctl's."""
        self.logger.log("Configure is not supported by the emuctl adb backend.")

    def start(self) -> None:
        """The container/emulator lifecycle stays with docker compose."""
        self.logger.log("Start is not supported by the emuctl adb backend; manage the device externally.")

    def restart(self, *, ready: ReadyCheck | None = None) -> bool:
        """Launch Clash and wait for readiness (never emuctl's BOOT-gated restart).

        One attempt: ``start_app`` plus a bounded predicate. The bot passes its
        main-menu detector via ``ready``; without one, fall back to a cheap
        transport-liveness probe so the adapter has no bot-state dependency.
        Raises the *bot's* ``EmulatorNotReadyError`` on timeout, never returns
        False.

        Gap to document for the POC: emuctl's adb ``start_app`` runs ``monkey``
        directly and does not force-stop the package first (verified against the
        emuctl sync-facade build). We do not reach for vendor commands; add the
        force-stop there or accept relaunch semantics.
        """
        start = time.monotonic()
        self.logger.change_status("Launching Clash Royale via emuctl...")
        self.start_app(CLASH_ROYALE_PACKAGE)

        is_ready = ready if ready is not None else self._transport_ready
        deadline = start + self._ready_timeout
        while time.monotonic() < deadline:
            if is_ready(self):
                self.logger.change_status("Clash Royale is ready.")
                self.logger.log(f"emuctl restart completed in {time.monotonic() - start:.1f}s")
                return True
            time.sleep(2)

        raise EmulatorNotReadyError("emuctl restart() timed out waiting for the Clash Royale main menu")

    def _transport_ready(self, _emulator: BaseEmulatorController) -> bool:
        """Cheap default readiness: the adb transport answers a probe."""
        return self.is_reachable()[0]

    def abort(self) -> None:
        """Restore wm geometry and release the facade after a failed setup."""
        self.stop()

    def stop(self) -> None:
        """Restore any wm overrides, then release the facade (idempotent)."""
        if self._stopped:
            return
        self._stopped = True
        self._wm.restore()
        self._facade.close()

    # ── screen ──

    def screenshot(self) -> np.ndarray:
        """PNG bytes -> one cv2 decode -> BGR ndarray (no re-encode, no scaling)."""
        png = self._facade.screenshot()
        if not png:
            raise ValueError("emuctl screenshot() returned no PNG bytes")

        image = cv2.imdecode(np.frombuffer(png, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to decode emuctl screenshot PNG")

        self._warn_if_unexpected_frame_size(png, image)
        return image

    def _warn_if_unexpected_frame_size(self, png: bytes, image: np.ndarray) -> None:
        """Warn once about a non-419x633 frame; never fail (the POC needs the numbers)."""
        if self._frame_size_checked:
            return
        self._frame_size_checked = True

        width, height = image.shape[1], image.shape[0]
        if self._connected_via_emuctl:
            from emuctl import png_dimensions  # optional dependency, same lazy seam

            width, height = png_dimensions(png)
        if (width, height) != (REQUIRED_WIDTH, REQUIRED_HEIGHT):
            self.logger.log(
                f"emuctl screenshot is {width}x{height}, expected {REQUIRED_WIDTH}x{REQUIRED_HEIGHT}; "
                "coordinates are likely wrong."
            )

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.0) -> None:
        """Absolute device pixels; ``clicks``/``interval`` map to emuctl's ``count``/``interval``."""
        self._facade.click(x_coord, y_coord, count=max(1, clicks), interval=interval)

    def swipe(self, x_coord1: int, y_coord1: int, x_coord2: int, y_coord2: int) -> None:
        self._facade.swipe(x_coord1, y_coord1, x_coord2, y_coord2)

    def key(self, code: str | int) -> None:
        self._facade.key(code)

    def text(self, value: str) -> None:
        self._facade.text(value)

    # ── apps / health ──

    def install_apk(self, apk_path: str) -> None:
        self._facade.install_apk(apk_path)

    def start_app(self, package_name: str) -> None:
        if not self._facade.is_app_installed(package_name):
            raise EmulatorNotReadyError(f"{package_name} is not installed on the emulator")
        self._facade.start_app(package_name)

    def is_app_installed(self, package: str) -> bool:
        return self._facade.is_app_installed(package)

    def is_reachable(self) -> tuple[bool, str]:
        probe = self._facade.is_reachable()
        if probe.ok:
            return True, ""
        return False, probe.reason
