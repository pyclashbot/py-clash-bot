"""time module for timing functions and controling pacing"""

import time
from pyclashbot.bot.account_switching import switch_accounts
from pyclashbot.bot.bannerbox import collect_bannerbox_rewards_state
from pyclashbot.bot.donate import donate_cards_state
from pyclashbot.bot.card_mastery_state import card_mastery_state
from pyclashbot.bot.deck_randomization import randomize_deck_state
from pyclashbot.bot.do_fight_state import (
    do_1v1_fight_state,
    do_2v2_fight_state,
    end_fight_state,
    start_1v1_fight_state,
    start_2v2_fight_state,
)
from pyclashbot.bot.level_up_chest import collect_level_up_chest_state
from pyclashbot.bot.nav import check_if_on_clash_main_menu, check_if_in_battle_at_start
from pyclashbot.bot.open_chests_state import get_chest_statuses, open_chests_state
from pyclashbot.bot.request_state import request_state
from pyclashbot.bot.trophy_road_rewards import collect_trophy_road_rewards_state
from pyclashbot.bot.upgrade_all_cards import upgrade_all_cards_state
from pyclashbot.bot.upgrade_state import upgrade_cards_state
from pyclashbot.bot.battlepass import collect_battlepass_state
from pyclashbot.bot.war_state import war_state
from pyclashbot.memu.launcher import (
    close_clash_royale_app,
    restart_emulator,
    start_clash_royale,
)
from pyclashbot.bot.buy_shop_offers import buy_shop_offers_state
from pyclashbot.utils.logger import Logger
from pyclashbot.bot.daily_challenge_collection import collect_daily_rewards_state
from pyclashbot.memu.client import click
from pyclashbot.memu.docker import start_memu_dock_mode

mode_used_in_1v1 = None


def state_tree(
    vm_index,
    logger: Logger,
    state,
    job_list,
) -> str:
    """method to handle and loop between the various states of the bot"""
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

        logger.set_total_accounts(len(job_list["random_account_switch_list"]))

        next_state = "account_switch"

        restart_emulator(logger)

        logger.log(
            f"Emulator boot sequence took {str(time.time() - start_time)[:5]} seconds"
        )
        return next_state

    if state == "restart":  # --> account_switch
        next_state = "account_switch"

        logger.log("Entered the restart state after a failure in another state...")

        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # print("Bot is in restart state. Press enter to continue!!!!!!")
        # input()

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
        logger.change_status("Waiting for CR main menu")
        clash_main_wait_start_time = time.time()
        clash_main_wait_timeout = 240  # s
        time.sleep(12)
        while time.time() - clash_main_wait_start_time < clash_main_wait_timeout:
            clash_main_check = check_if_on_clash_main_menu(vm_index)
            if clash_main_check is True:
                break
            # Check if a battle is detected at start
            battle_start_result = check_if_in_battle_at_start(vm_index, logger)
            if battle_start_result == "good":
                break  # Successfully handled starting battle or end-of-battle scenario
            elif battle_start_result == "restart":
                # Need to restart the process due to issues detected
                return "restart"

            # click deadspace
            click(vm_index, 5, 350)

            logger.log("Not on clash main")
            logger.log("Pixels are: ")
            for p in clash_main_check:
                logger.log(p)

        if clash_main_check is not True:
            logger.log("Clash main wait timed out! These are the pixels it saw:")
            for p in clash_main_check:
                logger.log(p)
            return "restart"

        logger.log('Detected clash main at the end of "restart" state.')
        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]}seconds"
        )
        logger.log(f"Next state is {next_state}")

        return next_state

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

        account_total = job_list["account_switching_slider"]
        logger.log(f"Doing switch #{job_list['next_account']} of {account_total}")

        accout_index = job_list["next_account"]

        if (
            switch_accounts(
                vm_index, logger, job_list["random_account_switch_list"][accout_index]
            )
            is False
        ):
            return "restart"

        # increment next account iteration
        job_list["next_account"] += 1
        if job_list["next_account"] >= job_list["account_switching_slider"]:
            job_list["next_account"] = 0

        logger.log(
            f"Next account is {job_list['next_account']} / {job_list['account_switching_slider']}"
        )

        # update current account # to GUI
        logger.change_current_account(
            job_list["random_account_switch_list"][accout_index]
        )

        return next_state

    if state == "open_chests":  # --> level_up_chest
        next_state = "level_up_chest"

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

        # if job not ready, skip this state
        logger.log('Checking if "open_chests_increment_user_input" is ready')
        if not logger.check_if_can_collect_level_up_chest(
            job_list["level_up_chest_increment_user_input"]
        ):
            logger.log("Can't open level up chest at this time, skipping this state")
            return next_state

        # run this state
        logger.log(
            'Level up chests is toggled and ready. Running "collect_level_up_chest_state()"'
        )
        return collect_level_up_chest_state(vm_index, logger, next_state)

    if state == "randomize_deck":  # --> upgrade
        next_state = "upgrade"

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

    if state == "upgrade":  # --> upgrade_all
        next_state = "upgrade_all"

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

    if state == "upgrade_all":  # --> trophy_rewards
        next_state = "trophy_rewards"

        # if 'upgrade_user_toggle' is toggled on, return next state
        if job_list["upgrade_user_toggle"]:
            logger.change_status(
                "Regular upgrade is toggled. Skipping 'UPGRADE ALL' state"
            )
            return next_state

        # if job isnt selected, just return the next state
        if not job_list["upgrade_all_cards_user_toggle"]:
            logger.change_status(
                "Upgrade all cards is not toggled. Skipping this state"
            )
            return next_state

        # if job is available, increment attempts, run the state
        if logger.check_if_can_card_upgrade():
            logger.change_status("Upgrade all cards is ready!")
            logger.add_card_upgrade_attempt()
            return upgrade_all_cards_state(vm_index, logger, next_state)

        # else just return next state
        logger.change_status("Upgrade all cards isn't ready!")
        return next_state

    if state == "trophy_rewards":  # --> request
        next_state = "request"

        # if job isnt selected, just return the next state
        if not job_list["trophy_road_rewards_user_toggle"]:
            logger.change_status(
                "Trophy rewards collection is not toggled. Skipping this state"
            )
            return next_state

        # if job is available, increment attempts, run the state
        if logger.check_if_can_collect_trophy_road_rewards(
            job_list["trophy_road_reward_increment_user_input"]
        ):
            logger.change_status("Trophy rewards collection is ready!")
            logger.add_trophy_reward_collect_attempt()
            return collect_trophy_road_rewards_state(vm_index, logger, next_state)

        # else just return next state
        logger.change_status("Trophy rewards collection isn't ready!")

        return next_state

    if state == "request":  # --> donate
        next_state = "donate"

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

    if state == "donate":  # --> shop_buy
        next_state = "shop_buy"

        # if job not selected, return next state
        if not job_list["donate_toggle"]:
            logger.log("Donate job isn't toggled. Skipping")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_donate(job_list["donate_increment_user_input"]):
            logger.log("Donate job isn't ready. Skipping")
            return next_state

        # return output of this state
        return donate_cards_state(vm_index, logger, next_state)

    if state == "shop_buy":  # --> bannerbox
        next_state = "bannerbox"

        # if job not selected, return next state
        if (
            not job_list["free_offer_user_toggle"]
            and not job_list["gold_offer_user_toggle"]
        ):
            logger.log("Free neither free, not gold offer buys toggled")
            return next_state

        # if job not ready, reutrn next state
        if not logger.check_if_can_shop_buy(job_list["shop_buy_increment_user_input"]):
            logger.log("Free shop_buy isn't ready")
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
        if not job_list["open_bannerbox_user_toggle"]:
            logger.log("Bannerbox job isn't toggled. Skipping")
            return next_state

        return collect_bannerbox_rewards_state(vm_index, logger, next_state)

    if state == "daily_rewards":  # --> battlepass_rewards
        next_state = "battlepass_rewards"

        # if job not toggled, return next state
        if not job_list["daily_rewards_user_toggle"]:
            logger.log("daily_rewards job isn't toggled. Skipping")
            return next_state

        # if job not ready, return next state
        if not logger.check_if_can_collect_daily_rewards(
            job_list["daily_reward_increment_user_input"]
        ):
            logger.log("daily_rewards job isn't ready")
            return next_state

        # run this job, return its output
        return collect_daily_rewards_state(vm_index, logger, next_state)

    if state == "battlepass_rewards":  # --> card_mastery
        next_state = "card_mastery"

        if not job_list["battlepass_collect_user_toggle"]:
            logger.change_status(
                "Battlepass collect is not toggled. Skipping this state"
            )
            return next_state

        if not logger.check_if_can_battlepass_collect(
            job_list["battlepass_collect_increment_user_input"]
        ):
            logger.change_status("Battlepass collect is not ready. Skipping this state")
            return next_state

        return collect_battlepass_state(vm_index, logger, next_state)

    if state == "card_mastery":  # --> start_fight
        next_state = "start_fight"

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
        return card_mastery_state(vm_index, logger, next_state)

    if state == "start_fight":  # --> 1v1_fight, war
        next_state = "war"

        _1v1_toggle = (
            job_list["trophy_road_1v1_battle_user_toggle"]
            or job_list["path_of_legends_1v1_battle_user_toggle"]
        )
        _2v2_toggle = job_list["2v2_battle_user_toggle"]

        trophy_road_toggle = job_list["trophy_road_1v1_battle_user_toggle"]
        path_of_legends_toggle = job_list["path_of_legends_1v1_battle_user_toggle"]

        fight_mode = "trophy_road"
        if _1v1_toggle:
            if trophy_road_toggle and path_of_legends_toggle:
                fight_mode = "both"
            elif path_of_legends_toggle:
                fight_mode = "path_of_legends"

        # if all chests slots are taken, skip starting a battle
        if job_list["skip_fight_if_full_chests_user_toggle"]:
            if all(
                chest_status == "available"
                for chest_status in get_chest_statuses(vm_index)
            ):
                logger.change_status("All chests are available, skipping fight state")
                return next_state

        # if both are toggled, choose the lest used fight type
        if _1v1_toggle and _2v2_toggle:
            logger.log("Both 1v1 and 2v2 are selected. Choosing the less used one")
            if logger.get_1v1_fights() < logger.get_2v2_fights():
                next_1v1_state, mode_used_in_1v1 = start_1v1_fight_state(
                    vm_index, logger, mode=fight_mode
                )
                return next_1v1_state

            return start_2v2_fight_state(vm_index, logger)

        # if only 1v1 is toggled
        elif _1v1_toggle:
            logger.log("1v1 is toggled")
            trophy_road_toggle = job_list["trophy_road_1v1_battle_user_toggle"]
            path_of_legends_toggle = job_list["path_of_legends_1v1_battle_user_toggle"]

            print(f"trophy_road_toggle is {trophy_road_toggle}")
            print(f"path_of_legends_toggle is {path_of_legends_toggle}")

            print(f"Fight mode is gonna be: {fight_mode}")
            next_1v1_state, mode_used_in_1v1 = start_1v1_fight_state(
                vm_index, logger, mode=fight_mode
            )
            print(f"Fight mode is : {mode_used_in_1v1}")
            return next_1v1_state

        # if only 2v2 is toggled
        elif _2v2_toggle:
            logger.log("2v2 is toggled")
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
        print(f"Random fight mode is {random_fight_mode} in state == '1v1_fight'")

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        print(f"Fight mode is {mode_used_in_1v1}")
        return do_1v1_fight_state(
            vm_index, logger, next_state, random_fight_mode, mode_used_in_1v1, False
        )

    if state == "end_fight":  # --> war
        next_state = "war"

        logger.log(
            f"This state: {state} took {str(time.time() - start_time)[:5]} seconds"
        )
        return end_fight_state(
            vm_index, logger, next_state, job_list["disable_win_track_toggle"]
        )

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

    logger.error("Failure in state tree")
    return "fail"


def clip_that():
    import pyautogui
    pyautogui.click(860,1197)
    time.sleep(1)


def state_tree_tester(vm_index):
    logger = Logger()
    state = "account_switch"
    job_list = {
        # job toggles
        "open_battlepass_user_toggle": True,
        "open_chests_user_toggle": True,
        "request_user_toggle": True,
        "donate_toggle": True,
        "card_mastery_user_toggle": True,
        "free_offer_user_toggle": True,
        "gold_offer_user_toggle": True,
        "trophy_road_1v1_battle_user_toggle": False,
        "path_of_legends_1v1_battle_user_toggle": True,
        "2v2_battle_user_toggle": True,
        "upgrade_user_toggle": True,
        "war_user_toggle": True,
        "random_decks_user_toggle": True,
        "open_bannerbox_user_toggle": True,
        "daily_rewards_user_toggle": True,
        "battlepass_collect_user_toggle": True,
        "level_up_chest_user_toggle": True,
        "upgrade_all_cards_user_toggle": True,
        "trophy_road_rewards_user_toggle": True,
        # keep these off
        "disable_win_track_toggle": True,
        "skip_fight_if_full_chests_user_toggle": True,
        "random_plays_user_toggle": True,
        "memu_attach_mode_toggle": True,
        # job increments
        "card_upgrade_increment_user_input": 1,
        "shop_buy_increment_user_input": 1,
        "request_increment_user_input": 1,
        "donate_increment_user_input": 1,
        "daily_reward_increment_user_input": 1,
        "card_mastery_collect_increment_user_input": 1,
        "open_chests_increment_user_input": 1,
        "deck_randomization_increment_user_input": 1,
        "war_attack_increment_user_input": 1,
        "battlepass_collect_increment_user_input": 1,
        "level_up_chest_increment_user_input": 1,
        "trophy_road_reward_increment_user_input": 1,
        # account switching input info
        "account_switching_increment_user_input": 1,
        "account_switching_toggle": False,
        "account_switching_slider": 1,
        "next_account": 0,
        "random_account_switch_list": [0],
    }

    while 1:
        state = state_tree(
            vm_index,
            logger,
            state,
            job_list,
        )
        if state == 'restart':
            print('Restart state')
            print('Clipping that')
            clip_that()


if __name__ == "__main__":
    # state_tree_tester(12)
    clip_that()
