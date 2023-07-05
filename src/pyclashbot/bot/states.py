from bot.card_mastery_state import card_mastery_collection_state
from bot.do_1v1_fight_state import (
    do_1v1_fight_state,
    end_fight_state,
    start_1v1_fight_state,
)
from bot.free_offer_state import free_offer_collection_state
from bot.open_chests_state import open_chests_state

from bot.request_state import request_state
from bot.switch_account_state import switch_account_state

from memu.launcher import restart_vm
from memu.launcher import restart_emulator
from bot.navigation import wait_for_clash_main_menu
from memu.launcher import close_clash_royale_app, start_clash_royale
from bot.upgrade_state import upgrade_cards_state
from utils.logger import Logger
import time


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
    account_index_to_switch_to,
    account_switch_order,
):
    print(f"This state is {state}")
    if state is None:
        print("Error! State is None!!")
        while 1:
            pass

    if state == "start":  # --> open_chests
        # open clash
        restart_emulator(logger)

        return "open_chests", account_index_to_switch_to

    elif state == "restart":  # --> open_chests
        # close app
        close_clash_royale_app(logger, vm_index)
        time.sleep(10)

        # start app
        start_clash_royale(logger, vm_index)

        # wait for clash main
        wait_for_clash_main_menu(vm_index, logger)

        # restart_vm(logger, vm_index)
        return "open_chests", account_index_to_switch_to

    elif state == "open_chests":  # --> upgrade
        NEXT_STATE = "upgrade"

        if "Open Chests" in job_list:
            return (
                open_chests_state(vm_index, logger, NEXT_STATE),
                account_index_to_switch_to,
            )
        else:
            return NEXT_STATE, account_index_to_switch_to

    elif state == 'upgrade': # --> request
        NEXT_STATE = "request"
        if "upgrade" in job_list:
            return upgrade_cards_state(vm_index, logger, NEXT_STATE)
        else:
            return NEXT_STATE, account_index_to_switch_to



    elif state == "request":  # --> free_offer_collection
        NEXT_STATE = "free_offer_collection"
        if "request" in job_list:
            return (
                request_state(vm_index, logger, NEXT_STATE),
                account_index_to_switch_to,
            )
        return NEXT_STATE, account_index_to_switch_to
    
    elif state == "free_offer_collection":  # --> start_fight
        NEXT_STATE = "start_fight"
        if "free offer collection" in job_list:
            return (
                free_offer_collection_state(vm_index, logger, NEXT_STATE),
                account_index_to_switch_to,
            )

        return NEXT_STATE, account_index_to_switch_to

    elif state == "start_fight":  # --> 1v1_fight, account_switch
        NEXT_STATE = "account_switch"
        if "1v1 battle" in job_list:
            return start_1v1_fight_state(vm_index, logger), account_index_to_switch_to
        return NEXT_STATE, account_index_to_switch_to

    elif state == "1v1_fight":  # --> end_fight
        return do_1v1_fight_state(vm_index, logger), account_index_to_switch_to

    elif state == "end_fight":  # --> card_mastery
        NEXT_STATE = "card_mastery"
        return end_fight_state(vm_index, logger, NEXT_STATE), account_index_to_switch_to

    elif state == "card_mastery":  # --> account_switch
        NEXT_STATE = "account_switch"
        if "card_mastery" in job_list:
            return (
                card_mastery_collection_state(vm_index, logger, NEXT_STATE),
                account_index_to_switch_to,
            )
        else:
            return NEXT_STATE, account_index_to_switch_to

    elif state == "account_switch":  # --> open_chests
        NEXT_STATE = "open_chests"
        if "account_switch" in job_list:
            return (
                switch_account_state(
                    vm_index, logger, account_index_to_switch_to, account_switch_order
                ),
                account_index_to_switch_to,
            )
        return NEXT_STATE, account_index_to_switch_to

    print("Failure in state tree")
    return None, None


if __name__ == "__main__":
    logger = Logger()
    job_list = [
        "open_chests",
        "request",
        "free_offer_collection",
        "1v1_fight",
        # "account_switch",
        "card_mastery",
    ]
    state = "open_chests"

    # account_switch_order = [1, 0]
    account_switch_order = [0]
    account_index_to_switch_to = 0

    while 1:
        state, account_index_to_switch_to = state_tree(
            1,
            logger,
            state,
            job_list,
            account_index_to_switch_to,
            account_switch_order,
        )

    # screenshot(1)
