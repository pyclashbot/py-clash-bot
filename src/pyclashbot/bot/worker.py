import random
import time
from typing import Any

from pyclashbot.bot.states import state_tree
from pyclashbot.memu.launcher import check_for_vm
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def run(self) -> None:
        try:
            jobs = self.args  # parse thread args
            # logger = Logger()
            state = "start"

            vm_index = check_for_vm(self.logger)

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # code to run
                state: str | tuple[None, None] = state_tree(
                    vm_index,
                    self.logger,
                    state,
                    jobs,
                )

                while self.pause_flag.is_set():
                    time.sleep(0.1)  # sleep for 100ms until pause flag is unset

        except ThreadKilled:
            # normal shutdown
            return

        except Exception as err:  # pylint: disable=broad-except
            # we don't want the thread to crash the interface so we catch all exceptions and log
            # raise e
            self.logger.error(str(err))
