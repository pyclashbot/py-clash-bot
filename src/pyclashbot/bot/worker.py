import time

from bot.states import state_tree
from memu.launcher import check_for_vm
from utils.logger import Logger
from utils.thread import PausableThread, ThreadKilled
import random


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None):
        super().__init__(args, kwargs)
        self.logger = logger

    def run(self):
        try:
            jobs, ssid_max = self.args  # parse thread args
            # logger = Logger()
            account_switch_order = self.make_account_switch_order(ssid_max)
            state = "start"

            vm_index = check_for_vm(self.logger)
            account_index_to_switch_to = account_switch_order[0]

            # loop until shutdown flag is set
            while not self.shutdown_flag.is_set():
                # code to run
                state, account_index_to_switch_to = state_tree(
                    vm_index,
                    self.logger,
                    state,
                    jobs,
                    account_index_to_switch_to,
                    account_switch_order,
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

    def make_account_switch_order(self, account_count):
        # Generate a list of numbers from 0 to account_count - 1
        account_numbers = list(range(account_count))
        # Shuffle the list randomly
        random.shuffle(account_numbers)
        # Pad the list with zeros up to length 4
        account_numbers += [0] * (4 - account_count)
        return account_numbers
