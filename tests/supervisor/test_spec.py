"""Deterministic guest identity derivation."""

from __future__ import annotations

import pytest

from pyclashbot.supervisor.spec import (
    BASE_DEVICE_PORT,
    BASE_GUEST_IP,
    BASE_SERVER_PORT,
    GuestSpec,
    GuestSpecError,
)


def test_defaults_are_derived_from_the_index() -> None:
    spec = GuestSpec.for_index(2)

    assert spec.index == 2
    assert spec.server_port == BASE_SERVER_PORT + 2
    assert spec.device_port == BASE_DEVICE_PORT + 2
    assert spec.ip == str(BASE_GUEST_IP + 2)
    assert spec.mac == "02:00:00:00:00:03"
    assert spec.serial == f"127.0.0.1:{BASE_DEVICE_PORT + 2}"


def test_derivation_is_stable() -> None:
    assert GuestSpec.for_index(7) == GuestSpec.for_index(7)
    assert GuestSpec.for_index(0) != GuestSpec.for_index(1)
    assert GuestSpec.for_index(0).serial != GuestSpec.for_index(1).serial


def test_every_component_can_be_pinned() -> None:
    spec = GuestSpec.for_index(
        0,
        server_port=6001,
        device_port=6002,
        ip="10.9.0.5",
        mac="02:aa:bb:cc:dd:ee",
        serial="127.0.0.1:6002",
    )
    assert (spec.server_port, spec.device_port) == (6001, 6002)
    assert spec.ip == "10.9.0.5"
    assert spec.mac == "02:aa:bb:cc:dd:ee"


def test_names_and_env_are_explicit() -> None:
    spec = GuestSpec.for_index(1)
    assert spec.container_name == "pyclashbot-guest-1"
    assert spec.avd_name == "pyclashbot-guest-1"
    assert spec.label == f"pyclashbot.supervisor.guest={spec.serial}"
    env = spec.env()
    assert env["ADB_SERIAL"] == spec.serial
    assert env["ADB_SERVER_PORT"] == str(spec.server_port)
    assert env["ADB_MDNS"] == "0"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"index": -1}, "index"),
        ({"index": 240}, "index"),
        ({"index": True}, "index"),
        ({"server_port": 0}, "server_port"),
        ({"server_port": 70000}, "server_port"),
        ({"ip": "not-an-ip"}, "ip"),
        ({"ip": "0.0.0.0"}, "ip"),
        ({"mac": "02:00:00:00:00"}, "mac"),
        ({"serial": ""}, "serial"),
        ({"serial": "127.0.0.1:5554 bad"}, "serial"),
    ],
)
def test_invalid_components_are_rejected(kwargs: dict[str, object], message: str) -> None:
    index = kwargs.pop("index", 0)
    with pytest.raises(GuestSpecError, match=message):
        GuestSpec.for_index(index, **kwargs)  # ty: ignore[invalid-argument-type]


def test_server_and_device_ports_must_differ() -> None:
    with pytest.raises(GuestSpecError, match="must differ"):
        GuestSpec.for_index(0, server_port=6000, device_port=6000)


def test_dict_round_trip() -> None:
    spec = GuestSpec.for_index(3)
    assert GuestSpec.from_dict(spec.to_dict()) == spec
