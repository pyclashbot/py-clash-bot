"""Integration test: relaunch Clash Royale and wait for the main menu.

Kills+relaunches the Clash Royale app via start_app(), then waits for the
main menu to be detected. This is a sanity check for the launch flow.

Note: NOT included in test_all_clash.py's default suite — the runner's
precondition check already verifies the main menu is reached before any
job test runs. This test exists for one-off "is the launch helper still
working?" verification.

Run via tests/clash-royale/test_all_clash.py (passed explicitly) or directly
construct an emulator + call run_test().
"""

from __future__ import annotations

from pyclashbot.bot.nav import wait_for_clash_main_menu

CLASH_ROYALE_PACKAGE = "com.supercell.clashroyale"


def run_test(emulator, logger) -> tuple[bool, str]:
    vm = next((v for v in emulator.pmc.list_vm_info() if v["index"] == emulator.vm_index), None)
    if vm is None or not vm["running"]:
        return (False, f"Failed during precondition: VM idx={emulator.vm_index} is not running")

    print(f"[+] starting {CLASH_ROYALE_PACKAGE} on VM idx={emulator.vm_index}")
    emulator.start_app(CLASH_ROYALE_PACKAGE)

    print("[+] waiting for clash main menu (timeout 240s)...")
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Failed during wait_for_clash_main_menu (timed out — main menu never detected)")

    return (True, "")
