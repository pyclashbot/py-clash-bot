import time

from pyclashbot.bot.states import state_tree
from pyclashbot.utils import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None):
        super().__init__(args, kwargs)
        self.logger = logger

    def run(self):
        try:
            jobs, ssid_max = self.args  # parse thread args
            ssid = 0  # start ssid at 0
            state = "intro"
            ssid_order_list = None

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # perform state transition
                (state, ssid, ssid_order_list) = state_tree(
                    jobs, self.logger, ssid_max, ssid, state, ssid_order_list
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
