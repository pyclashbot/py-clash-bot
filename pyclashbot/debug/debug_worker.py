import time

from pyclashbot.bot.states import detect_state, state_tree
from pyclashbot.utils import Logger
from pyclashbot.utils.thread import PausableThread


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None):
        super().__init__(args, kwargs)
        self.logger = logger

    def run(self):
        try:
            jobs, ssid_max = self.args  # parse thread args
            ssid = 0  # start ssid at 0
            state = "restart"

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # perform state transition
                (state, ssid) = state_tree(jobs, self.logger, ssid_max, ssid, state)
                while self.pause_flag.is_set():
                    time.sleep(0.1)  # sleep for 100ms until pause flag is unset
        except Exception as e:  # pylint: disable=broad-except
            # we don't want the thread to crash the interface so we catch all exceptions and log
            # raise e
            self.logger.error(str(e))
