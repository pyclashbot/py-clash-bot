"""Multi-guest supervisor skeleton.

Deterministic identity and allocation, container/AVD re-create with readiness and
onboarding hooks, process-per-guest supervision, and per-guest metrics. The
module boundary is stdlib-only and side effects are injected, so the skeleton is
tested offline before live onboarding is wired in.
"""

from __future__ import annotations

from pyclashbot.supervisor.alloc import (
    AllocationConflictError,
    GuestAllocator,
    assert_disjoint,
    validate_plan,
)
from pyclashbot.supervisor.guest import (
    AvdRuntime,
    CommandResult,
    DockerRuntime,
    GuestManager,
    spawn_child,
)
from pyclashbot.supervisor.metrics import GuestMetrics, MetricsRegistry
from pyclashbot.supervisor.runner import (
    AlreadyRunningError,
    AlreadySupervisedError,
    Backoff,
    RestartBudgetExceededError,
    SingleInstanceLock,
    Supervisor,
    SupervisorError,
    guest_child_argv,
    guest_child_env,
)
from pyclashbot.supervisor.spec import GuestSpec, GuestSpecError

__all__ = [
    "AllocationConflictError",
    "AlreadyRunningError",
    "AlreadySupervisedError",
    "AvdRuntime",
    "Backoff",
    "CommandResult",
    "DockerRuntime",
    "GuestAllocator",
    "GuestManager",
    "GuestMetrics",
    "GuestSpec",
    "GuestSpecError",
    "MetricsRegistry",
    "RestartBudgetExceededError",
    "SingleInstanceLock",
    "Supervisor",
    "SupervisorError",
    "assert_disjoint",
    "guest_child_argv",
    "guest_child_env",
    "spawn_child",
    "validate_plan",
]
