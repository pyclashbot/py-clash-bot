"""Deterministic identity and networking for supervisor guests.

Each guest owns a disjoint slice of the host's ports plus a stable Android-side
identity. The numbers are derived from a single integer index so two callers
that ask for the same index always get the same guest, and any two guests are
collision-free before a container or emulator is started.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import asdict, dataclass
from typing import Any, Final

BASE_SERVER_PORT: Final[int] = 5560
BASE_DEVICE_PORT: Final[int] = 5570
BASE_GUEST_IP: Final[ipaddress.IPv4Address] = ipaddress.IPv4Address("10.0.2.15")
MAC_PREFIX: Final[str] = "02:00:00:00:00"
MAX_GUEST_INDEX: Final[int] = 239  # keeps 10.0.2.15+i inside 10.0.2.0/24

_MAC_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$")


class GuestSpecError(ValueError):
    """A guest spec is malformed or outside the supported allocation range."""


def _require_int(name: str, value: object, *, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GuestSpecError(f"{name} must be an int, got {type(value).__name__}")
    if value < minimum or (maximum is not None and value > maximum):
        bound = f"{minimum}..{maximum}" if maximum is not None else f">= {minimum}"
        raise GuestSpecError(f"{name} must be {bound}, got {value}")
    return value


@dataclass(frozen=True, slots=True)
class GuestSpec:
    """One guest's stable identity; index is the only input needed to derive it."""

    index: int
    server_port: int
    device_port: int
    ip: str
    mac: str
    serial: str

    def __post_init__(self) -> None:
        _require_int("index", self.index, minimum=0, maximum=MAX_GUEST_INDEX)
        _require_int("server_port", self.server_port, minimum=1, maximum=65535)
        _require_int("device_port", self.device_port, minimum=1, maximum=65535)
        if self.server_port == self.device_port:
            raise GuestSpecError("server_port and device_port must differ")
        try:
            parsed = ipaddress.IPv4Address(self.ip)
        except (ipaddress.AddressValueError, ValueError) as exc:
            raise GuestSpecError(f"ip must be a dotted IPv4 address, got {self.ip!r}") from exc
        if parsed.is_unspecified or parsed.is_multicast:
            raise GuestSpecError(f"ip must be a usable unicast address, got {self.ip!r}")
        if not isinstance(self.mac, str) or _MAC_RE.fullmatch(self.mac) is None:
            raise GuestSpecError(f"mac must be six colon-separated hex octets, got {self.mac!r}")
        if not isinstance(self.serial, str) or not self.serial.strip() or any(c.isspace() for c in self.serial):
            raise GuestSpecError("serial must be a non-empty string with no whitespace")

    @classmethod
    def for_index(
        cls,
        index: int,
        *,
        server_port: int | None = None,
        device_port: int | None = None,
        ip: str | None = None,
        mac: str | None = None,
        serial: str | None = None,
    ) -> GuestSpec:
        """Derive the guest for ``index``; every component can be pinned explicitly."""
        checked = _require_int("index", index, minimum=0, maximum=MAX_GUEST_INDEX)
        derived_device = BASE_DEVICE_PORT + checked
        return cls(
            index=checked,
            server_port=BASE_SERVER_PORT + checked if server_port is None else server_port,
            device_port=derived_device if device_port is None else device_port,
            ip=str(BASE_GUEST_IP + checked) if ip is None else ip,
            mac=f"{MAC_PREFIX}:{checked + 1:02x}" if mac is None else mac,
            serial=f"127.0.0.1:{derived_device if device_port is None else device_port}" if serial is None else serial,
        )

    @property
    def container_name(self) -> str:
        return f"pyclashbot-guest-{self.index}"

    @property
    def avd_name(self) -> str:
        return f"pyclashbot-guest-{self.index}"

    @property
    def label(self) -> str:
        return f"pyclashbot.supervisor.guest={self.serial}"

    def env(self) -> dict[str, str]:
        """Per-child environment: explicit serial and ports, never discovery order."""
        return {
            "ADB_SERIAL": self.serial,
            "ADB_SERVER_PORT": str(self.server_port),
            "ADB_MDNS": "0",
            "PYCLASHBOT_GUEST_INDEX": str(self.index),
            "PYCLASHBOT_GUEST_IP": self.ip,
            "PYCLASHBOT_GUEST_MAC": self.mac,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> GuestSpec:
        return cls(
            index=payload["index"],
            server_port=payload["server_port"],
            device_port=payload["device_port"],
            ip=payload["ip"],
            mac=payload["mac"],
            serial=payload["serial"],
        )
