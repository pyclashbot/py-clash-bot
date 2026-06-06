"""random module for randomizing fight plays"""

import collections
import random
import time
from typing import Literal

from pyclashbot.bot.card_detection import (
    check_which_cards_are_available,
    create_default_bridge_iar,
    get_card_group,
    get_play_coords_for_card,
    switch_side,
    trigger_hero_champion_ability,
)
from pyclashbot.bot.coords import (
    CLOSE_BATTLE_LOG_BUTTON,
    EMOTE_BUTTON_COORD,
    EMOTE_ICON_COORDS,
    HAND_CARDS_COORDS,
    MAG_DUMP_CARD_COORDS,
    QUICKMATCH_POPUP_BUTTON_COORD,
    START_FIGHT_BUTTON_COORD,
)
from pyclashbot.bot.nav import (
    check_for_in_battle_with_delay,
    get_to_activity_log,
    get_to_main_after_fight,
    wait_for_battle_start,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.recorder import save_play, save_win_loss
from pyclashbot.bot.state_detect import (
    check_if_battle_has_ended,
    check_if_in_battle,
    check_if_on_clash_main_menu,
    check_pixels_for_win_in_battle_log,
    count_elixir,
)
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.logger import Logger

ELIXIR_WAIT_TIMEOUT = 40  # too high but someone got errors with that so idk
ABILITY_TRIGGER_DELAY_S = 3


def do_fight_state(
    emulator,
    logger: Logger,
    random_fight_mode,
    fight_mode_chosen,
    called_from_launching=False,
    recording_flag: bool = False,
) -> bool:
    """Handle the entirety of a battle state (start fight, do fight, end fight)."""

    logger.change_status("Waiting for battle to start")

    # Wait for battle start
    if wait_for_battle_start(emulator, logger) is False:
        logger.change_status("Timed out waiting for battle to start")
        return False

    logger.change_status("Starting fight loop")
    logger.log(f'This is the fight mode: "{fight_mode_chosen}"')

    # Run regular fight loop if random mode not toggled
    if not random_fight_mode and _fight_loop(emulator, logger, recording_flag) is False:
        logger.change_status("Fight loop failed")
        return False

    # Run random fight loop if random mode toggled
    if random_fight_mode and _random_fight_loop(emulator, logger) is False:
        logger.change_status("Fight loop failed")
        return False

    # Only log the fight if not called from the start
    if not called_from_launching:
        if fight_mode_chosen in ["Classic 1v1", "Trophy Road"]:
            logger.add_1v1_fight()
        elif fight_mode_chosen == "Classic 2v2":
            logger.increment_2v2_fights()

        if fight_mode_chosen == "Trophy Road":
            logger.increment_trophy_road_fights()
        elif fight_mode_chosen == "Classic 1v1":
            logger.increment_classic_1v1_fights()
        elif fight_mode_chosen == "Classic 2v2":
            logger.increment_classic_2v2_fights()

    interruptible_sleep(10)
    return True


def start_fight(emulator, logger, mode) -> bool:
    """Start a fight with the specified mode.

    Args:
        emulator: The emulator controller
        logger: Logger instance
        mode: Fight mode - must be one of "Classic 1v1", "Classic 2v2", or "Trophy Road"

    Returns:
        bool: True if fight started successfully, False otherwise
    """
    valid_modes = ["Classic 1v1", "Classic 2v2", "Trophy Road"]
    if mode not in valid_modes:
        logger.change_status(f"Invalid fight mode: {mode}")
        return False

    logger.change_status(f"Starting a {mode} fight")

    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot start fight")
        return False

    # For all modes (1v1 and 2v2), use the same start button
    # Mode is already set by select_mode() in states.py, just click start button
    emulator.click(START_FIGHT_BUTTON_COORD[0], START_FIGHT_BUTTON_COORD[1])

    # 2v2 needs a second popup after Start
    if mode == "Classic 2v2":
        logger.change_status("Classic 2v2 — clicking Quick Match popup...")
        interruptible_sleep(3)
        emulator.click(QUICKMATCH_POPUP_BUTTON_COORD[0], QUICKMATCH_POPUP_BUTTON_COORD[1])

    return True


def send_emote(emulator, logger: Logger):
    """Method to do an emote in a fight"""
    logger.change_status("Sending emote")

    # click emote button
    emulator.click(EMOTE_BUTTON_COORD[0], EMOTE_BUTTON_COORD[1])
    interruptible_sleep(0.33)

    emote_coord = random.choice(EMOTE_ICON_COORDS)
    emulator.click(emote_coord[0], emote_coord[1])


def mag_dump(emulator, logger):
    logger.log("Mag dumping...")
    for index in range(3):
        logger.change_status(f"Mag dump play {index}")
        card_index = random.randint(0, 3)
        card_coord = MAG_DUMP_CARD_COORDS[card_index]
        play_coord = (random.randint(101, 440), random.randint(50, 526))

        # record play here

        emulator.click(card_coord[0], card_coord[1])
        interruptible_sleep(0.1)

        emulator.click(play_coord[0], play_coord[1])
        interruptible_sleep(0.1)


def wait_for_elixir(
    emulator,
    logger,
    elixir_wait_amount,
    WAIT_THRESHOLD=5000,  # noqa: N803
    PLAY_THRESHOLD=10000,  # noqa: N803
    recording_flag: bool = False,
) -> Literal["restart", "no battle"] | bool:
    """Method to wait for 4 elixir during a battle"""
    start_time = time.time()
    battle_detection_lost_count = 0
    last_logged_second = -1
    last_lost_detection_log_second = -1
    ability_available_since = None

    while not count_elixir(emulator, elixir_wait_amount):
        # debug screenshot saving removed from production
        wait_time = time.time() - start_time
        elapsed_second = int(wait_time)
        if elapsed_second != last_logged_second:
            logger.change_status(
                f"Waiting for {elixir_wait_amount} elixir for {elapsed_second}s...",
            )
            last_logged_second = elapsed_second

        card_indices, ability_visible = check_which_cards_are_available(emulator, True, False)
        if ability_visible:
            if ability_available_since is None:
                ability_available_since = time.time()
                logger.change_status(
                    f"Hero/Champion ability ready — triggering in {ABILITY_TRIGGER_DELAY_S}s",
                )
            elif time.time() - ability_available_since >= ABILITY_TRIGGER_DELAY_S:
                trigger_hero_champion_ability(emulator, logger)
                ability_available_since = None
        else:
            ability_available_since = None

        card_inhand = len(card_indices)
        action_offset, _ = switch_side()
        if action_offset > PLAY_THRESHOLD and card_inhand > 0:
            logger.change_status("Battle too active — playing now")
            return True

        if action_offset > WAIT_THRESHOLD and card_inhand == 4:
            logger.change_status("All cards are available!")
            return True

        if wait_time > ELIXIR_WAIT_TIMEOUT:
            logger.change_status(status="Waited too long for elixir")
            return "restart"

        if not check_for_in_battle_with_delay(emulator):
            if check_if_battle_has_ended(emulator):
                logger.change_status(status="Battle ended — stopping elixir wait")
                return "no battle"

            battle_detection_lost_count += 1
            lost_detection_second = int(time.time())
            if lost_detection_second != last_lost_detection_log_second:
                logger.change_status(
                    status="Lost battle detection while waiting for elixir — assuming still in battle",
                )
                last_lost_detection_log_second = lost_detection_second
            if battle_detection_lost_count >= 4:
                logger.change_status(
                    status="Lost battle detection repeatedly — assuming battle ended",
                )
                return "no battle"

            interruptible_sleep(0.5)
            continue

        battle_detection_lost_count = 0

    logger.change_status(
        f"Took {str(time.time() - start_time)[:4]}s for {elixir_wait_amount} elixir.",
    )

    return True


def end_fight_state(
    emulator,
    logger: Logger,
    recording_flag,
    disable_win_tracker_toggle=True,
):
    """Method to handle the time after a fight and before the next state"""
    # count the crown score on this end-battle screen

    if get_to_main_after_fight(emulator, logger) is False:
        logger.change_status("Failed to return to main menu after fight")
        return False

    interruptible_sleep(3)

    # check if the prev game was a win
    if not disable_win_tracker_toggle:
        win_check_return = check_if_previous_game_was_win(emulator, logger)

        if win_check_return == "restart":
            return False

        if win_check_return:
            logger.add_win()

            if recording_flag:
                save_win_loss("win")
            return True

        logger.add_loss()
        if recording_flag:
            save_win_loss("loss")
    else:
        logger.log("Not checking win/loss because check is disabled")

    return True


def check_if_previous_game_was_win(
    emulator,
    logger: Logger,
) -> bool | Literal["restart"]:
    """Method to handle the checking if the previous game was a win or loss"""
    logger.change_status(status="Checking last game result")

    # Use wait_for_clash_main_menu to ensure we are on the main menu.
    if not wait_for_clash_main_menu(emulator, logger, deadspace_click=True):
        logger.change_status(status="Not on main menu — cannot check last game result")
        return "restart"

    # get to clash main options menu
    if get_to_activity_log(emulator, logger, printmode=False) == "restart":
        logger.change_status(status="Failed to open battle log")

        return "restart"

    logger.change_status(status="Checking battle log for win...")
    is_a_win = check_pixels_for_win_in_battle_log(emulator)
    result = "win" if is_a_win else "loss"
    logger.change_status(status=f"Last game result: {result}")

    # close battle log
    logger.change_status(status="Returning to main menu")
    emulator.click(CLOSE_BATTLE_LOG_BUTTON[0], CLOSE_BATTLE_LOG_BUTTON[1])
    if wait_for_clash_main_menu(emulator, logger) is False:
        logger.change_status(status="Timed out returning to main menu after battle log")
        return "restart"
    interruptible_sleep(2)

    return is_a_win


# main fight loops

# Initialize a deque with a maximum length of 3 to store the last three chosen cards
last_three_cards = collections.deque(maxlen=3)

_HAND_SLOT_LABELS = "ABCD"


def _hand_slot_label(card_index: int) -> str:
    return _HAND_SLOT_LABELS[card_index]


def _hand_slot_labels(card_indices: list[int]) -> str:
    return ", ".join(_hand_slot_label(i) for i in sorted(card_indices))


def select_card_index(card_indices, last_three_cards):
    if not card_indices:
        raise ValueError("card_indices cannot be empty")

    # First preference: Cards not in the last_three_cards queue
    preferred_cards = [index for index in card_indices if index not in last_three_cards]

    # Second preference: Cards not among the last two added to the queue
    if not preferred_cards and len(last_three_cards) == 3:
        preferred_cards = [index for index in card_indices if index not in list(last_three_cards)[-2:]]

    # Third preference: Any card except the most recently added one
    if not preferred_cards and last_three_cards:
        preferred_cards = [index for index in card_indices if index != last_three_cards[-1]]

    # Fallback: If all else fails, consider all cards
    if not preferred_cards:
        preferred_cards = card_indices

    return random.choice(preferred_cards)


def play_a_card(emulator, logger, recording_flag: bool, battle_strategy: "BattleStrategy") -> bool:
    print("\n")

    card_indices = check_which_cards_are_available(emulator, False, True)

    if not card_indices:
        logger.change_status("No cards ready yet...")
        return False

    card_index = select_card_index(card_indices, last_three_cards)
    if card_index not in last_three_cards:
        last_three_cards.append(card_index)

    card_id, play_coord = get_play_coords_for_card(emulator, logger, card_index, battle_strategy.get_elapsed_time())

    if None in [HAND_CARDS_COORDS, card_index]:
        logger.change_status("Non-fatal error: card index is None")
        return False

    if play_coord is None:
        logger.change_status("Non-fatal error: play coordinates are None")
        return False

    emulator.click(HAND_CARDS_COORDS[card_index][0], HAND_CARDS_COORDS[card_index][1])
    emulator.click(play_coord[0], play_coord[1])
    if recording_flag:
        save_play(play_coord, card_index)

    slot = _hand_slot_label(card_index)
    logger.log(
        f"Ready slots: {_hand_slot_labels(card_indices)} | chose {slot} | group: {get_card_group(card_id)}",
    )
    logger.change_status(f"Played {card_id} from slot {slot} at {play_coord}")
    logger.add_card_played()

    if random.randint(0, 9) == 1:
        send_emote(emulator, logger)
    return True


class BattleStrategy:
    """Manages battle timing and elixir selection strategy.

    Encapsulates the sophisticated elixir selection logic that changes
    based on battle phase, eliminating the need for global variables.
    """

    def __init__(self):
        self.start_time = None
        self.elixir_amounts = [3, 4, 5, 6, 7, 8, 9]

        # Strategy weights for each battle phase
        self.phase_strategies = {
            "early": [
                0,
                0,
                0,
                0,
                0.3,
                0.3,
                0.4,
            ],  # 0-7s: Conservative, wait for more elixir
            "single": [
                0.05,
                0.05,
                0.1,
                0.15,
                0.15,
                0.3,
                0.2,
            ],  # 7-90s: Balanced distribution
            "double": [
                0.05,
                0.05,
                0.1,
                0.15,
                0.25,
                0.3,
                0.1,
            ],  # 90-200s: Favor 7-8 elixir
            "triple": [
                0.05,
                0.05,
                0.1,
                0.1,
                0.3,
                0.4,
                0,
            ],  # 200s+: Heavy favor 7-8, never 9
        }

        # Wait/play thresholds for each phase
        self.phase_thresholds = {
            "early": (6000, 9000),
            "single": (6000, 9000),
            "double": (7000, 10000),
            "triple": (8000, 11000),
        }

    def start_battle(self):
        """Call when battle begins to start timing."""
        self.start_time = time.time()

    def get_elapsed_time(self):
        """Get seconds elapsed since battle start."""
        return time.time() - self.start_time if self.start_time else 0

    def get_battle_phase(self):
        """Determine current battle phase based on elapsed time."""
        elapsed = self.get_elapsed_time()
        if elapsed < 7:
            return "early"
        elif elapsed < 90:
            return "single"
        elif elapsed < 200:
            return "double"
        else:
            return "triple"

    def select_elixir_amount(self):
        """Select elixir amount to wait for based on current battle phase."""
        phase = self.get_battle_phase()
        weights = self.phase_strategies[phase]
        return random.choices(self.elixir_amounts, weights=weights, k=1)[0]

    def get_thresholds(self):
        """Get (WAIT_THRESHOLD, PLAY_THRESHOLD) for current battle phase."""
        phase = self.get_battle_phase()
        return self.phase_thresholds[phase]


def _fight_loop(emulator, logger: Logger, recording_flag: bool) -> bool:
    """Method for handling dynamically timed fight"""
    create_default_bridge_iar(emulator)
    collections.deque(maxlen=3)
    prev_cards_played = logger.get_cards_played()
    battle_detection_lost_count = 0

    # Initialize battle strategy and start timing
    battle_strategy = BattleStrategy()
    battle_strategy.start_battle()

    while True:
        if not check_for_in_battle_with_delay(emulator):
            if check_if_battle_has_ended(emulator):
                break

            battle_detection_lost_count += 1
            logger.change_status(
                f"Lost battle detection mid-fight ({battle_detection_lost_count}) — waiting it out",
            )

            # If we've lost detection several times in a row, assume the battle
            # ended even if we couldn't confirm it (prevents infinite loops if UI changes).
            if battle_detection_lost_count >= 4:
                logger.change_status(
                    "Lost battle detection repeatedly — assuming battle ended",
                )
                break

            interruptible_sleep(1)
            continue

        battle_detection_lost_count = 0
        # debug screenshot saving removed from production

        # Get elixir amount and thresholds based on current battle phase
        elixir_amount = battle_strategy.select_elixir_amount()
        wait_threshold, play_threshold = battle_strategy.get_thresholds()

        wait_output = wait_for_elixir(
            emulator,
            logger,
            elixir_amount,
            wait_threshold,
            play_threshold,
            recording_flag,
        )

        if wait_output == "restart":
            logger.change_status("Failed while waiting for elixir")
            return False

        if wait_output == "no battle":
            logger.change_status("Not in battle anymore!")
            break

        if not check_if_in_battle(emulator):
            if check_if_battle_has_ended(emulator):
                logger.change_status("Battle ended (confirmed)")
                break

            logger.change_status("Lost battle detection — continuing fight loop")
            continue

        if play_a_card(emulator, logger, recording_flag, battle_strategy) is False:
            logger.change_status("Failed to play a card, retrying...")

    logger.change_status("Fight complete")
    interruptible_sleep(2.13)
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return True


def _random_fight_loop(emulator, logger) -> bool:
    """Method for handling dynamically timed fight with random plays"""
    logger.change_status(status="Starting battle with random plays")
    fight_timeout = 5 * 60  # 5 minutes
    start_time = time.time()
    battle_detection_lost_count = 0

    # while in battle:
    while True:
        if not check_for_in_battle_with_delay(emulator):
            if check_if_battle_has_ended(emulator):
                break

            battle_detection_lost_count += 1
            logger.change_status(
                f"Lost battle detection mid-fight ({battle_detection_lost_count}) — waiting it out",
            )

            if battle_detection_lost_count >= 4:
                logger.change_status(
                    "Lost battle detection repeatedly — assuming battle ended",
                )
                break

            interruptible_sleep(1)
            continue

        battle_detection_lost_count = 0
        if time.time() - start_time > fight_timeout:
            logger.change_status("Random fight loop timed out after 5 minutes")
            return False

        mag_dump(emulator, logger)
        for _ in range(random.randint(1, 3)):
            logger.add_card_played()

        interruptible_sleep(8)

    logger.change_status("Random-plays fight complete")
    return True


if __name__ == "__main__":
    pass
