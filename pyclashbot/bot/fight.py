"""random module for randomizing fight plays"""

import collections
import logging
import random
import time
from typing import Literal

from pyclashbot.bot.card_detection import (
    check_which_cards_are_available,
    create_default_bridge_iar,
    get_play_coords_for_card,
    switch_side,
)
from pyclashbot.bot.nav import (
    check_for_in_battle_with_delay,
    check_for_trophy_reward_menu,
    check_if_in_battle,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    handle_trophy_reward_menu,
    wait_for_battle_start,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.recorder import save_play, save_win_loss
from pyclashbot.bot.statistics import BotStatistics
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_image,
    pixel_is_equal,
)

CLOSE_BATTLE_LOG_BUTTON: tuple[Literal[365], Literal[72]] = (365, 72)
# coords of the cards in the hand
HAND_CARDS_COORDS = [
    (142, 561),
    (210, 563),
    (272, 561),
    (341, 563),
]
CLOSE_THIS_CHALLENGE_PAGE_BUTTON = (27, 22)

QUICKMATCH_BUTTON_COORD = (
    274,
    353,
)  # coord of the quickmatch button after you click the battle button
ELIXER_WAIT_TIMEOUT = 40  # way to high but someone got errors with that so idk

EMOTE_BUTTON_COORD = (67, 521)
EMOTE_ICON_COORDS = [
    (124, 419),
    (182, 420),
    (255, 411),
    (312, 423),
    (133, 471),
    (188, 472),
    (243, 469),
    (308, 470),
]
CLASH_MAIN_DEADSPACE_COORD = (20, 520)
ELIXIR_COORDS = [
    [613, 149],
    [613, 165],
    [613, 188],
    [613, 212],
    [613, 240],
    [613, 262],
    [613, 287],
    [613, 314],
    [613, 339],
    [613, 364],
]
ELIXIR_COLOR = [240, 137, 244]


def do_fight_state(
    emulator,
    logger: BotStatistics,
    random_fight_mode,
    fight_mode_choosed,
    called_from_launching=False,
    recording_flag: bool = False,
) -> bool:
    """Handle the entirety of a battle state (start fight, do fight, end fight)."""

    logger.change_status("do_fight_state state")
    logger.change_status("Waiting for battle to start")

    # Wait for battle start
    if wait_for_battle_start(emulator, logger) is False:
        logger.change_status(
            "Error waiting for battle to start in do_fight_state()",
        )
        return False

    logger.change_status("Starting fight loop")
    logger.log(f'This is the fight mode: "{fight_mode_choosed}"')

    # Run regular fight loop if random mode not toggled
    if not random_fight_mode and _fight_loop(emulator, logger, recording_flag) is False:
        logger.change_status("Failure in fight loop")
        return False

    # Run random fight loop if random mode toggled
    if random_fight_mode and _random_fight_loop(emulator, logger) is False:
        logger.change_status("Failure in fight loop")
        return False

    # Only log the fight if not called from the start
    if not called_from_launching:
        if fight_mode_choosed in ["Classic 1v1", "Trophy Road"]:
            logger.add_1v1_fight()
        elif fight_mode_choosed == "Classic 2v2":
            logger.increment_2v2_fights()

        if fight_mode_choosed == "Trophy Road":
            logger.increment_trophy_road_fights()
        elif fight_mode_choosed == "Classic 1v1":
            logger.increment_classic_1v1_fights()
        elif fight_mode_choosed == "Classic 2v2":
            logger.increment_classic_2v2_fights()

    time.sleep(10)
    return True


def do_2v2_fight_state(
    emulator,
    logger: BotStatistics,
    random_fight_mode,
    recording_flag: bool = False,
) -> bool:
    """Handle the entirety of the 2v2 battle state (start fight, do fight, end fight)."""
    # Use the same fight logic as 1v1, just with 2v2 mode
    return do_fight_state(
        emulator,
        logger,
        random_fight_mode,
        "Classic 2v2",
        called_from_launching=False,
        recording_flag=recording_flag,
    )


def start_fight(emulator, logger, mode) -> bool:
    """Start a fight with the specified mode.

    Args:
        emulator: The emulator controller
        logger: BotStatistics instance
        mode: Fight mode - must be one of "Classic 1v1", "Classic 2v2", or "Trophy Road"

    Returns:
        bool: True if fight started successfully, False otherwise
    """
    # Validate mode parameter
    logger.log(f'Input mode type: "{type(mode)}"')
    logger.log(f"Input mode value: {mode}")
    valid_modes = ["Classic 1v1", "Classic 2v2", "Trophy Road"]
    logger.log(f"Valid modes: {valid_modes}")
    if mode not in valid_modes:
        logger.log(f"The valid modes for start_fight() are: {valid_modes}")
        logger.log(f"But start_fight() got an invalid mode: '{mode}'")
        return False

    logger.change_status(f"Starting a {mode} fight")

    # Check if on clash main menu
    logger.log("Checking if on clash main before starting fight...")
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on clash main menu, cannot start fight")
        return False

    # For all modes (1v1 and 2v2), use the same start button
    # Mode is already set by select_mode() in states.py, just click start button
    emulator.click(203, 487)
    logger.log("Clicked Start button at (203, 487)")

    # if its 2v2 mode, we gotta click that second popup
    if mode == "Classic 2v2":
        logger.change_status("Its 2v2 mode so we gotta click the quickmatch popup option!")
        time.sleep(3)
        quick_match_button_coord = [280, 350]
        emulator.click(quick_match_button_coord[0], quick_match_button_coord[1])
        logger.log(f"Clicked Quickmatch button at {quick_match_button_coord}")

    return True


def send_emote(emulator, logger: BotStatistics):
    """Method to do an emote in a fight"""
    logger.change_status("Hitting an emote")

    # click emote button
    emulator.click(EMOTE_BUTTON_COORD[0], EMOTE_BUTTON_COORD[1])
    time.sleep(0.33)

    emote_coord = random.choice(EMOTE_ICON_COORDS)
    emulator.click(emote_coord[0], emote_coord[1])


def mag_dump(emulator, logger):
    card_coords = [
        (137, 559),
        (206, 559),
        (274, 599),
        (336, 555),
    ]

    logger.log("Mag dumping...")
    for index in range(3):
        logger.change_status(f"mag dump play {index}")
        card_index = random.randint(0, 3)
        card_coord = card_coords[card_index]
        play_coord = (random.randint(101, 440), random.randint(50, 526))

        # record play here

        emulator.click(card_coord[0], card_coord[1])
        time.sleep(0.1)

        emulator.click(play_coord[0], play_coord[1])
        time.sleep(0.1)


def wait_for_elixer(
    emulator,
    logger,
    random_elixer_wait,
    WAIT_THRESHOLD=5000,  # noqa: N803
    PLAY_THRESHOLD=10000,  # noqa: N803
    recording_flag: bool = False,
) -> Literal["restart", "no battle"] | bool:
    """Method to wait for 4 elixer during a battle"""
    start_time = time.time()

    while not count_elixer(emulator, random_elixer_wait):
        # debug screenshot saving removed from production
        wait_time = time.time() - start_time
        logger.change_status(
            f"Waiting for {random_elixer_wait} elixer for {str(wait_time)[:4]}s...",
        )

        card_inhand = len(check_which_cards_are_available(emulator, True, False))
        action_offset, _ = switch_side()
        if action_offset > PLAY_THRESHOLD and card_inhand > 0:
            logger.change_status("Too much going on, playing now")
            return True

        if action_offset > WAIT_THRESHOLD and card_inhand == 4:
            logger.change_status("All cards are available!")
            return True

        if wait_time > ELIXER_WAIT_TIMEOUT:
            logger.change_status(status="Waited too long for elixer")
            return "restart"

        if not check_for_in_battle_with_delay(emulator):
            logger.change_status(status="Not in battle, stopping waiting for elixer.")
            return "no battle"

    logger.change_status(
        f"Took {str(time.time() - start_time)[:4]}s for {random_elixer_wait} elixer.",
    )

    return True


def count_elixer(emulator, elixer_count) -> bool:
    """Method to check for 4 elixer during a battle"""
    iar = emulator.screenshot()

    if pixel_is_equal(
        iar[ELIXIR_COORDS[elixer_count - 1][0], ELIXIR_COORDS[elixer_count - 1][1]],
        ELIXIR_COLOR,
        tol=65,
    ):
        return True
    return False


def end_fight_state(
    emulator,
    logger: BotStatistics,
    recording_flag,
    disable_win_tracker_toggle=True,
):
    """Method to handle the time after a fight and before the next state"""
    # count the crown score on this end-battle screen

    # get to clash main after this fight
    logger.log("Getting to clash main after doing a fight")
    if get_to_main_after_fight(emulator, logger) is False:
        logger.log("Error 69a3d69 Failed to get to clash main after a fight")
        return False

    logger.log("Made it to clash main after doing a fight")
    time.sleep(3)

    # check if the prev game was a win
    if not disable_win_tracker_toggle:
        win_check_return = check_if_previous_game_was_win(emulator, logger)

        if win_check_return == "restart":
            logger.log("Error 885869 Failed while checking if previous game was a win")
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
    logger: BotStatistics,
) -> bool | Literal["restart"]:
    """Method to handle the checking if the previous game was a win or loss"""
    logger.change_status(status="Checking if last game was a win/loss")

    # Use wait_for_clash_main_menu to ensure we are on the main menu.
    if not wait_for_clash_main_menu(emulator, logger, deadspace_click=True):
        logger.change_status(status='Error Not on main menu, returning "restart"')
        return "restart"

    # get to clash main options menu
    if get_to_activity_log(emulator, logger, printmode=False) == "restart":
        logger.change_status(
            status="Error 8967203948 get_to_activity_log() in check_if_previous_game_was_win()",
        )

        return "restart"

    logger.change_status(status="Checking if last game was a win...")
    is_a_win = check_pixels_for_win_in_battle_log(emulator)
    logger.change_status(status=f"Last game is win: {is_a_win}")

    # close battle log
    logger.change_status(status="Returning to clash main")
    emulator.click(CLOSE_BATTLE_LOG_BUTTON[0], CLOSE_BATTLE_LOG_BUTTON[1])
    if wait_for_clash_main_menu(emulator, logger) is False:
        logger.change_status(
            status="Error 95867235 wait_for_clash_main_menu() in check_if_previous_game_was_win()",
        )
        return "restart"
    time.sleep(2)

    return is_a_win


def check_pixels_for_win_in_battle_log(emulator) -> bool:
    """Method to check pixels that appear in the battle
    log to determing if the previous game was a win
    """
    line1 = check_line_for_color(
        emulator,
        x_1=47,
        y_1=135,
        x_2=109,
        y_2=154,
        color=(255, 51, 102),
    )
    line2 = check_line_for_color(
        emulator,
        x_1=46,
        y_1=152,
        x_2=115,
        y_2=137,
        color=(255, 51, 102),
    )
    line3 = check_line_for_color(
        emulator,
        x_1=47,
        y_1=144,
        x_2=110,
        y_2=147,
        color=(255, 51, 102),
    )

    if line1 and line2 and line3:
        return False
    return True


def find_post_battle_button(emulator):
    """Find and return coordinates for post-battle exit/OK button.

    Tries multiple detection methods in order:
    1. Pixel-based detection (fastest)
    2. Image recognition for OK button
    3. Image recognition for exit button

    Returns:
        tuple[int, int] | None: Button coordinates (x, y) or None if not found
    """
    iar = emulator.screenshot()

    # Method 1: Fast pixel-based detection
    pixels = [
        iar[545][178],
        iar[547][239],
        iar[553][214],
        iar[554][201],
    ]
    colors = [
        [255, 187, 104],
        [255, 187, 104],
        [255, 255, 255],
        [255, 255, 255],
    ]

    pixel_match = True
    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=20):
            pixel_match = False
            break

    if pixel_match:
        return (200, 550)

    # Method 2: Image recognition for OK button
    coord = find_image(iar, "ok_post_battle_button", tolerance=0.85)
    if coord is not None:
        return coord

    # Method 3: Image recognition for exit button
    coord = find_image(iar, "exit_battle_button", tolerance=0.9)
    if coord is not None:
        return coord

    return None


def get_to_main_after_fight(emulator, logger):
    timeout = 120  # s
    start_time = time.time()
    clicked_ok_or_exit = False

    logger.change_status("Returning to clash main after the fight...")

    while time.time() - start_time < timeout:
        # if on clash main
        if check_if_on_clash_main_menu(emulator) is True:
            # wait 3 seconds for the trophy road page to maybe appear bc of UI lag
            time.sleep(3)

            # if that trophy road page appears, handle it, then return True
            if check_for_trophy_reward_menu(emulator):
                print("Found trophy reward menu")
                handle_trophy_reward_menu(emulator, logger, printmode=False)
                time.sleep(2)

            print("Made it to clash main after a fight")
            return True

        # check for trophy reward screen
        if check_for_trophy_reward_menu(emulator):
            print("Found trophy reward menu!\nHandling Trophy Reward Menu")
            handle_trophy_reward_menu(emulator, logger, printmode=False)
            time.sleep(3)
            continue

        # check for post-battle button (OK/exit)
        if not clicked_ok_or_exit:
            button_coord = find_post_battle_button(emulator)
            if button_coord is not None:
                logging.info("Found post-battle button, clicking it.")
                emulator.click(button_coord[0], button_coord[1])
                clicked_ok_or_exit = True
                continue

        time.sleep(1)
        logging.info("Clicking on deadspace to close potential pop-up windows.")
        emulator.click(CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1])

    return False


# main fight loops

# Initialize a deque with a maximum length of 3 to store the last three chosen cards
last_three_cards = collections.deque(maxlen=3)


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

    # check which cards are available
    logger.change_status("Looking at which cards are available")
    available_card_check_start_time = time.time()
    card_indicies = check_which_cards_are_available(emulator, False, True)

    if not card_indicies:
        logger.change_status("No cards ready yet...")
        return False

    available_card_check_time_taken = str(
        time.time() - available_card_check_start_time,
    )[:3]

    logger.change_status(
        f"These cards are available: {card_indicies} ({available_card_check_time_taken}s)",
    )

    card_index = select_card_index(card_indicies, last_three_cards)
    if card_index not in last_three_cards:
        last_three_cards.append(card_index)
    logger.change_status(f"Choosing this card index: {card_index}")

    # get a coord based on the selected side
    play_coord_calculation_start_time = time.time()
    card_id, play_coord = get_play_coords_for_card(emulator, logger, card_index, battle_strategy.get_elapsed_time())
    play_coord_calculation_time_taken = str(
        time.time() - play_coord_calculation_start_time,
    )[:3]

    logger.change_status(
        f"Calculated play for: {card_id} at {play_coord} ({play_coord_calculation_time_taken}s)",
    )

    # click the card index
    click_and_play_card_start_time = time.time()
    if None in [HAND_CARDS_COORDS, card_index]:
        logger.change_status("[!] Non fatal error: card_index is None")
        return False

    logger.change_status(f"Playing card {card_index}")
    emulator.click(HAND_CARDS_COORDS[card_index][0], HAND_CARDS_COORDS[card_index][1])

    # click the play coord
    if play_coord is None:
        logger.change_status("[!] Non fatal error: play_coord is None")
        return False

    emulator.click(play_coord[0], play_coord[1])
    click_and_play_card_time_taken = str(time.time() - click_and_play_card_start_time)[:3]
    if recording_flag:
        save_play(play_coord, card_index)

    logger.change_status(f"Made the play {click_and_play_card_time_taken}s")
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


def _fight_loop(emulator, logger: BotStatistics, recording_flag: bool) -> bool:
    """Method for handling dynamically timed fight"""
    create_default_bridge_iar(emulator)
    collections.deque(maxlen=3)
    prev_cards_played = logger.get_cards_played()

    # Initialize battle strategy and start timing
    battle_strategy = BattleStrategy()
    battle_strategy.start_battle()

    while check_for_in_battle_with_delay(emulator):
        # debug screenshot saving removed from production

        # Get elixir amount and thresholds based on current battle phase
        elixir_amount = battle_strategy.select_elixir_amount()
        wait_threshold, play_threshold = battle_strategy.get_thresholds()

        wait_output = wait_for_elixer(
            emulator,
            logger,
            elixir_amount,
            wait_threshold,
            play_threshold,
            recording_flag,
        )

        if wait_output == "restart":
            logger.change_status("Failure while waiting for elixer")
            return False

        if wait_output == "no battle":
            logger.change_status("Not in battle anymore!")
            break

        if not check_if_in_battle(emulator):
            logger.change_status("Not in a battle anymore")
            break

        play_start_time = time.time()
        if play_a_card(emulator, logger, recording_flag, battle_strategy) is False:
            logger.change_status("Failed to play a card, retrying...")
        # play_time_taken = str(time.time() - play_start_time)[:4]
        logger.change_status(
            f"Made a play in {str(time.time() - play_start_time)[:4]}s",
        )

    logger.change_status("End of the fight!")
    time.sleep(2.13)
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return True


def _random_fight_loop(emulator, logger) -> bool:
    """Method for handling dynamically timed fight with random plays"""
    logger.change_status(status="Starting battle with random plays")
    fight_timeout = 5 * 60  # 5 minutes
    start_time = time.time()

    # while in battle:
    while check_if_in_battle(emulator):
        if time.time() - start_time > fight_timeout:
            logger.change_status("_random_fight_loop() timed out. Breaking")
            return False

        mag_dump(emulator, logger)
        for _ in range(random.randint(1, 3)):
            logger.add_card_played()

        time.sleep(8)

    logger.change_status("Finished with battle with random plays...")
    return True


if __name__ == "__main__":
    pass
