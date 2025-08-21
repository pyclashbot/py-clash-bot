import time

from pyclashbot.bot.states import StateHistory, state_tree, StateOrder
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled
from pyclashbot.emulators.memu import MemuEmulatorController,verify_memu_installation
from pyclashbot.emulators.google_play import GooglePlayEmulatorController


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def run(self) -> None:
        print(f"Workerthread run()...")
        # parse render mode out of jobs
        jobs = self.args  # parse thread args
        emulator_selection = jobs.get("emulator", "memu")

        # set up the emulator of choice
        emulator = None
        if emulator_selection == "Google Play":
            # Set up Google Play emulator
            print('Creating google play emulator')
            try:
                emulator = GooglePlayEmulatorController()
                print('Successfully created google play emulator')
            except Exception as e:
                print(f'Failed to create Google Play emulator: {e}')
                self.logger.change_status(f"Failed to start Google Play. Verify its installation!")
                return

        elif emulator_selection == "MEmu":
            # Verifying MEmu emulator
            if not verify_memu_installation():
                self.logger.change_status('Memu is not installed! Please install it to use Memu Emulator Mode')
                return
           
            # Set up MEmu emulator
            render_mode = jobs.get("memu_render_mode", "opengl")
            emulator = MemuEmulatorController(render_mode)

        # handle bad emulator selection
        if emulator is None:
            print(
                f"[!] Fatal error: Emulator {emulator_selection} is not supported!\nKilling worker thread..."
            )
            return None

        # run state tree loop with that emulator
        try:

            state = "start"
            state_history = StateHistory(self.logger)
            state_order = StateOrder()

            while not self.shutdown_flag.is_set():
                state = state_tree(
                    emulator, self.logger, state, jobs, state_history, state_order
                )
                while self.pause_flag.is_set():
                    time.sleep(0.33)

        except ThreadKilled:
            # normal shutdown
            return

        except Exception as err:  # pylint: disable=broad-except
            # we don't want the thread to crash the interface so we catch all exceptions and log
            # raise exception to be handled by the caller
            self.logger.error(str(err))
