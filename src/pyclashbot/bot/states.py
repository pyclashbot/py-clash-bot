"""time module for timing functions and controling pacing"""
import random
import time
from pyclashbot.bot.account_switching import switch_accounts
from pyclashbot.bot.bannerbox import collect_bannerbox_rewards_state

from pyclashbot.bot.card_mastery_state import card_mastery_collection_state
from pyclashbot.bot.deck_randomization import randomize_deck_state
from pyclashbot.bot.do_fight_state import (
    do_1v1_fight_state,
    do_2v2_fight_state,
    end_fight_state,
    start_1v1_fight_state,
    start_2v2_fight_state,
)
from pyclashbot.bot.free_offer_state import free_offer_collection_state
from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.bot.open_chests_state import get_chest_statuses, open_chests_state
from pyclashbot.bot.request_state import request_state
from pyclashbot.bot.upgrade_state import upgrade_cards_state
from pyclashbot.bot.war_state import war_state
from pyclashbot.memu.launcher import (
    close_clash_royale_app,
    restart_emulator,
    start_clash_royale,
)
from pyclashbot.utils.logger import Logger


class StateException(Exception):
    """custom exception for state errors"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class RestartException(StateException):
    """custom exception for restart errors"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
) -> str:
    """method to handle and loop between the various states of the bot"""
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

    elif state == "start":  # --> open_chests
        # open clash
        restart_emulator(logger)

        logger.log(
            f"Emulator boot sequence took {str(time.time() - start_time)[:5]} seconds"
        )
        return "open_chests"

    if state == "restart":  # --> open_chests
        logger.log("Entered the restart state after a failure in another state...")
        next_state = "open_chests"

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

        # wait for clash main
        logger.log("Running wait_for_clash_main_menu()")
        if wait_for_clash_main_menu(vm_index, logger) == "restart":
            logger.log(
                'Waited too long for clashmain in "restart". Recursively redoing restart state'
            )
            return "restart"

        logger.log('Detected clash main at the end of "restart" state.')

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )

        logger.log(f"Next state is {next_state}")

        return next_state

    if state == "open_chests":  # --> upgrade
        next_state = "upgrade"

        # if job not selected, skip this state
        logger.log('Checking if "open_chests_user_toggle" is on')
        if not job_list["open_chests_user_toggle"]:
            logger.log("Open chests user toggle is off, skipping this state")
            return next_state

        # if job not ready, skip this state
        logger.log('Checking if "open_chests_increment_user_input" is ready')
        if not logger.check_if_can_open_chests(
            job_list["open_chests_increment_user_input"]
        ):
            logger.log("Can't open chests at this time, skipping this state")
            return next_state

        # run this state
        logger.log('Open chests is toggled and ready. Running "open_chests_state()"')
        return open_chests_state(vm_index, logger, next_state)

    if state == "upgrade":  # --> request
        next_state = "request"

        # if job not selected, return next state
        if not job_list["upgrade_user_toggle"]:
            logger.log("Upgrade user toggle is off, skipping this state")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_card_upgrade(
            job_list["card_upgrade_increment_user_input"]
        ):
            logger.log("Upgrade state isn't ready, skipping this state")
            return next_state

        # return output of this state
        return upgrade_cards_state(vm_index, logger, next_state)

    if state == "request":  # --> free_offer_collection
        next_state = "free_offer_collection"

        # if job not selected, return next state
        if not job_list["request_user_toggle"]:
            logger.log("Request job isn't toggled. Skipping")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_request(job_list["request_increment_user_input"]):
            logger.log("Request job isn't ready. Skipping")
            return next_state

        # return output of this state
        return request_state(vm_index, logger, next_state)

    if state == "free_offer_collection":  # --> bannerbox
        next_state = "bannerbox"

        # if job not selected, return next state
        if not job_list["free_offer_user_toggle"]:
            logger.log("Free offer state isn't toggled")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_collect_free_offer(
            job_list["free_offer_collection_increment_user_input"]
        ):
            logger.log("Free offer state isn't ready")
            return next_state

        # return output of this state
        return free_offer_collection_state(vm_index, logger, next_state)

    if state == "bannerbox":  # --> randomize_deck
        next_state = "randomize_deck"
        if not job_list["open_bannerbox_user_toggle"]:
            logger.log("Bannerbox job isn't toggled. Skipping")
            return next_state

        return collect_bannerbox_rewards_state(vm_index, logger, next_state)

    if state == "randomize_deck":  # --> start_fight
        next_state = "start_fight"

        # if randomize deck isn't toggled, return next state
        if not job_list["random_decks_user_toggle"]:
            logger.log("deck randomization isn't toggled. skipping this state")
            return next_state

        # if randomize deck isn't ready, return next state
        if not logger.check_if_can_randomize_deck(
            job_list["deck_randomization_increment_user_input"]
        ):
            logger.log("deck randomization isn't ready. skipping this state")
            return next_state

        return randomize_deck_state(vm_index, logger, next_state)

    if state == "start_fight":  # --> 1v1_fight, card_mastery
        next_state = "card_mastery"

        _1v1_toggle = job_list["1v1_battle_user_toggle"]
        _2v2_toggle = job_list["2v2_battle_user_toggle"]

        # if all chests slots are taken, skip starting a battle
        if job_list["skip_fight_if_full_chests_user_toggle"]:
            if all(
                chest_status == "available"
                for chest_status in get_chest_statuses(vm_index)
            ):
                logger.change_status("All chests are available, skipping fight state")
                return next_state

        if _1v1_toggle and _2v2_toggle:
            logger.log("Both 1v1 and 2v2 are selected. Choosing the less used one")
        elif _1v1_toggle:
            logger.log("1v1 is toggled")
        elif _2v2_toggle:
            logger.log("2v2 is toggled")

        if _1v1_toggle and _2v2_toggle:
            if logger.get_1v1_fights() < logger.get_2v2_fights():
                return start_1v1_fight_state(vm_index, logger)

            return start_2v2_fight_state(vm_index, logger)

        # if only 1v1, do 1v1
        if _1v1_toggle:
            return start_1v1_fight_state(vm_index, logger)

        # if only 2v2, do 2v2
        if _2v2_toggle:
            return start_2v2_fight_state(vm_index, logger)

        # if neither, go to NEXT_STATE
        logger.log("Neither 1v1 or 2v2 is toggled. Skipping this state")
        return next_state

    if state == "2v2_fight":  # --> end_fight
        next_state = "end_fight"

        random_fight_mode = job_list["random_plays_user_toggle"]

        print(f'random_fight_mode is {random_fight_mode} in state == "2v2_fight"')

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )

        return do_2v2_fight_state(vm_index, logger, next_state, random_fight_mode)

    if state == "1v1_fight":  # --> end_fight
        next_state = "end_fight"

        random_fight_mode = job_list["random_plays_user_toggle"]
        print(f'random_fight_mode is {random_fight_mode} in state == "2v2_fight"')

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        return do_1v1_fight_state(vm_index, logger, next_state, random_fight_mode)

    if state == "end_fight":  # --> card_mastery
        next_state = "card_mastery"

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        return end_fight_state(vm_index, logger, next_state)

    if state == "card_mastery":  # --> war
        next_state = "war"

        # if job not selected, return next state
        if not job_list["card_mastery_user_toggle"]:
            logger.log("Card mastery job isn't toggled. Skipping this state")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_collect_card_mastery(
            job_list["card_mastery_collect_increment_user_input"]
        ):
            logger.log("Card mastery job isn't ready. Skipping this state")
            return next_state

        # return output of this state
        return card_mastery_collection_state(vm_index, logger, next_state)

    if state == "war":  # --> account_switch
        next_state = "account_switch"

        # if job not selected, return next state
        if not job_list["war_user_toggle"]:
            logger.log("War job isn't toggled. Skipping this state")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_do_war(job_list["war_attack_increment_user_input"]):
            logger.log("War job isn't ready. Skipping this state")
            return next_state

        # return output of this state
        return war_state(vm_index, logger, next_state)

    if state == "account_switch":  # --> open_chests
        next_state = "open_chests"

        # if job not selected, return next state
        if not job_list["account_switching_toggle"]:
            logger.log("Account switching isn't toggled. Skipping this state")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_switch_account(
            job_list["account_switching_increment_user_input"]
        ):
            logger.log("Account switching job isn't ready. Skipping this state")
            return next_state
        
        logger.log(
            f"Attempt to switch to account #{job_list['next_account']} of {job_list['account_switching_slider']}"
        )

        if switch_accounts(vm_index, logger, job_list["next_account"]) is False:
            return "restart"
        
        # increment next account iteration
        job_list["next_account"] += 1
        if job_list["next_account"] >= job_list["account_switching_slider"]:
            job_list["next_account"] = 0
        
        logger.log(f"Next account is {job_list['next_account']} / {job_list['account_switching_slider']}")

        # update current account # to GUI
        current_account = (
            job_list["next_account"] - 1
            if job_list["next_account"] > 0
            else job_list["account_switching_slider"]
        )
        logger.change_current_account(current_account)

        return next_state

    logger.error("Failure in state tree")
    return "fail"


if __name__ == "__main__":
    vm_index = 8
    logger = Logger()
    next_state = '"next state return string!!"'

    # upgrade test
    open_chests_state(vm_index, logger, next_state)
