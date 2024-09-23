"""time module for timing functions and controling pacing"""

import time

from pyclashbot.bot.account_switching import switch_accounts
from pyclashbot.bot.bannerbox import collect_bannerbox_rewards_state
from pyclashbot.bot.battlepass import collect_battlepass_state
from pyclashbot.bot.buy_shop_offers import buy_shop_offers_state
from pyclashbot.bot.card_mastery_state import card_mastery_state
from pyclashbot.bot.daily_challenge_collection import collect_daily_rewards_state
from pyclashbot.bot.deck_randomization import randomize_deck_state
from pyclashbot.bot.do_fight_state import (
    do_1v1_fight_state,
    do_2v2_fight_state,
    end_fight_state,
    start_fight,
)
from pyclashbot.bot.donate import donate_cards_state
from pyclashbot.bot.level_up_chest import collect_level_up_chest_state
from pyclashbot.bot.nav import check_if_in_battle_at_start, check_if_on_clash_main_menu
from pyclashbot.bot.open_chests_state import get_chest_statuses, open_chests_state
from pyclashbot.bot.request_state import request_state
from pyclashbot.bot.season_shop_offers import collect_season_shop_offers_state
from pyclashbot.bot.trophy_road_rewards import collect_trophy_road_rewards_state
from pyclashbot.bot.upgrade_state import upgrade_cards_state
from pyclashbot.bot.war_state import war_state
from pyclashbot.memu.client import click
from pyclashbot.memu.docker import start_memu_dock_mode
from pyclashbot.memu.launcher import (
    close_clash_royale_app,
    restart_emulator,
    start_clash_royale,
)
from pyclashbot.utils.logger import Logger

mode_used_in_1v1 = None

CLASH_MAIN_DEADSPACE_COORD = (20, 520)


def get_render_mode(job_list):
    render_mode = "open_gl"
    if job_list["directx_toggle"]:
        render_mode = "directx"
    return render_mode


class StateHistory:
    def __init__(self, logger):
        self.time_history_string_list = []
        self.logger = logger

        # This increment time is hard-coded to be as
        # low as possible while not spamming slow states

        self.state2time_increment = {
            # "account_switch": 0.8,  #'state':increment in hours,
            "account_switch": 0.00001,  #'state':increment in hours,
            "open_chests": 1,  #'state':increment in hours,
            "level_up_chests": 0,  #'state':increment in hours,
            "upgrade": 0,  #'state':increment in hours,
            "trophy_rewards": 0.25,  #'state':increment in hours,
            "request": 1,  #'state':increment in hours,
            "donate": 1,  #'state':increment in hours,
            "shop_buy": 2,  #'state':increment in hours,
            "bannerbox": 1,  #'state':increment in hours,
            "daily_rewards": 0,  #'state':increment in hours,
            "battlepass_rewards": 0.25,  #'state':increment in hours,
            "card_mastery": 0,  #'state':increment in hours,
            "season_shop": 2,  #'state':increment in hours,
            "war": 0.25,  #'state':increment in hours,
        }

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
        self.print()

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
                    # account_switch state ignores account index filter
                    if state != "account_switch" and int(this_account_index) != int(
                        self.logger.current_account
                    ):
                        continue

                    # handling negative time for whatever reason
                    if time > most_recent_time:
                        most_recent_time = time
                except Exception as e:
                    print(
                        f"Got an expcetion in StateHistory.get_time_of_last_state()\n{e}"
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


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
    state_history: StateHistory,
) -> str:
    """Method to handle and loop between the various states of the bot"""
    global mode_used_in_1v1
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

    elif state == "start":  # --> account_switch
        if job_list["memu_attach_mode_toggle"]:
            start_memu_dock_mode()

        next_state = "account_switch"

        restart_emulator(logger, get_render_mode(job_list))

        logger.log(
            f"Emulator boot sequence took {str(time.time() - start_time)[:5]} seconds",
        )
        return next_state

    if state == "restart":  # --> account_switch
        next_state = "account_switch"

        logger.log("Entered the restart state after a failure in another state...")

        # close app
        logger.log("Running close_clash_royale_app()")
        close_clash_royale_app(logger, vm_index)
        logger.log("Manual sleep of 10 sec after closing app")
        time.sleep(10)

        logger.log("Incrementing restart counter in logger")
        logger.add_restart_after_failure()

        # start app
        logger.log("Starting clash app again")
        start_clash_royale(logger, vm_index)

        # wait for clash main to appear
        logger.change_status("Waiting for CR main menu after restart")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        time.sleep(12)
        while time.time() - clash_main_wait_start_time < clash_main_wait_timeout:
            time.sleep(1)
            clash_main_check = check_if_on_clash_main_menu(vm_index)
            if clash_main_check is True:
                break
            time.sleep(1)
            # Check if a battle is detected at start
            battle_start_result = check_if_in_battle_at_start(vm_index, logger)
            if battle_start_result == "good":
                break  # Successfully handled starting battle or end-of-battle scenario
            if battle_start_result == "restart":
                # Need to restart the process due to issues detected
                return state_tree(vm_index, logger, "restart", job_list, state_history)

            # click deadspace
            click(
                vm_index, CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1]
            )

        if check_if_on_clash_main_menu(vm_index) is not True:
            logger.log("Clash main wait timed out! These are the pixels it saw:")
            # for p in clash_main_check:
            #     logger.log(p)
            return state_tree(vm_index, logger, "restart", job_list, state_history)

        logger.log('Detected clash main at the end of "restart" state.')
        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]}seconds",
        )
        logger.log(f"Next state is {next_state}")

        return next_state

    if state == "account_switch":  # --> open_chests
        next_state = "open_chests"

        # if job not selected, return next state
        if not job_list["account_switching_toggle"]:
            logger.log("Account switching isn't toggled. Skipping this state")
            return next_state

        # if job not ready, return next state
        if state_history.state_is_ready("account_switch") is False:
            logger.log("Account switching isn't ready. Skipping this state")
            return next_state

        # see how many accounts there are in the toggle
        account_total = job_list["account_switch_count"]

        # see what account we should use right now
        next_account_index = logger.get_next_account(account_total)

        # switch to that account
        if (
            switch_accounts(
                vm_index,
                logger,
                next_account_index,
            )
            is False
        ):
            logger.change_status(
                f"Failed to switch to account #{next_account_index}. Restarting..."
            )
            return "restart"

        # set current account
        logger.current_account = int(next_account_index)

        # add this account to logger's account history object
        logger.add_account_to_account_history(next_account_index)

        return next_state

    if state == "open_chests":  # --> level_up_chest
        next_state = "level_up_chest"

        # if job not selected, skip this state
        logger.log('Checking if "open_chests_user_toggle" is on')
        if not job_list["open_chests_user_toggle"]:
            logger.log("Open chests user toggle is off, skipping this state")
            return next_state

        # if all chests are available, skip this increment user input check
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # run this state
        logger.log('Open chests is toggled and ready. Running "open_chests_state()"')
        return open_chests_state(vm_index, logger, next_state)

    if state == "level_up_chest":  # --> randomize_deck
        # keys for this state:
        #   level_up_chest_user_toggle
        #   level_up_chest_increment_user_input

        next_state = "randomize_deck"

        # if job not selected, skip this state
        logger.log('Checking if "level_up_chest_user_toggle" is on')
        if not job_list["level_up_chest_user_toggle"]:
            logger.log("level_up_chest_user_toggle is off, skipping this state")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # run this state
        logger.log(
            'Level up chests is toggled and ready. Running "collect_level_up_chest_state()"',
        )
        return collect_level_up_chest_state(vm_index, logger, next_state)

    if state == "randomize_deck":  # --> upgrade
        next_state = "upgrade"

        # if randomize deck isn't toggled, return next state
        if not job_list["random_decks_user_toggle"]:
            logger.log("deck randomization isn't toggled. skipping this state")
            return next_state

        # make sure there's a relevent job toggled, else just skip deck randomization
        if (
            not job_list["trophy_road_1v1_battle_user_toggle"]
            and not job_list["goblin_queens_journey_1v1_battle_user_toggle"]
            and not job_list["path_of_legends_1v1_battle_user_toggle"]
            and not job_list["upgrade_user_toggle"]
            and not job_list["2v2_battle_user_toggle"]
        ):
            print(
                "No fight jobs, or card jobs are even toggled, so skipping random deck state."
            )
            return next_state

        return randomize_deck_state(vm_index, logger, next_state)

    if state == "upgrade":  # --> trophy_rewards
        next_state = "trophy_rewards"

        # if job not selected, return next state
        if not job_list["upgrade_user_toggle"]:
            logger.log("Upgrade user toggle is off, skipping this state")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # return output of this state
        return upgrade_cards_state(vm_index, logger, next_state)

    if state == "trophy_rewards":  # --> request
        next_state = "request"

        # if job isnt selected, just return the next state
        if not job_list["trophy_road_rewards_user_toggle"]:
            logger.log(
                "Trophy rewards collection is not toggled. Skipping this state",
            )
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # run the state
        logger.log("Trophy rewards collection is ready!")
        return collect_trophy_road_rewards_state(vm_index, logger, next_state)

    if state == "request":  # --> donate
        next_state = "donate"

        # if job not selected, return next state
        if not job_list["request_user_toggle"]:
            logger.log("Request job isn't toggled. Skipping")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # return output of this state
        return request_state(vm_index, logger, next_state)

    if state == "donate":  # --> shop_buy
        next_state = "shop_buy"

        # if job not selected, return next state
        if not job_list["donate_toggle"] and not job_list["free_donate_toggle"]:
            logger.log("Donate job isn't toggled. Skipping")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # return output of this state
        return donate_cards_state(
            vm_index,
            logger,
            next_state,
            job_list["free_donate_toggle"],
        )

    if state == "shop_buy":  # --> bannerbox
        next_state = "bannerbox"

        # if job not selected, return next state
        if (
            not job_list["free_offer_user_toggle"]
            and not job_list["gold_offer_user_toggle"]
        ):
            logger.log("Free neither free, not gold offer buys toggled")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # return output of this state
        return buy_shop_offers_state(
            vm_index,
            logger,
            job_list["gold_offer_user_toggle"],
            job_list["free_offer_user_toggle"],
            next_state,
        )

    if state == "bannerbox":  # --> daily_rewards
        next_state = "daily_rewards"

        # if not in job list, go next state
        if not job_list["open_bannerbox_user_toggle"]:
            logger.log("Bannerbox job isn't toggled. Skipping")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        return collect_bannerbox_rewards_state(vm_index, logger, next_state)

    if state == "daily_rewards":  # --> battlepass_rewards
        next_state = "battlepass_rewards"

        # if job not toggled, return next state
        if not job_list["daily_rewards_user_toggle"]:
            logger.log("daily_rewards job isn't toggled. Skipping")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # run this job, return its output
        return collect_daily_rewards_state(vm_index, logger, next_state)

    if state == "battlepass_rewards":  # --> card_mastery
        next_state = "card_mastery"

        # if job not toggled go next state
        if not job_list["battlepass_collect_user_toggle"]:
            logger.log(
                "Battlepass collect is not toggled. Skipping this state",
            )
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        return collect_battlepass_state(vm_index, logger, next_state)

    if state == "card_mastery":  # --> season_shop
        next_state = "season_shop"

        # if job not selected, return next state
        if not job_list["card_mastery_user_toggle"]:
            logger.log("Card mastery job isn't toggled. Skipping this state")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # return output of this state
        return card_mastery_state(vm_index, logger, next_state)

    if state == "season_shop":  # --> start_fight
        next_state = "start_fight"

        # if job isnt toggled, return next state
        if not job_list["season_shop_buys_user_toggle"]:
            logger.log("Season shop buys is not toggled. Skipping this state")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        return collect_season_shop_offers_state(vm_index, logger, next_state)

    if state == "start_fight":  # --> 1v1_fight, war
        next_state = "war"

        if job_list["skip_fight_if_full_chests_user_toggle"] and (
            get_chest_statuses(vm_index).count("available") == 4
        ):
            logger.change_status("All chests are available. Skipping fight states")
            return next_state

        mode2toggle = {
            "2v2": job_list["2v2_battle_user_toggle"],
            "trophy_road": job_list["trophy_road_1v1_battle_user_toggle"],
            "path_of_legends": job_list["path_of_legends_1v1_battle_user_toggle"],
            "queens_journey": job_list["goblin_queens_journey_1v1_battle_user_toggle"],
        }

        for mode, toggle in mode2toggle.items():
            print(f"{mode:^14} : {toggle}")

        # if all are toggled off, return next_state
        if not any(mode2toggle.values()):
            logger.log("No fight modes are toggled. Skipping this state")
            return next_state

        mode = logger.pick_lowest_fight_type_count(mode2toggle)
        print(f"Lowest mode is: {mode}")

        if start_fight(vm_index, logger, mode) is False:
            logger.change_status("Failed while starting fight")
            return "restart"

        if mode == "2v2":
            next_state = "2v2_fight"
        else:
            next_state = "1v1_fight"

        # if neither, go to NEXT_STATE
        return next_state

    if state == "2v2_fight":  # --> end_fight
        next_state = "end_fight"

        random_fight_mode = job_list["random_plays_user_toggle"]

        print(f'random_fight_mode is {random_fight_mode} in state == "2v2_fight"')

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds",
        )

        return do_2v2_fight_state(
            vm_index,
            logger,
            next_state,
            random_fight_mode,
            False,
        )

    if state == "1v1_fight":  # --> end_fight
        next_state = "end_fight"

        random_fight_mode = job_list["random_plays_user_toggle"]
        print(f"Random fight mode is {random_fight_mode} in state == '1v1_fight'")

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds",
        )
        print(f"Fight mode is {mode_used_in_1v1}")
        return do_1v1_fight_state(
            vm_index,
            logger,
            next_state,
            random_fight_mode,
            mode_used_in_1v1,
            False,
        )

    if state == "end_fight":  # --> war
        next_state = "war"

        logger.log(
            f"This state: {state} took {str(time.time()- start_time)[:5]} seconds",
        )
        return end_fight_state(
            vm_index,
            logger,
            next_state,
            job_list["disable_win_track_toggle"],
        )

    if state == "war":  # --> account_switch
        next_state = "account_switch"

        # if job not selected, return next state
        if not job_list["war_user_toggle"]:
            logger.log("War job isn't toggled. Skipping this state")
            return next_state

        # if job not ready, go next state
        if state_history.state_is_ready(state) is False:
            logger.log(f"{state} isn't ready. Skipping this state...")
            return next_state

        # return output of this state
        return war_state(vm_index, logger, next_state)

    logger.error("Failure in state tree")
    return "fail"


def state_tree_tester(vm_index):
    logger = Logger()
    state = "account_switch"
    job_list = {
        # job toggles
        "open_battlepass_user_toggle": True,
        "open_chests_user_toggle": True,
        "request_user_toggle": True,
        "donate_toggle": True,
        "free_donate_toggle": True,
        "card_mastery_user_toggle": True,
        "free_offer_user_toggle": True,
        "gold_offer_user_toggle": True,
        "trophy_road_1v1_battle_user_toggle": False,
        "path_of_legends_1v1_battle_user_toggle": False,
        "goblin_queens_journey_1v1_battle_user_toggle": False,
        "2v2_battle_user_toggle": True,
        "upgrade_user_toggle": True,
        "war_user_toggle": True,
        "random_decks_user_toggle": True,
        "open_bannerbox_user_toggle": True,
        "daily_rewards_user_toggle": False,
        "battlepass_collect_user_toggle": True,
        "level_up_chest_user_toggle": True,
        "trophy_road_rewards_user_toggle": True,
        "season_shop_buys_user_toggle": True,
        # keep these off
        "disable_win_track_toggle": False,
        "skip_fight_if_full_chests_user_toggle": False,
        "random_plays_user_toggle": False,
        "memu_attach_mode_toggle": False,
        # account switching input info
        "account_switching_toggle": True,
        "account_switch_count": 2,
    }
    state_history = StateHistory(logger)

    while 1:
        state = state_tree(
            vm_index,
            logger,
            state,
            job_list,
            state_history,
        )
        if state == "restart":
            print("Restart state")
            input("Enter to continue...")


if __name__ == "__main__":
    state_tree_tester(1)
