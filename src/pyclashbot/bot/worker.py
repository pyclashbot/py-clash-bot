import time

from pyclashbot.bot.states import StateHistory, state_tree
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled
from pyclashbot.bot.google_play_emulator import gpe


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def run(self) -> None:
        jobs = self.args


        gpe.connect()
        print(f'Workerthread connected to google play emulator: {gpe.is_connected()}')

        try:
            state = "start"

            state_history = StateHistory(self.logger)

            while not self.shutdown_flag.is_set():
                # code to run
                state: str | tuple[None, None] = state_tree(
                    self.logger, state, jobs, state_history
                )
                while self.pause_flag.is_set():
                    time.sleep(0.1)

        except ThreadKilled:
            return

        except Exception as err:
            self.logger.error(str(err))


if __name__ == "__main__":
    pass
