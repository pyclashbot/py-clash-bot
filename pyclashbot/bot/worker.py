import time

from pyclashbot.bot.states import StateHistory, state_tree
from pyclashbot.memu.launcher import get_vm
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def run(self) -> None:
        # parse render mode out of jobs
        jobs = self.args  # parse thread args
        render_mode = "opengl"
        if jobs["directx_toggle"] is True:
            render_mode = "directx"

        try:
            #init start state
            state = "start"

            #init state manager object
            state_history = StateHistory(self.logger)

            #init the vm
            vm_index = get_vm(self.logger, render_mode=render_mode)

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # code to run
                state: str | tuple[None, None] = state_tree(
                    vm_index,
                    self.logger,
                    state,
                    jobs,
                    state_history
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
