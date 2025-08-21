import time

from pyclashbot.bot.states import StateHistory, state_tree, StateOrder
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled
from pyclashbot.emulators.memu import MemuEmulatorController, verify_memu_installation
from pyclashbot.emulators.google_play import GooglePlayEmulatorController


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def _create_google_play_emulator(self):
        """Create and return a Google Play emulator instance."""
        try:
            emulator = GooglePlayEmulatorController()
            print('Successfully created google play emulator')
            return emulator
        except Exception as e:
            print(f'Failed to create Google Play emulator: {e}')
            self.logger.change_status("Failed to start Google Play. Verify its installation!")
            return None

    def _create_memu_emulator(self, render_mode):
        """Create and return a MEmu emulator instance."""
        if not verify_memu_installation():
            self.logger.change_status('Memu is not installed! Please install it to use Memu Emulator Mode')
            return None
        
        return MemuEmulatorController(render_mode)

    def _setup_emulator(self, jobs):
        """Set up the appropriate emulator based on job configuration."""
        emulator_selection = jobs.get("emulator", "MEmu")
        
        if emulator_selection == "Google Play":
            print('Creating google play emulator')
            return self._create_google_play_emulator()
        elif emulator_selection == "MEmu":
            render_mode = jobs.get("memu_render_mode", "opengl")
            return self._create_memu_emulator(render_mode)
        else:
            print(f"[!] Fatal error: Emulator {emulator_selection} is not supported!")
            return None

    def _run_bot_loop(self, emulator, jobs):
        """Run the main bot state loop."""
        state = "start"
        state_history = StateHistory(self.logger)
        state_order = StateOrder()

        while not self.shutdown_flag.is_set():
            state = state_tree(
                emulator, self.logger, state, jobs, state_history, state_order
            )
            while self.pause_flag.is_set():
                time.sleep(0.33)

    def run(self) -> None:
        """Main worker thread execution."""
        print("WorkerThread run()...")
        jobs = self.args
        
        emulator = self._setup_emulator(jobs)
        if emulator is None:
            return

        try:
            self._run_bot_loop(emulator, jobs)
        except ThreadKilled:
            return
        except Exception as err:
            self.logger.error(str(err))
