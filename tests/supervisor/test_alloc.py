"""Deterministic allocation and collision admission."""

from __future__ import annotations

import pytest

from pyclashbot.supervisor.alloc import (
    AllocationConflictError,
    GuestAllocator,
    assert_disjoint,
    validate_plan,
)
from pyclashbot.supervisor.spec import GuestSpec


def test_allocate_range_is_deterministic_and_disjoint() -> None:
    specs = GuestAllocator().allocate_range(0, 3)

    assert [spec.index for spec in specs] == [0, 1, 2]
    assert len({spec.server_port for spec in specs}) == 3
    assert len({spec.device_port for spec in specs}) == 3
    assert len({spec.ip for spec in specs}) == 3
    assert len({spec.mac for spec in specs}) == 3
    assert len({spec.serial for spec in specs}) == 3


def test_duplicate_index_is_rejected() -> None:
    allocator = GuestAllocator()
    allocator.allocate(0)
    with pytest.raises(AllocationConflictError) as caught:
        allocator.allocate(0)
    assert caught.value.field_name == "index"


@pytest.mark.parametrize(
    ("field_name", "override"),
    [
        ("server_port", {"server_port": 5560}),
        ("device_port", {"device_port": 5570}),
        ("ip", {"ip": "10.0.2.15"}),
        ("mac", {"mac": "02:00:00:00:00:01"}),
        ("serial", {"serial": "127.0.0.1:5570"}),
    ],
)
def test_duplicate_identity_field_is_rejected(field_name: str, override: dict[str, object]) -> None:
    allocator = GuestAllocator()
    allocator.allocate(0)
    candidate = GuestSpec.for_index(5, **override)  # ty: ignore[invalid-argument-type]
    with pytest.raises(AllocationConflictError) as caught:
        allocator.admit(candidate)
    assert caught.value.field_name == field_name
    assert caught.value.existing_index == 0


def test_validate_plan_checks_without_mutating() -> None:
    specs = GuestAllocator().allocate_range(0, 2)
    assert validate_plan(specs) == specs
    assert_disjoint(specs)

    with pytest.raises(AllocationConflictError):
        validate_plan((specs[0], GuestSpec.for_index(0)))


def test_negative_count_is_rejected() -> None:
    with pytest.raises(ValueError, match="count"):
        GuestAllocator().allocate_range(0, -1)
