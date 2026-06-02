"""Module-level test: MEmu VM config drift detection + restore.

Flow:
  1. Drift a couple of config keys to known-bad values.
  2. Assert is_config_valid() == False (detection catches the drift).
  3. Run emu.configure() to restore the JSON-defined values.
  4. Assert is_config_valid() == True.

Requires an existing MEmu VM titled `pyclashbot-136`. VM may be stopped.

Run directly:
    py tests/memu/test_config.py

Or via pytest:
    pytest tests/memu/test_config.py
"""

from __future__ import annotations

import sys

from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger

DRIFT_VALUES = {"cpucap": "99", "fps": "99"}


def is_config_valid(emu: MemuEmulatorController) -> tuple[bool, list[str]]:
    """Compare every key in emu.config against the VM's live value.

    Returns (all_match, mismatches) where mismatches are human-readable strings.
    """
    live = emu._get_current_config()
    mismatches: list[str] = []
    for key, expected in emu.config.items():
        expected_str = str(expected)
        actual = live.get(key)
        if actual != expected_str:
            mismatches.append(f"{key}: expected={expected_str!r} actual={actual!r}")
    return (not mismatches, mismatches)


def test_config_drift_and_restore() -> None:
    emu = MemuEmulatorController(Logger(), debug_mode=True)

    try:
        # 1) Drift
        for key, bad_value in DRIFT_VALUES.items():
            emu.pmc.set_configuration_vm(key, bad_value, vm_index=emu.vm_index)
        print(f"[+] drifted keys: {list(DRIFT_VALUES)}")

        # 2) Detect drift
        valid_before, mismatches_before = is_config_valid(emu)
        print(f"[+] before configure(): valid={valid_before}  mismatches={mismatches_before}")
        assert valid_before is False, (
            "is_config_valid should return False after intentional drift, "
            f"but returned True (mismatches={mismatches_before})"
        )

        # 3) Restore via configure()
        emu.configure()

        # 4) Verify restored
        valid_after, mismatches_after = is_config_valid(emu)
        print(f"[+] after configure():  valid={valid_after}   mismatches={mismatches_after}")
        assert valid_after is True, (
            "is_config_valid should return True after configure(), "
            f"but returned False (mismatches={mismatches_after})"
        )

    finally:
        # Defensive cleanup: if we exited mid-drift before configure() ran,
        # rerun configure() so the VM doesn't stay broken.
        valid_now, _ = is_config_valid(emu)
        if not valid_now:
            print("[!] final state invalid — running configure() to clean up")
            emu.configure()


if __name__ == "__main__":
    try:
        test_config_drift_and_restore()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
