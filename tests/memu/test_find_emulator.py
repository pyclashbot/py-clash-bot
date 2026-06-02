"""Module-level test: detection of the clashbot MEmu VM by name.

Verifies both branches of `_get_clashbot_vm_index` behavior:
  1. When a VM titled EMULATOR_NAME exists  -> True
  2. When no such VM exists                 -> False

The single existing VM is renamed away and back during the test; nothing is
created or deleted. A try/finally guarantees the original name is restored
even if an assertion fails.

Run directly:
    py tests/memu/test_find_emulator.py

Or via pytest:
    pytest tests/memu/test_find_emulator.py
"""

from __future__ import annotations

import sys

from pymemuc import PyMemuc

from pyclashbot.emulators.memu import EMULATOR_NAME

TEMP_RENAME = "not-the-clashbot-vm"


def find_clashbot_vm(pmc: PyMemuc) -> bool:
    """Return True iff a VM whose title contains EMULATOR_NAME exists."""
    for vm in pmc.list_vm_info():
        if EMULATOR_NAME in vm["title"]:
            return True
    return False


def _get_target_index(pmc: PyMemuc, title: str) -> int | None:
    for vm in pmc.list_vm_info():
        if vm["title"] == title:
            return vm["index"]
    return None


def test_find_emulator_both_conditions() -> None:
    pmc = PyMemuc()

    target_idx = _get_target_index(pmc, EMULATOR_NAME)
    assert target_idx is not None, (
        f"precondition failed: no VM titled '{EMULATOR_NAME}' exists. " "create or rename one before running this test."
    )

    try:
        # 1) positive case
        assert find_clashbot_vm(pmc) is True, f"detection should return True when VM '{EMULATOR_NAME}' exists"
        print(f"[+] positive: detected '{EMULATOR_NAME}' at idx={target_idx}")

        # 2) negative case — rename away
        pmc.rename_vm(vm_index=target_idx, new_name=TEMP_RENAME)
        print(f"[+] renamed idx={target_idx} -> '{TEMP_RENAME}'")
        assert find_clashbot_vm(pmc) is False, f"detection should return False after renaming VM to '{TEMP_RENAME}'"
        print("[+] negative: not detected after rename")

    finally:
        # always restore — locate by the temp name in case the index shifted
        restore_idx = _get_target_index(pmc, TEMP_RENAME)
        if restore_idx is not None:
            pmc.rename_vm(vm_index=restore_idx, new_name=EMULATOR_NAME)
            print(f"[+] restored idx={restore_idx} -> '{EMULATOR_NAME}'")


if __name__ == "__main__":
    try:
        test_find_emulator_both_conditions()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
