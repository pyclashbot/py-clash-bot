"""The Clash Royale job suite as one ordered, parametrized test.

Each job/nav module exposes `run_test(emulator, logger) -> (bool, str)`; the
`SUITE` list below is the order (pytest preserves it). Run with `-x` — entries
double as setup for later ones (select_battle_mode leaves a mode the fight tests
need).
"""

from __future__ import annotations

import pytest

from .contract.test_screenshot import run_test as screenshot_contract
from .jobs.test_1v1_fight import run_test as fight_1v1
from .jobs.test_2v2_fight import run_test as fight_2v2
from .jobs.test_card_mastery import run_test as card_mastery
from .jobs.test_clan_chat_claim import run_test as clan_chat_claim
from .jobs.test_clan_chat_donate import run_test as clan_chat_donate
from .jobs.test_clan_chat_request import run_test as clan_chat_request
from .jobs.test_cycle_deck import run_test as cycle_deck
from .jobs.test_randomize_deck import run_test as randomize_deck
from .jobs.test_select_battle_mode import run_test as select_battle_mode
from .jobs.test_setup import run_app_installed
from .jobs.test_switch_account import run_test as switch_account
from .jobs.test_upgrade import run_test as upgrade
from .jobs.test_war import run_test as war
from .navigation.test_navigate_main_pages import run_test as nav_main_pages

# Fixed order — setup first (install check, then a screenshot smoke), cheap/safe
# jobs next, the fight chain last. The emulator is already booted and on the main
# menu by the time these run (controllers boot in construction; the fixture aborts
# if that fails). switch_account is a round-trip (slot 1 -> 2 -> 1) so the rest of
# the suite stays on slot 1.
SUITE = [
    ("app_installed", run_app_installed),
    ("screenshot_contract", screenshot_contract),
    ("nav_main_pages", nav_main_pages),
    ("switch_account", switch_account),
    ("upgrade", upgrade),
    ("card_mastery", card_mastery),
    ("clan_chat_claim", clan_chat_claim),
    ("clan_chat_donate", clan_chat_donate),
    ("clan_chat_request", clan_chat_request),
    ("war", war),
    ("select_battle_mode", select_battle_mode),
    ("randomize_deck", randomize_deck),
    ("cycle_deck", cycle_deck),
    ("1v1_fight", fight_1v1),
    ("2v2_fight", fight_2v2),
]


@pytest.mark.emulator
@pytest.mark.parametrize("run_test", [fn for _, fn in SUITE], ids=[name for name, _ in SUITE])
def test_clash_job(run_test, emulator, logger):
    ok, msg = run_test(emulator, logger)
    assert ok, msg
