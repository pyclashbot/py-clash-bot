"""Deterministic guest allocation and admission.

The allocator is intentionally dumb: derive the spec from its index, then refuse
to admit it if any identity field already belongs to another guest. No probing of
the host, docker, or ADB happens here, so the same plan is reproducible in tests
and on a fresh machine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pyclashbot.supervisor.spec import GuestSpec, GuestSpecError

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

#: Identity fields that must be unique across guests. ``index`` is included so
#: two specs cannot claim the same slice even if their overrides diverge.
COLLISION_FIELDS: tuple[str, ...] = (
    "index",
    "server_port",
    "device_port",
    "ip",
    "mac",
    "serial",
)


class AllocationConflictError(GuestSpecError):
    """A candidate reuses another guest's identity."""

    def __init__(self, *, field_name: str, value: Any, existing_index: int) -> None:
        super().__init__(f"{field_name}={value!r} is already used by guest index {existing_index}")
        self.field_name = field_name
        self.value = value
        self.existing_index = existing_index


@dataclass(slots=True)
class GuestAllocator:
    """Admits guests one at a time, rejecting any identity collision."""

    _specs: list[GuestSpec] = field(default_factory=list)

    @property
    def specs(self) -> tuple[GuestSpec, ...]:
        return tuple(self._specs)

    @property
    def by_serial(self) -> dict[str, GuestSpec]:
        return {spec.serial: spec for spec in self._specs}

    @property
    def by_index(self) -> dict[int, GuestSpec]:
        return {spec.index: spec for spec in self._specs}

    def admit(self, spec: GuestSpec) -> GuestSpec:
        for existing in self._specs:
            for field_name in COLLISION_FIELDS:
                if getattr(spec, field_name) == getattr(existing, field_name):
                    raise AllocationConflictError(
                        field_name=field_name,
                        value=getattr(spec, field_name),
                        existing_index=existing.index,
                    )
        self._specs.append(spec)
        return spec

    def allocate(self, index: int, **overrides: Any) -> GuestSpec:
        return self.admit(GuestSpec.for_index(index, **overrides))

    def allocate_range(self, start: int, count: int) -> tuple[GuestSpec, ...]:
        if count < 0:
            raise GuestSpecError(f"count must be >= 0, got {count}")
        return tuple(self.allocate(index) for index in range(start, start + count))


def validate_plan(specs: Iterable[GuestSpec]) -> tuple[GuestSpec, ...]:
    """Admission-check an arbitrary plan without mutating it."""
    allocator = GuestAllocator()
    for spec in specs:
        allocator.admit(spec)
    return allocator.specs


def assert_disjoint(specs: Sequence[GuestSpec]) -> None:
    """Raise on the first collision in ``specs`` (alias for plan validation)."""
    validate_plan(specs)
