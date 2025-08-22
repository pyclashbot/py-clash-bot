"""time module for timing functions and controling pacing"""

import random
import time

from pyclashbot.bot.card_mastery_state import card_mastery_state
from pyclashbot.bot.deck_randomization import randomize_deck_state
from pyclashbot.bot.fight import (
    do_fight_state,
    do_2v2_fight_state,
    end_fight_state,
    start_fight,
    select_mode,
)
from pyclashbot.bot.upgrade_state import upgrade_cards_state

from pyclashbot.utils.logger import Logger


def handle_state_failure(logger: Logger, state_name: str, function_name: str, error_msg: str = None) -> str:
    """Helper function to standardize error logging when states fail.
    
    Args:
        logger: The logger instance
        state_name: Name of the current state
        function_name: Name of the function that failed
        error_msg: Optional additional error message
    
    Returns:
        "restart" to trigger a restart
    """
    full_msg = f"State '{state_name}' failed in function '{function_name}'"
    if error_msg:
        full_msg += f": {error_msg}"
    
    logger.error(full_msg)
    logger.change_status(f"Error in {state_name} - restarting")
    print(f"[ERROR] {full_msg}")
    
    return "restart"


mode_used_in_1v1 = None
fight_mode_cycle_index = 0

CLASH_MAIN_DEADSPACE_COORD = (20, 520)


def get_next_fight_mode(job_list):
    """Get the next fight mode to use, cycling through enabled modes."""
    global fight_mode_cycle_index
    
    # Get all enabled fight modes
    enabled_modes = []
    if job_list.get("classic_1v1_user_toggle", False):
        enabled_modes.append("Classic 1v1")
    if job_list.get("classic_2v2_user_toggle", False):
        enabled_modes.append("Classic 2v2")
    if job_list.get("trophy_road_user_toggle", False):
        enabled_modes.append("Trophy Road")
    
    if not enabled_modes:
        return None
    
    # Get the current mode and increment the cycle index
    current_mode = enabled_modes[fight_mode_cycle_index % len(enabled_modes)]
    fight_mode_cycle_index += 1
    
    return current_mode


class StateHistory:
    def __init__(self, logger):
        self.time_history_string_list = []
        self.logger = logger

        # This increment time is hard-coded to be as
        # low as possible while not spamming slow states

        self.state2time_increment = {
            "upgrade": 0.0,
            "card_mastery": 0.0,
        }
        self.randomize_state2time_increment()

    def randomize_state2time_increment(self):
        percent_diff = 40
        for state, time_increment in self.state2time_increment.items():
            adjustment_factor = (
                random.randint(100 - percent_diff, 100 + percent_diff) / 100
            )
            new_value = time_increment * adjustment_factor
            self.state2time_increment[state] = new_value

    def print_time_increments(self):
        def hours2readable(hours):
            def format_digit(digit):
                digit = str(digit)
                while len(digit) < 2:
                    digit = "0" + str(digit)

                return str(digit)

            remainder = hours * 60 * 60

            hours = int(remainder // 3600)
            remainder = remainder % 3600

            minutes = int(remainder // 60)
            remainder = remainder % 60

            seconds = int(remainder)

            return (
                f"{format_digit(hours)}:{format_digit(minutes)}:{format_digit(seconds)}"
            )

        for state, time_increment in self.state2time_increment.items():
            print(f"{state:>20} : {hours2readable(time_increment)}")

    def print(self):
        print("State history:")
        for i, line in enumerate(self.time_history_string_list):
            print("\t", i, line)
        print("\n")

    def add_state(self, state):
        time_history_string = (
            f"{state} {time.time()} {int(self.logger.current_account)}"
        )
        self.time_history_string_list.append(time_history_string)

    def get_time_of_last_state(self, state: str) -> int:
        most_recent_time = -1
        for line in self.time_history_string_list:
            # filter by state
            if state in line:
                # split line
                try:
                    # split by account index
                    state, time, this_account_index = line.split(" ")
                    time = float(time)
                    this_account_index = int(this_account_index)
                    if int(this_account_index) != int(self.logger.current_account):
                        continue

                    # handling negative time for whatever reason
                    most_recent_time = max(most_recent_time, time)
                except Exception as e:
                    print(
                        f"Got an exception in StateHistory.get_time_of_last_state()\n{e}"
                    )
                    pass

        return int(most_recent_time)

    def state_is_ready(self, state: str) -> bool:
        def to_wrap():
            # if the state isnt in the state time increment dictionary, return True
            if state not in self.state2time_increment:
                print(
                    f"The time increment for {state} isn't specified, so defaulting to True (ready)"
                )
                return True

            # get the time of the last state
            last_time = self.get_time_of_last_state(state)

            # if the last time is -1, then the state has never been run before
            if last_time == -1:
                print(f"{state} has never been run before, so it is ready")
                return True

            # retrieve the time increment for this state
            time_increment = self.state2time_increment[state]

            # convert the time increment from hours to seconds
            time_increment = time_increment * 60 * 60

            # time since last state
            time_since_last_state = time.time() - last_time
            print(
                f"It's been {str(time_since_last_state)[:5]}s since this state has been ran"
            )

            # if the time since the last state is greater than the time increment, return True
            if time_since_last_state > time_increment:
                print(f"{state} is ready to run")
                return True

            # otherwise
            print(f"{state} is not ready to run")
            return False

        # add ready states to history because they always happen after True returns
        if to_wrap():
            self.add_state(state)
            return True

        return False


class StateOrder:
    def __init__(self):
        self.states = [
            "upgrade",
            "card_mastery",
            "randomize_deck",
            "start_fight",
            "1v1_fight",
            "2v2_fight",
            "end_fight",
        ]

    def next_state(self, curr_state):
        if curr_state in ["restart", "start"]:
            return self.states[0]

        if curr_state not in self.states:
            print(f'[!] Fatal error: state "{curr_state}" not in state order')
            return "No next state found!"

        this_index = self.states.index(curr_state)

        # if last, loop
        if this_index == len(self.states) - 1:
            return self.states[0]

        # else, return next state
        return self.states[this_index + 1]


def state_tree(
    emulator,
    logger: Logger,
    state,
    job_list,
    state_history: StateHistory,
    state_order: StateOrder,
) -> str:
    """Method to handle and loop between the various states of the bot"""
    global mode_used_in_1v1, fight_mode_cycle_index  # noqa: PLW0602
    start_time = time.time()
    logger.log(f'Set the current state to "{state}"')
    logger.set_current_state(state)
    time.sleep(0.1)

    # header in the log file to split the log by state loop iterations
    logger.log(f"\n\n------------------------------\nTHIS STATE IS: {state} ")

    if state is None:
        logger.error("Error! State is None!!")
        raise ValueError("State is None - critical error in state machine")
    
    if state == "fail":
        logger.error("State machine entered 'fail' state - stopping execution")
        logger.add_restart_after_failure()
        raise RuntimeError("State machine entered fail state - unrecoverable error")

    if state == "start":
        return state_order.next_state(state)

    if state == "restart":

        emulator.restart()
        return state_order.next_state(state)

    if state == "randomize_deck":
        # if randomize deck isn't toggled, return next state
        if not job_list["random_decks_user_toggle"]:
            logger.log("deck randomization isn't toggled. skipping this state")
            return state_order.next_state(state)

        # make sure there's a relevant job toggled, else just skip deck randomization
        if (
            not job_list.get("classic_1v1_user_toggle", False)
            and not job_list.get("classic_2v2_user_toggle", False)
            and not job_list.get("trophy_road_user_toggle", False)
            and not job_list["upgrade_user_toggle"]
        ):
            print(
                "No fight jobs, or card jobs are even toggled, so skipping random deck state."
            )
            return state_order.next_state(state)

        # Get the selected deck number from job_list, default to 2 if not found
        deck_number = job_list.get("deck_number_selection", 2)
        if randomize_deck_state(emulator, logger, deck_number) is False:
            return handle_state_failure(logger, "randomize_deck", "randomize_deck_state")

        return state_order.next_state(state)

    if state == "upgrade":
        # if job not selected, return next state
        if not job_list["upgrade_user_toggle"]:
            logger.log("Upgrade user toggle is off, skipping this state")
            return state_order.next_state(state)

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return state_order.next_state(state)

        # return output of this state
        if upgrade_cards_state(emulator, logger) is False:
            return handle_state_failure(logger, "upgrade", "upgrade_cards_state")

        return state_order.next_state(state)

    if state == "card_mastery":
        # if job not selected, return next state
        if not job_list["card_mastery_user_toggle"]:
            logger.log("Card mastery job isn't toggled. Skipping this state")
            return state_order.next_state(state)

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return state_order.next_state(state)

        # return output of this state
        if card_mastery_state(emulator, logger) is False:
            return handle_state_failure(logger, "card_mastery", "card_mastery_state")

        return state_order.next_state(state)

    if state == "start_fight":
        # Get the next fight mode to use
        selected_mode = get_next_fight_mode(job_list)
        
        if selected_mode is None:
            print("No fight modes are enabled. Skipping this state")
            return state_order.next_state(state)

        print(f"Starting a {selected_mode} fight")
        
        # Use select_mode to set the fight mode before starting
        if select_mode(emulator, selected_mode) is False:
            return handle_state_failure(logger, "start_fight", "select_mode", f"Failed to select mode: {selected_mode}")
            
        # Start fight using the selected mode directly
        if start_fight(emulator, logger, selected_mode) is False:
            return handle_state_failure(logger, "start_fight", "start_fight", "Failed while starting fight")

        # Store the selected mode for use in fight states
        mode_used_in_1v1 = selected_mode

        # go to next state
        return state_order.next_state(state)

    if state == "1v1_fight":
        # Check if the current mode is a 1v1 type (Classic 1v1 or Trophy Road)
        if mode_used_in_1v1 not in ["Classic 1v1", "Trophy Road"]:
            print(f"Current mode '{mode_used_in_1v1}' is not a 1v1 type. Skipping this state")
            return state_order.next_state(state)

        random_plays_flag = job_list.get("random_plays_user_toggle", False)


        recording_flag = job_list.get("record_fights_toggle", False)
        if (
            do_fight_state(
                emulator,
                logger,
                random_plays_flag,
                mode_used_in_1v1,
                False,
                recording_flag,
            )
            is False
        ):
            return handle_state_failure(logger, "1v1_fight", "do_fight_state", f"1v1 fight failed in mode: {mode_used_in_1v1}")

        return state_order.next_state(state)

    if state == "2v2_fight":
        # Check if the current mode is a 2v2 type (Classic 2v2)
        if mode_used_in_1v1 != "Classic 2v2":
            print(f"Current mode '{mode_used_in_1v1}' is not a 2v2 type. Skipping this state")
            return state_order.next_state(state)

        random_plays_flag = job_list.get("random_plays_user_toggle", False)


        recording_flag = job_list.get("record_fights_toggle", False)
        if (
            do_2v2_fight_state(
                emulator,
                logger,
                random_plays_flag,
                recording_flag,
            )
            is False
        ):
            return handle_state_failure(logger, "2v2_fight", "do_2v2_fight_state", "2v2 fight failed")

        return state_order.next_state(state)

    if state == "end_fight":
        recording_flag = job_list.get("record_fights_toggle", False)
        if (
            end_fight_state(
                emulator,
                logger,
                recording_flag,
                job_list["disable_win_track_toggle"],
            )
            is False
        ):
            return handle_state_failure(logger, "end_fight", "end_fight_state", "Failed to end fight properly")

        return state_order.next_state(state)

    logger.error("Failure in state tree")
    return "fail"


if __name__ == "__main__":
    pass
