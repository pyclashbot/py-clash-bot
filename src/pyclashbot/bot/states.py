"""time module for timing functions and controling pacing"""
import time

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
from pyclashbot.bot.open_chests_state import open_chests_state
from pyclashbot.bot.request_state import request_state
from pyclashbot.bot.upgrade_state import upgrade_cards_state
from pyclashbot.bot.war_state import war_state
from pyclashbot.memu.launcher import (
    close_clash_royale_app,
    restart_emulator,
    start_clash_royale,
)
from pyclashbot.utils.logger import Logger


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
) -> str:
    start_time = time.time()
    logger.log(f'Set the current state to "{state}"')
    logger.set_current_state(state)
    time.sleep(1)

    # header in the log file to split the log by state loop iterations
    logger.log(f"\n\n------------------------------\nSTATE == {state} ")

    if state is None:
        logger.error("Error! State is None!!")
        while 1:
            time.sleep(1)

    elif state == "start":  # --> open_chests
        # open clash
        logger.log("Running restart_emulator() for initial emulator boot")
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
                "Error 0124097926761 Clash main menu not found after restart! (RECURSIVE)"
            )
            for _ in range(3):
                logger.log(
                    "Error 33 wait_for_clash_main_menu() in restart state recursively restarting!"
                )
            logger.log("\n")
            next_state = "restart"

        # restart_vm(logger, vm_index)
        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        return next_state

    if state == "open_chests":  # --> upgrade
        next_state = "upgrade"

        # if job not selected, skip this state
        if not job_list["open_chests_user_toggle"]:
            logger.log("Open chests user toggle is off, skipping this state")
            return next_state

        # if job not ready, skip this state
        if not logger.check_if_can_open_chests(
            job_list["open_chests_increment_user_input"]
        ):
            logger.log("Cant open chests at this time, skipping this state")
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
            logger.log("Upgrade state isnt ready, skipping this state")
            return next_state

        # return output of this state
        return upgrade_cards_state(vm_index, logger, next_state)

    if state == "request":  # --> free_offer_collection
        next_state = "free_offer_collection"

        # if job not selected, return next state
        if not job_list["request_user_toggle"]:
            logger.log("Request job isnt toggled. Skipping")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_request(job_list["request_increment_user_input"]):
            logger.log("Request job isnt ready. Skipping")
            return next_state

        # return output of this state
        return request_state(vm_index, logger, next_state)

    if state == "free_offer_collection":  # --> randomize_deck
        next_state = "randomize_deck"

        # if job not selected, return next state
        if not job_list["free_offer_user_toggle"]:
            logger.log("Free offer state isnt toggled")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_collect_free_offer(
            job_list["free_offer_collection_increment_user_input"]
        ):
            logger.log("Free offer state isnt ready")
            return next_state

        # return output of this state
        return free_offer_collection_state(vm_index, logger, next_state)

    if state == "randomize_deck":  # --> start_fight
        next_state = "start_fight"

        # if randomize deck isnt toggled, return next state
        if not job_list["random_decks_user_toggle"]:
            logger.log("deck randomization isnt toggled. skipping this state")
            return next_state

        # if randomize deck isnt ready, return next state
        if not logger.check_if_can_randomize_deck(
            job_list["deck_randomization_increment_user_input"]
        ):
            logger.log("deck randomization isnt ready. skipping this state")
            return next_state

        return randomize_deck_state(vm_index, logger, next_state)

    if state == "start_fight":  # --> 1v1_fight, card_mastery
        next_state = "card_mastery"

        _1v1_toggle = job_list["1v1_battle_user_toggle"]
        _2v2_toggle = job_list["2v2_battle_user_toggle"]

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

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        return do_2v2_fight_state(vm_index, logger, next_state)

    if state == "1v1_fight":  # --> end_fight
        next_state = "end_fight"

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        return do_1v1_fight_state(vm_index, logger, next_state)

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
            logger.log("Card mastery job isnt toggled. Skipping this state")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_collect_card_mastery(
            job_list["card_mastery_collect_increment_user_input"]
        ):
            logger.log("Card mastery job isnt ready. Skipping this state")
            return next_state

        # return output of this state
        return card_mastery_collection_state(vm_index, logger, next_state)

    if state == "war":  # --> open_chests
        next_state = "open_chests"

        # if job not selected, return next state
        if not job_list["war_user_toggle"]:
            logger.log("War job isnt toggled. Skipping this state")
            return next_state

        # return output of this state
        return war_state(vm_index, logger, next_state)

    logger.error("Failure in state tree")
    return "fail"
