"""Integration test: relaunch Clash Royale and wait for the main menu.

Relaunches the Clash Royale app via start_app(), then waits for the main menu
to be detected. A sanity check for the launch flow on any backend.

Note: NOT wired into test_jobs.py's SUITE — the SUITE's boot setup test already
covers reaching the main menu. This exists for one-off "is the launch helper
still working?" verification: construct an emulator + call run_test() directly,
or temporarily append run_test to the SUITE in test_jobs.py.
"""

from __future__ import annotations

from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.emulators.base import CLASH_ROYALE_PACKAGE


def run_test(emulator, logger) -> tuple[bool, str]:
    reachable, reason = emulator.is_reachable()
    if not reachable:
        return (False, f"Failed during precondition: emulator not reachable ({reason})")

    print(f"[+] starting {CLASH_ROYALE_PACKAGE}")
    emulator.start_app(CLASH_ROYALE_PACKAGE)

    print("[+] waiting for clash main menu (timeout 240s)...")
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Failed during wait_for_clash_main_menu (timed out — main menu never detected)")

    return (True, "")
