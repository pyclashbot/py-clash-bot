"""time module for timing functions and controling pacing"""

import random
import time

from pyclashbot.bot.card_mastery_state import card_mastery_state
from pyclashbot.bot.deck_randomization import randomize_deck_state
from pyclashbot.bot.fight import (
    do_1v1_fight_state,
    end_fight_state,
    start_fight,
)
from pyclashbot.bot.upgrade_state import upgrade_cards_state

from pyclashbot.utils.logger import Logger


mode_used_in_1v1 = None

CLASH_MAIN_DEADSPACE_COORD = (20, 520)


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
    global mode_used_in_1v1  # noqa: PLW0602
    start_time = time.time()
    logger.log(f'Set the current state to "{state}"')
    logger.set_current_state(state)
    time.sleep(0.1)

    # header in the log file to split the log by state loop iterations
    logger.log(f"\n\n------------------------------\nTHIS STATE IS: {state} ")

    if state is None:
        logger.error("Error! State is None!!")
        while 1:
            time.sleep(1)

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
            not job_list["trophy_road_1v1_battle_user_toggle"]
            and not job_list["path_of_legends_1v1_battle_user_toggle"]
            and not job_list["upgrade_user_toggle"]
            and not job_list["2v2_battle_user_toggle"]
        ):
            print(
                "No fight jobs, or card jobs are even toggled, so skipping random deck state."
            )
            return state_order.next_state(state)

        # Get the selected deck number from job_list, default to 2 if not found
        deck_number = job_list.get("deck_number_selection", 2)
        if randomize_deck_state(emulator, logger, deck_number) is False:
            return "restart"

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
            return "restart"

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
            return "restart"

        return state_order.next_state(state)

    if state == "start_fight":
        if not job_list["trophy_road_1v1_battle_user_toggle"]:
            print("1v1 mode isnt enabled. Skipping this state")
            return state_order.next_state(state)

        print("starting a fight")
        if start_fight(emulator, logger, "trophy_road") is False:
            print("starting a fight failed")
            logger.change_status("Failed while starting fight")
            return "restart"

        # go to next state
        return state_order.next_state(state)

    if state == "1v1_fight":
        random_plays_flag = job_list.get("random_plays_user_toggle", False)

        print(f"About to do a 1v1 fight. Real quick, here's the job list: {job_list}")
        for k, v in job_list.items():
            print(f"\t{k}={v}")

        recording_flag = job_list.get("record_fights_toggle", False)
        if (
            do_1v1_fight_state(
                emulator,
                logger,
                random_plays_flag,
                mode_used_in_1v1,
                False,
                recording_flag,
            )
            is False
        ):
            return "restart"

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
            return "restart"

        return state_order.next_state(state)

    logger.error("Failure in state tree")
    return "fail"


if __name__ == "__main__":
    pass
