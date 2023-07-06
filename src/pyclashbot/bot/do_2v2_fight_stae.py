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

    logger.add_1v1_fight()
    return NEXT_STATE


def _2v2_fight_loop(vm_index, logger):
    pass


def wait_for_2v2_battle_start(vm_index, logger):
    pass
