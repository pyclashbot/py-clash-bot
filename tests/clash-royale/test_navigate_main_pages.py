"""Main nav test: every page <-> every page permutation.

Walks an Eulerian circuit through the 5-page graph (main, card_page, shop,
social, clan-chat) so each of the 20 directed edges is traversed exactly once.
After every navigation, asserts that ONLY the destination page's check returns
True and the other four return False — exercises both branches of every check
function across the suite.

Precondition: MEmu VM `pyclashbot-136` running, signed in to Clash Royale, and
the user has parked the emulator on the main menu.

Postcondition: ends on main menu (Eulerian circuit terminates at the start).

Run directly:
    py tests/clash-royale/test_navigate_main_pages.py
"""

from __future__ import annotations

import sys
from collections import defaultdict

from pyclashbot.bot.nav import (
    MAIN_PAGE_CHECKS,
    NAV_CLICKS,
    PAGE_MAIN,
    check_if_on_clash_main_menu,
    navigate_main_page,
    wait_for_clash_main_menu,
)
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger


def compute_eulerian_circuit(edges: list[tuple[str, str]], start: str) -> list[str]:
    """Hierholzer's algorithm. Returns a node sequence covering every edge once."""
    out_edges: dict[str, list[str]] = defaultdict(list)
    for u, v in edges:
        out_edges[u].append(v)

    stack = [start]
    circuit: list[str] = []
    while stack:
        v = stack[-1]
        if out_edges[v]:
            stack.append(out_edges[v].pop())
        else:
            circuit.append(stack.pop())
    return list(reversed(circuit))


def assert_only_on(emu, expected_page: str) -> None:
    """Assert check_if_on_<expected> is True and every other page check is False."""
    actual = {page: bool(check(emu)) for page, check in MAIN_PAGE_CHECKS.items()}
    expected = {page: (page == expected_page) for page in MAIN_PAGE_CHECKS}
    if actual != expected:
        diffs = [
            f"{page}: expected={expected[page]} actual={actual[page]}"
            for page in MAIN_PAGE_CHECKS
            if actual[page] != expected[page]
        ]
        raise AssertionError(f"expected to be only on {expected_page!r}, but page-check mismatch: " + "; ".join(diffs))


def test_navigate_all_main_page_permutations() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    assert wait_for_clash_main_menu(emu, logger), "precondition: not on main menu at start"
    assert_only_on(emu, PAGE_MAIN)
    print(f"[+] precondition: on {PAGE_MAIN}")

    try:
        circuit = compute_eulerian_circuit(list(NAV_CLICKS.keys()), start=PAGE_MAIN)
        edges_to_walk = len(circuit) - 1
        assert edges_to_walk == len(
            NAV_CLICKS
        ), f"eulerian circuit should cover all {len(NAV_CLICKS)} edges, got {edges_to_walk}"
        print(f"[+] eulerian circuit: {edges_to_walk} edges across {len(circuit)} stops")

        for i in range(edges_to_walk):
            start = circuit[i]
            end = circuit[i + 1]
            print(f"[{i + 1:>2}/{edges_to_walk}] {start} -> {end}")
            ok = navigate_main_page(emu, logger, start, end)
            assert ok, f"navigate_main_page({start!r}, {end!r}) returned False"
            assert_only_on(emu, end)

        assert circuit[-1] == PAGE_MAIN, f"circuit should end on {PAGE_MAIN!r}, ended on {circuit[-1]!r}"
        assert_only_on(emu, PAGE_MAIN)
        print(f"[+] finished on {PAGE_MAIN}")

    finally:
        # Best-effort recovery: if we're not on main, try to find where we are
        # and navigate back so the next test starts in a known state.
        if not check_if_on_clash_main_menu(emu):
            for page, check in MAIN_PAGE_CHECKS.items():
                if page == PAGE_MAIN:
                    continue
                if check(emu):
                    print(f"[!] cleanup: navigating from {page} back to main")
                    navigate_main_page(emu, logger, page, PAGE_MAIN)
                    break


if __name__ == "__main__":
    try:
        test_navigate_all_main_page_permutations()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
