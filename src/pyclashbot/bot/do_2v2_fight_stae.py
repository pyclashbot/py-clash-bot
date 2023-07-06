from pyclashbot.utils.logger import Logger


def do_2v2_fight_state(vm_index, logger: Logger):
    NEXT_STATE = "end_fight_2v2"

    logger.change_status("do_2v2_fight_state state")
    logger.change_status("waiting for 2v2 battle start")

    # wait for 2v2 battle start
    if wait_for_2v2_battle_start(vm_index, logger) == "restart":
        logger.change_status(
            "Error 374736 wait_for_2v2_battle_start() in do_2v2_fight_state()"
        )
        return "restart"

    logger.change_status("2v2 Battle started!")

    logger.change_status("Starting 2v2 fight loop")
    if _2v2_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 222267245 Failuring in fight loop")
        return "restart"

    logger.add_2v2_fight()
    return NEXT_STATE


def _2v2_fight_loop(vm_index, logger):
    logger.change_status("Starting battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0

    # while in battle:
    while check_for_in_1v1_battle(vm_index):
        logger.log(f"Battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        elixer_wait_return = wait_for_6_elixer(vm_index, logger)

        if elixer_wait_return == "restart":
            logger.change_status("Error 788455 wait_for_6_elixer() in fight_loop()")
            return "restart"

        elif elixer_wait_return == "no battle":
            break

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.log(f"Clicking card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        this_play_side = choose_play_side(vm_index, favorite_side)

        # get a coord based on the selected side
        id, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            continue

        id_string = "Regular card"
        if id != "Unknown":
            id_string = id
        logger.change_status(f"Playing card: {id_string} on {this_play_side} side")

        # click that random card coord
        random_card_coord = HAND_CARDS_COORDS[random_card_index]
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(0.1)

        # click that play coord
        click(vm_index, play_coord[0], play_coord[1])
        logger.add_card_played()
        time.sleep(0.1)

        # increment plays counter
        plays += 1


def wait_for_2v2_battle_start(vm_index, logger):
    pass
