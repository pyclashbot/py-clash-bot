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
from utils.logger import Logger


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
    account_index_to_switch_to,
    account_switch_order,
):
    if state == "start":  # --> open_chests
        # open clash
        restart_vm(logger, vm_index)

        return "open_chests", account_index_to_switch_to

    elif state == "restart":  # --> open_chests
        print("Got to restart state")
        while 1:
            pass

        # restart_vm(logger, vm_index)
        return "open_chests", account_index_to_switch_to

    elif state == "open_chests":  # --> request
        NEXT_STATE = "request"

        if "open_chests" in job_list:
            return (
                open_chests_state(vm_index, logger, NEXT_STATE),
                account_index_to_switch_to,
            )
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
        if "free_offer_collection" in job_list:
            return (
                free_offer_collection_state(vm_index, logger, NEXT_STATE),
                account_index_to_switch_to,
            )

        return NEXT_STATE, account_index_to_switch_to

    elif state == "start_fight":  # --> 1v1_fight, account_switch
        NEXT_STATE = "account_switch"
        if "1v1_fight" in job_list:
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
    account_switch_order=[0]
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
