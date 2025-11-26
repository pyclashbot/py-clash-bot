import time
import traceback

from pyclashbot.bot.states import StateHistory, StateOrder, state_tree
from pyclashbot.emulators import EmulatorType, get_emulator_registry
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.platform import is_macos
from pyclashbot.utils.thread import PausableThread, ThreadKilled


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def _setup_emulator(self, jobs):
        """Set up the appropriate emulator based on job configuration."""
        emulator_selection = jobs.get("emulator", EmulatorType.MEMU)
        registry = get_emulator_registry()

        if emulator_selection not in registry:
            print(f"[!] Fatal error: Emulator {emulator_selection} is not supported on this platform!")
            self.logger.change_status(f"Emulator {emulator_selection} is not available on this platform.")
            return None

        controller_class = registry[emulator_selection]

        try:
            if emulator_selection == EmulatorType.GOOGLE_PLAY:
                print("Creating Google Play emulator")
                return controller_class(logger=self.logger)

            elif emulator_selection == EmulatorType.BLUESTACKS:
                print("Creating BlueStacks 5 emulator")
                # Default: Vulkan on macOS, OpenGL on Windows
                default_mode = "vlcn" if is_macos() else "gl"
                bs_mode = jobs.get("bluestacks_render_mode", default_mode)
                render_settings = {"graphics_renderer": bs_mode}
                return controller_class(logger=self.logger, render_settings=render_settings)

            elif emulator_selection == EmulatorType.MEMU:
                print("Creating MEmu emulator")
                from pyclashbot.emulators.memu import verify_memu_installation

                if not verify_memu_installation():
                    self.logger.change_status("MEmu is not installed! Please install it to use MEmu Emulator Mode")
                    return None
                render_mode = jobs.get("memu_render_mode", "opengl")
                return controller_class(self.logger, render_mode)

            elif emulator_selection == EmulatorType.ADB:
                print("Creating ADB Device controller")
                adb_serial = jobs.get("adb_serial", None)
                return controller_class(logger=self.logger, device_serial=adb_serial)

        except Exception as e:
            print(f"Failed to create {emulator_selection} emulator: {e}")
            self.logger.change_status(f"Failed to start {emulator_selection}. Verify its installation!")
            return None

        return None

    def _run_bot_loop(self, emulator, jobs):
        """Run the main bot state loop."""
        state = "start"
        state_history = StateHistory(self.logger)
        state_order = StateOrder()
        consecutive_restarts = 0
        max_consecutive_restarts = 5

        while not self.shutdown_flag.is_set():
            try:
                new_state = state_tree(emulator, self.logger, state, jobs, state_history, state_order)

                # Check for restart loops
                if new_state == "restart":
                    consecutive_restarts += 1
                    if consecutive_restarts >= max_consecutive_restarts:
                        self.logger.error(
                            f"Too many consecutive restarts ({consecutive_restarts}) - stopping bot to prevent infinite loop"
                        )
                        break
                    self.logger.log(f"Restart #{consecutive_restarts} - attempting to recover")
                else:
                    consecutive_restarts = 0  # Reset counter on successful state

                # Check for error states that should stop execution
                if new_state in ["fail", None]:
                    self.logger.error(f"Critical error: state_tree returned '{new_state}' - stopping bot")
                    if new_state == "fail":
                        self.logger.add_restart_after_failure()
                    break

                state = new_state

            except Exception as e:
                self.logger.error(f"Exception in state_tree: {e}")
                self.logger.log(f"Current state was: {state}")
                print(f"[ERROR] Exception in state_tree: {e}")
                print(f"[ERROR] Current state was: {state}")
                # Try to restart from a known state
                state = "restart"
                # If we keep getting exceptions, break out
                traceback.print_exc()
                consecutive_restarts += 1
                if consecutive_restarts >= max_consecutive_restarts:
                    self.logger.error("Too many consecutive exceptions - stopping bot")
                    break

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
