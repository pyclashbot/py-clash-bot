"""Offline regression: every fight starts with an empty recent-card queue."""

from pyclashbot.bot import fight


def test_fight_loop_clears_last_three_cards(monkeypatch):
    # Simulate a previous fight leaving all three slots populated.
    fight.last_three_cards.clear()
    fight.last_three_cards.extend([0, 1, 2])
    assert len(fight.last_three_cards) == 3

    # Stop the fight loop immediately after its reset/setup path, before any
    # card can be played, so the assertion is about the start of the fight.
    monkeypatch.setattr(fight, "create_default_bridge_iar", lambda emulator: None)
    monkeypatch.setattr(fight, "_maybe_start_fight_recording", lambda *args, **kwargs: None)
    monkeypatch.setattr(fight, "check_for_in_battle_with_delay", lambda emulator: False)
    monkeypatch.setattr(fight, "check_if_battle_has_ended", lambda emulator: True)
    monkeypatch.setattr(fight, "stop_fight_capture", lambda *args, **kwargs: None)
    monkeypatch.setattr(fight.time, "sleep", lambda seconds: None)

    try:
        assert fight._fight_loop(None, fight.Logger(timed=False), recording_flag=False) is True
        assert list(fight.last_three_cards) == [], "next fight inherited the previous fight's cards"
    finally:
        fight.last_three_cards.clear()
