import time

from pyclashbot.bot.card_mastery_state import card_mastery_collection_state
from pyclashbot.bot.do_fight_state import (
    do_1v1_fight_state,
    do_2v2_fight_state,
    get_to_main_after_fight,
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
) -> str | tuple[None, None]:
    # [
    #     "Open Chests",
    #     "upgrade",
    #     "request",
    #     "free offer collection",
    #     "1v1 battle",
    #     "2v2 battle",
    #     "card mastery collection",
    #     "war",
    # ]

    print(f"This state is {state}")
    logger.set_current_state(state)
    time.sleep(1)

    if state is None:
        logger.error("Error! State is None!!")
        while 1:
            time.sleep(1)

    elif state == "start":  # --> open_chests
        # open clash
        restart_emulator(logger)

        return "open_chests"

    if state == "restart":  # --> open_chests
        # close app
        close_clash_royale_app(logger, vm_index)
        time.sleep(10)

        logger.add_restart_after_failure()

        # start app
        start_clash_royale(logger, vm_index)

        # wait for clash main
        wait_for_clash_main_menu(vm_index, logger)

        # restart_vm(logger, vm_index)
        return "open_chests"

    if state == "open_chests":  # --> upgrade
        next_state = "upgrade"

        if "open Chests" in job_list:
            return open_chests_state(vm_index, logger, next_state)

        return next_state

    if state == "upgrade":  # --> request
        next_state = "request"

        if "upgrade" in job_list and logger.check_if_can_card_upgrade():
            return upgrade_cards_state(vm_index, logger, next_state)

        return next_state

    if state == "request":  # --> free_offer_collection
        next_state = "free_offer_collection"

        can_request = logger.check_if_can_request()

        if (
            "request" in job_list and can_request
        ):  # request in job, request every 30 min
            return request_state(vm_index, logger, next_state)

        return next_state

    if state == "free_offer_collection":  # --> start_fight
        next_state = "start_fight"

        can_free_offer_collect = logger.check_if_can_collect_free_offer()

        if "free offer collection" in job_list and can_free_offer_collect:
            return free_offer_collection_state(vm_index, logger, next_state)

        return next_state

    if state == "start_fight":  # --> 1v1_fight, card_mastery
        next_state = "card_mastery"
        # if both 1v1 and 2v2, pick a random one
        if "1v1 battle" in job_list and "2v2 battle" in job_list:
            if logger.get_1v1_fights() < logger.get_2v2_fights():
                return start_1v1_fight_state(vm_index, logger)

            return start_2v2_fight_state(vm_index, logger)

        # if only 1v1, do 1v1
        if "1v1 battle" in job_list:
            return start_1v1_fight_state(vm_index, logger)

        # if only 2v2, do 2v2
        if "2v2 battle" in job_list:
            return start_2v2_fight_state(vm_index, logger)

        # if neither, go to NEXT_STATE
        return next_state

    if state == "2v2_fight":  # --> end_fight
        next_state = "end_fight"
        return do_2v2_fight_state(vm_index, logger, next_state)

    if state == "1v1_fight":  # --> end_fight
        next_state = "end_fight"
        return do_1v1_fight_state(vm_index, logger, next_state)

    if state == "end_fight":  # --> card_mastery
        next_state = "card_mastery"
        return get_to_main_after_fight(vm_index, logger, next_state)

    if state == "card_mastery":  # --> war
        next_state = "war"
        if "card mastery collection" in job_list:
            return card_mastery_collection_state(vm_index, logger, next_state)

        return next_state

    if state == "war":  # --> open_chests
        next_state = "open_chests"
        if "war" in job_list:
            return war_state(vm_index, logger, next_state)
        return next_state

    logger.error("Failure in state tree")
    return "fail"
