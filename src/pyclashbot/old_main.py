from bot.states import (
    state_tree,
)
from memu.client import screenshot
from memu.emulator import get_vm_index
from memu.launcher import EMULATOR_NAME
from utils.logger import Logger


def main():
    logger = Logger()
    job_list = [
        "1v1",
        "request",
        "upgrade",
        "free_offer",
    ]

    state = "start"

    # while 1:
    #     state = state_tree(get_vm_index(logger, EMULATOR_NAME), logger, state, job_list,account_index_to_switch_to)


def dummy_main(vm_index, logger: Logger):
    pass

    screenshot(vm_index)


if __name__ == "__main__":
    main()
