"""Integration test: launch Clash Royale on MEmu and wait for the main menu.

Precondition: MEmu VM titled `pyclashbot-136` is already running and signed in
to a Clash Royale account. The test does not boot the VM or sign in.

Flow:
  1. Attach to the running VM (debug_mode=True so no restart).
  2. Start Clash Royale via the package name.
  3. Call wait_for_clash_main_menu() — reuses existing bot helper.
  4. Pass if it returns True within CLASH_MAIN_WAIT_TIMEOUT (240s).

Run directly:
    py tests/clash-royale/test_wait_for_main_menu.py

Or via pytest:
    pytest tests/clash-royale/test_wait_for_main_menu.py
"""

from __future__ import annotations

import sys

from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger

CLASH_ROYALE_PACKAGE = "com.supercell.clashroyale"


def test_reaches_main_menu_after_launch() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    # Precondition: VM must already be running. start_app on a stopped VM hangs.
    vm = next((v for v in emu.pmc.list_vm_info() if v["index"] == emu.vm_index), None)
    assert vm is not None and vm["running"], (
        f"precondition failed: VM idx={emu.vm_index} is not running. " "boot the MEmu VM before running this test."
    )

    print(f"[+] starting {CLASH_ROYALE_PACKAGE} on VM idx={emu.vm_index}")
    emu.start_app(CLASH_ROYALE_PACKAGE)

    print("[+] waiting for clash main menu (timeout 240s)...")
    reached = wait_for_clash_main_menu(emu, logger)
    print(f"[+] wait_for_clash_main_menu returned: {reached}")

    assert reached is True, (
        "wait_for_clash_main_menu timed out — never detected the main menu pixels. "
        "verify Clash Royale launched, the account is signed in, and no popup is blocking."
    )


if __name__ == "__main__":
    try:
        test_reaches_main_menu_after_launch()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
