import time

from pyclashbot.bot.card_mastery_state import card_mastery_collection_state
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
from pyclashbot.bot.switch_account_state import switch_account_state
from pyclashbot.bot.upgrade_state import upgrade_cards_state
from pyclashbot.bot.war_state import war_state
from pyclashbot.memu.launcher import (
    close_clash_royale_app,
    restart_emulator,
    start_clash_royale,
)
from pyclashbot.utils.logger import Logger



def clip_that():
    import pyautogui
    time.sleep(5)
    print('Clipping this error!')
    pyautogui.moveTo(2535,1253)
    time.sleep(1)
    pyautogui.click()
    time.sleep(5)


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
    account_index_to_switch_to,
    account_switch_order,
):  #prospector: --disable too-complex; pylint: disable=too-many-arguments



    print(f"This state is {state}")
    if state is None:
        print("Error! State is None!!")
        while 1:
            pass

    elif state == "start":  # --> open_chests
        # open clash
        restart_emulator(logger)

        return "open_chests", account_index_to_switch_to

    elif state == "restart":  # --> open_chests
        ####DEBUG
        for _ in range(5):
            print("ENTERED RESTART STATE. INFINITE LOOP")
        # clip_that()
        # while 1:
        #     pass

        # close app
        close_clash_royale_app(logger, vm_index)
        time.sleep(10)

        logger.add_restart_after_failure()

        # start app
        start_clash_royale(logger, vm_index)

        # wait for clash main
        wait_for_clash_main_menu(vm_index, logger)

        # restart_vm(logger, vm_index)
        return "open_chests", account_index_to_switch_to

    elif state == "open_chests":  # --> upgrade
        next_state = "upgrade"

        if "Open Chests" in job_list:
            return (
                open_chests_state(vm_index, logger, next_state),
                account_index_to_switch_to,
            )
        return next_state, account_index_to_switch_to

    elif state == "upgrade":  # --> request
        next_state = "request"
        if "upgrade" in job_list:
            return (
                upgrade_cards_state(vm_index, logger, next_state),
                account_index_to_switch_to,
            )
        return next_state, account_index_to_switch_to

    elif state == "request":  # --> free_offer_collection
        next_state = "free_offer_collection"
        if "request" in job_list:
            return (
                request_state(vm_index, logger, next_state),
                account_index_to_switch_to,
            )
        return next_state, account_index_to_switch_to

    elif state == "free_offer_collection":  # --> start_fight
        next_state = "start_fight"
        if "free offer collection" in job_list:
            return (
                free_offer_collection_state(vm_index, logger, next_state),
                account_index_to_switch_to,
            )

        return next_state, account_index_to_switch_to

    elif state == "start_fight":  # --> 1v1_fight, card_mastery
        next_state = "card_mastery"
        # if both 1v1 and 2v2, pick a random one
        if "1v1 battle" in job_list and "2v2 battle" in job_list:
            if logger.get_1v1_fights() < logger.get_2v2_fights():
                return (
                    start_1v1_fight_state(vm_index, logger),
                    account_index_to_switch_to,
                )
            return (
                start_2v2_fight_state(vm_index, logger),
                account_index_to_switch_to,
            )

        # if only 1v1, do 1v1
        if "1v1 battle" in job_list:
            return start_1v1_fight_state(vm_index, logger), account_index_to_switch_to

        # if only 2v2, do 2v2
        if "2v2 battle" in job_list:
            return start_2v2_fight_state(vm_index, logger), account_index_to_switch_to

        # if neither, go to NEXT_STATE
        return next_state, account_index_to_switch_to

    elif state == "2v2_fight":  # --> end_fight
        return do_2v2_fight_state(vm_index, logger), account_index_to_switch_to

    elif state == "1v1_fight":  # --> end_fight
        return do_1v1_fight_state(vm_index, logger), account_index_to_switch_to

    elif state == "end_fight":  # --> card_mastery
        next_state = "card_mastery"
        return end_fight_state(vm_index, logger, next_state), account_index_to_switch_to

    elif state == "card_mastery":  # --> war
        next_state = "war"
        if "card mastery collection" in job_list:
            return (
                card_mastery_collection_state(vm_index, logger, next_state),
                account_index_to_switch_to,
            )
        return next_state, account_index_to_switch_to

    elif state == "war":  # --> account_switch
        next_state = "account_switch"
        if "war" in job_list:
            return war_state(vm_index, logger, next_state), account_index_to_switch_to
        return next_state, account_index_to_switch_to

    elif state == "account_switch":  # --> open_chests
        next_state = "open_chests"
        if "account_switch" in job_list and len(account_switch_order) > 1:
            return (
                switch_account_state(
                    vm_index, logger, account_index_to_switch_to, account_switch_order
                ),
                account_index_to_switch_to,
            )
        return next_state, account_index_to_switch_to

    print("Failure in state tree")
    return None, None


if __name__ == "__main__":
    pass
