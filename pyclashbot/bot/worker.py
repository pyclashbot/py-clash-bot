import traceback
from multiprocessing import Event, Process, Queue
from typing import Any

from pyclashbot.bot.states import StateHistory, StateOrder, state_tree
from pyclashbot.emulators import EmulatorType, get_emulator_registry
from pyclashbot.interface.enums import UIField
from pyclashbot.utils.cancellation import CancellationToken
from pyclashbot.utils.logger import ProcessLogger
from pyclashbot.utils.platform import is_macos


class WorkerProcess(Process):
    """Worker process for running the bot.

    Uses multiprocessing instead of threading for reliable force termination.
    Communicates stats back to main process via Queue.
    """

    def __init__(
        self,
        jobs: dict[str, Any],
        stats_queue: Queue,
        shutdown_event: Event,
    ) -> None:
        super().__init__(daemon=True)
        self.jobs = jobs
        self.stats_queue = stats_queue
        self.shutdown_event = shutdown_event

    def _setup_emulator(self, jobs: dict[str, Any], logger: ProcessLogger):
        """Set up the appropriate emulator based on job configuration."""
        emulator_selection = jobs.get("emulator", EmulatorType.MEMU)
        registry = get_emulator_registry()

        if emulator_selection not in registry:
            print(f"[!] Fatal error: Emulator {emulator_selection} is not supported on this platform!")
            logger.change_status(f"Emulator {emulator_selection} is not available on this platform.")
            return None

        controller_class = registry[emulator_selection]

        try:
            if emulator_selection == EmulatorType.GOOGLE_PLAY:
                print("Creating Google Play emulator")
                gp_device_serial = jobs.get(UIField.GP_DEVICE_SERIAL.value) or None
                return controller_class(device_serial=gp_device_serial)

            elif emulator_selection == EmulatorType.BLUESTACKS:
                print("Creating BlueStacks 5 emulator")
                # Default: Vulkan on macOS, OpenGL on Windows
                default_mode = "vlcn" if is_macos() else "gl"
                bs_mode = jobs.get("bluestacks_render_mode", default_mode)
                render_settings = {"graphics_renderer": bs_mode}
                bs_device_serial = jobs.get(UIField.BS_DEVICE_SERIAL.value) or None
                return controller_class(
                    render_settings=render_settings,
                    device_serial=bs_device_serial,
                    action_callback=logger.show_temporary_action,
                )

            elif emulator_selection == EmulatorType.MEMU:
                print("Creating MEmu emulator")
                from pyclashbot.emulators.memu import verify_memu_installation

                if not verify_memu_installation():
                    logger.change_status("MEmu is not installed! Please install it to use MEmu Emulator Mode")
                    return None
                render_mode = jobs.get("memu_render_mode", "opengl")
                return controller_class(
                    render_mode=render_mode,
                    action_callback=logger.show_temporary_action,
                )

            elif emulator_selection == EmulatorType.ADB:
                print("Creating ADB Device controller")
                adb_serial = jobs.get(UIField.ADB_SERIAL.value) or None
                return controller_class(
                    device_serial=adb_serial,
                    action_callback=logger.show_temporary_action,
                )

        except Exception as e:
            print(f"Failed to create {emulator_selection} emulator: {e}")
            logger.change_status(f"Failed to start {emulator_selection}. Verify its installation!")
            return None

        return None

    def _run_bot_loop(self, emulator, jobs: dict[str, Any], logger: ProcessLogger) -> None:
        """Run the main bot state loop."""
        state = "start"
        state_history = StateHistory(logger)
        state_order = StateOrder()
        consecutive_restarts = 0
        max_consecutive_restarts = 5

        while not self.shutdown_event.is_set():
            try:
                new_state = state_tree(emulator, logger, state, jobs, state_history, state_order)

                # Check for restart loops
                if new_state == "restart":
                    consecutive_restarts += 1
                    if consecutive_restarts >= max_consecutive_restarts:
                        logger.error(
                            f"Too many consecutive restarts ({consecutive_restarts}) - stopping bot to prevent infinite loop"
                        )
                        break
                    logger.log(f"Restart #{consecutive_restarts} - attempting to recover")
                else:
                    consecutive_restarts = 0  # Reset counter on successful state

                # Check for error states that should stop execution
                if new_state in ["fail", None]:
                    logger.error(f"Critical error: state_tree returned '{new_state}' - stopping bot")
                    if new_state == "fail":
                        logger.add_restart_after_failure()
                    break

                state = new_state

            except Exception as e:
                logger.error(f"Exception in state_tree: {e}")
                logger.log(f"Current state was: {state}")
                print(f"[ERROR] Exception in state_tree: {e}")
                print(f"[ERROR] Current state was: {state}")
                # Try to restart from a known state
                state = "restart"
                # If we keep getting exceptions, break out
                traceback.print_exc()
                consecutive_restarts += 1
                if consecutive_restarts >= max_consecutive_restarts:
                    logger.error("Too many consecutive exceptions - stopping bot")
                    break

            # Note: Pause functionality removed in multiprocessing version
            # If pause is needed, use a separate mp.Event

    def run(self) -> None:
        """Main worker process execution."""
        print("WorkerProcess run()...")

        # Set up cancellation token for interruptible sleeps
        token = CancellationToken(self.shutdown_event)
        CancellationToken.set_current(token)

        # Create logger that sends stats through queue
        logger = ProcessLogger(self.stats_queue)

        try:
            emulator = self._setup_emulator(self.jobs, logger)
            if emulator is None:
                return

            self._run_bot_loop(emulator, self.jobs, logger)
        except Exception as err:
            logger.error(str(err))
            traceback.print_exc()
        finally:
            CancellationToken.set_current(None)
            logger.change_status("Bot stopped")
