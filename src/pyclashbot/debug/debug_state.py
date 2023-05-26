from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.bot.states import (
    state_battlepass_collection,
    state_card_mastery_collection,
    state_clashmain,
    state_endfight,
    state_fight,
    state_free_offer_collection,
    state_level_up_reward_collection,
    state_request,
    state_restart,
    state_startfight,
    state_upgrade,
    state_war,
)


def do_debug_state_tree(logger):
    if not check_if_on_clash_main_menu():
        state_restart(logger)
    jobs = [
        "Open Chests",
        "Fight",
        "Request",
        "Upgrade",
        "Randomize Deck",
        "card mastery collection",
        "level up reward collection",
        "battlepass reward collection",
        "war",
        "free_offer_collection",
    ]
    ssid = 0
    state = "clashmain"
    while True:
        print(state)
        state, ssid = debug_state_tree(
            jobs=jobs, logger=logger, ssid_max=4, ssid=ssid, state=state
        )


def debug_state_tree(logger, ssid_max, jobs, ssid, state):

    if state == "clashmain":

        state = state_clashmain(
            logger=logger, ssid_max=ssid_max, account_number=ssid, jobs=jobs
        )

        # Increment account number, loop back to 0 if it's ssid_max
        ssid = ssid + 1 if ssid < ssid_max else 0

    elif state == "startfight":
        print("state==startfight")
        state = (
            state_startfight(logger, random_deck="Randomize Deck" in jobs)
            if "Fight" in jobs
            else "upgrade"
        )

    elif state == "fighting":
        print("state==fighting")
        state = state_fight(logger)

    elif state == "endfight":
        print("state==endfight")
        state = state_endfight(logger)

    elif state == "upgrade":
        print("state==upgrade")
        state = (
            state_upgrade(logger) if "Upgrade" in jobs else "card mastery collection"
        )

    elif state == "request":
        print("state==request")
        state = (
            state_request(logger) if "Request" in jobs else "level up reward collection"
        )

    elif state == "restart":
        print("state==restart")
        state = state_restart(logger)

    elif state == "card mastery collection":
        print("state==mastery")
        state = (
            state_card_mastery_collection(logger)
            if "card mastery collection" in jobs
            else "request"
        )

    elif state == "level up reward collection":
        print("state==level up reward collection")
        state = (
            state_level_up_reward_collection(logger)
            if "level up reward collection" in jobs
            else "battlepass reward collection"
        )

    elif state == "battlepass reward collection":
        print("state==battlepass reward collection")
        state = (
            state_battlepass_collection(logger)
            if "battlepass reward collection" in jobs
            else "war"
        )

    elif state == "war":
        print("state==war")
        state = state_war(logger) if "war" in jobs else "free_offer_collection"

    elif state == "free_offer_collection":
        print("state==free_offer_collection")

        if "free_offer_collection" in jobs:
            print("free offer collection is in jobs")
            state = state_free_offer_collection(logger)
        else:
            print("free offer collection not in jobs")
            state = "clashmain"

    return (state, ssid)
