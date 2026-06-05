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

from collections import defaultdict

from pyclashbot.bot.nav import (
    MAIN_PAGE_CHECKS,
    NAV_CLICKS,
    PAGE_MAIN,
    navigate_main_page,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.state_detect import check_if_on_clash_main_menu


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


def _only_on(emu, expected_page: str) -> tuple[bool, str]:
    actual = {page: bool(check(emu)) for page, check in MAIN_PAGE_CHECKS.items()}
    expected = {page: (page == expected_page) for page in MAIN_PAGE_CHECKS}
    if actual == expected:
        return (True, "")
    diffs = [
        f"{page}: expected={expected[page]} actual={actual[page]}"
        for page in MAIN_PAGE_CHECKS
        if actual[page] != expected[page]
    ]
    return (False, f"expected only on {expected_page!r}, page-check mismatch: " + "; ".join(diffs))


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    ok, msg = _only_on(emulator, PAGE_MAIN)
    if not ok:
        return (False, f"Failed during precondition page-check: {msg}")
    print(f"[+] precondition: on {PAGE_MAIN}")

    try:
        circuit = compute_eulerian_circuit(list(NAV_CLICKS.keys()), start=PAGE_MAIN)
        edges_to_walk = len(circuit) - 1
        if edges_to_walk != len(NAV_CLICKS):
            return (
                False,
                f"Failed during eulerian-circuit construction: expected {len(NAV_CLICKS)} edges, got {edges_to_walk}",
            )
        print(f"[+] eulerian circuit: {edges_to_walk} edges across {len(circuit)} stops")

        for i in range(edges_to_walk):
            start = circuit[i]
            end = circuit[i + 1]
            print(f"[{i + 1:>2}/{edges_to_walk}] {start} -> {end}")
            if not navigate_main_page(emulator, logger, start, end):
                return (False, f"Failed during navigate_main_page({start!r} -> {end!r})")
            ok, msg = _only_on(emulator, end)
            if not ok:
                return (False, f"Failed during page-check after {start!r} -> {end!r}: {msg}")

        if circuit[-1] != PAGE_MAIN:
            return (False, f"Failed during circuit termination: ended on {circuit[-1]!r}, expected {PAGE_MAIN!r}")

    finally:
        # Best-effort recovery: if we're not on main, try to find where we are
        # and navigate back so the next test starts in a known state.
        if not check_if_on_clash_main_menu(emulator):
            for page, check in MAIN_PAGE_CHECKS.items():
                if page == PAGE_MAIN:
                    continue
                if check(emulator):
                    print(f"[!] cleanup: navigating from {page} back to main")
                    navigate_main_page(emulator, logger, page, PAGE_MAIN)
                    break

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
