"""Test: clan_chat_state — donate only.

Begins on main, runs clan_chat_state with only the donate flag enabled, ends
on main. A no-op (no donation requests visible) is still a pass.

Precondition: MEmu VM running, signed in to Clash Royale, in a clan, on main.

Run directly:
    py tests/clash-royale/jobs/test_clan_chat_donate.py
"""

from __future__ import annotations

from pyclashbot.bot.clan_chat_state import clan_chat_state
from pyclashbot.bot.nav import wait_for_clash_main_menu


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if not clan_chat_state(
        emulator,
        logger,
        donate_enabled=True,
        claim_enabled=False,
        request_enabled=False,
    ):
        return (False, "Failed during clan_chat_state(donate)")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
