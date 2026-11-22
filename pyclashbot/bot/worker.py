import signal
import traceback
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event
from typing import Any, Protocol

from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.bot.states import StateHistory, StateOrder, state_tree
from pyclashbot.emulators import EmulatorType, get_emulator_registry
from pyclashbot.emulators.base import EmulatorNotReadyError
from pyclashbot.interface.enums import UIField
from pyclashbot.utils.logger import ProcessLogger, attach_worker_file_logging
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
        session_log_path: str,
    ) -> None:
        super().__init__(daemon=True)
        self.jobs = jobs
        self.stats_queue = stats_queue
        self.shutdown_event = shutdown_event
        self.session_log_path = session_log_path

    def _setup_emulator(self, jobs: dict[str, Any], logger: ProcessLogger):
        """Set up the appropriate emulator based on job configuration."""
        emulator_selection = jobs.get("emulator", EmulatorType.MEMU)
        registry = get_emulator_registry()

        if emulator_selection not in registry:
            print(f"[!] Fatal error: Emulator {emulator_selection} is not supported on this platform!")
            logger.change_status(f"Emulator {emulator_selection} is not available on this platform.")
            return None

        controller_class = registry[emulator_selection]

        emu: Any = None
        try:
            if emulator_selection == EmulatorType.GOOGLE_PLAY:
                print("Creating Google Play emulator")
                gp_device_serial = jobs.get(UIField.GP_DEVICE_SERIAL.value) or None
                emu = controller_class(logger=logger, device_serial=gp_device_serial)

            elif emulator_selection == EmulatorType.BLUESTACKS:
                print("Creating BlueStacks 5 emulator")
                # Default: Vulkan on macOS, OpenGL on Windows
                default_mode = "vlcn" if is_macos() else "gl"
                bs_mode = jobs.get("bluestacks_render_mode", default_mode)
                render_settings = {"graphics_renderer": bs_mode}
                bs_device_serial = jobs.get(UIField.BS_DEVICE_SERIAL.value) or None
                emu = controller_class(logger=logger, render_settings=render_settings, device_serial=bs_device_serial)

            elif emulator_selection == EmulatorType.MEMU:
                print("Creating MEmu emulator")
                from pyclashbot.emulators.memu import verify_memu_installation

                if not verify_memu_installation():
                    logger.change_status("MEmu is not installed! Please install it to use MEmu Emulator Mode")
                    return None
                render_mode = jobs.get("memu_render_mode", "opengl")
                emu = controller_class(logger, render_mode)

            elif emulator_selection == EmulatorType.ADB:
                print("Creating ADB Device controller")
                adb_serial = jobs.get(UIField.ADB_SERIAL.value) or None
                emu = controller_class(
                    logger=logger,
                    device_serial=adb_serial,
                    adb_path=jobs.get("adb_path"),
                    adb_server_port=jobs.get("adb_server_port"),
                )

            elif emulator_selection == EmulatorType.EMUCTL:
                print("Creating emuctl controller")
                emuctl_serial = jobs.get(UIField.ADB_SERIAL.value) or None
                emu = controller_class(
                    logger=logger,
                    device_serial=emuctl_serial,
                    adb_path=jobs.get("adb_path"),
                    adb_server_port=jobs.get("adb_server_port"),
                )

            else:
                return None

            # Construction is cheap; restart() boots the emulator and launches Clash.
            # First-boot failure stops the bot — there is no setup retry.
            emu.restart(ready=check_if_on_clash_main_menu)
            return emu

        except EmulatorNotReadyError as e:
            print(f"{emulator_selection} emulator is not ready: {e}")
            logger.change_status(f"{emulator_selection} is not ready — fix it and start the bot again.")
            self._abort_failed_setup(emu, logger)
            return None
        except Exception as e:
            print(f"Failed to create {emulator_selection} emulator: {e}")
            logger.change_status(f"Failed to start {emulator_selection}. Verify its installation!")
            self._abort_failed_setup(emu, logger)
            return None

    @staticmethod
    def _abort_failed_setup(emulator, logger: ProcessLogger) -> None:
        """Best-effort backend cleanup after a failed setup; never masks the original error."""
        if emulator is None:
            return
        try:
            emulator.abort()
        except Exception:
            logger.error("Failed to clean up the emulator after a setup failure")

    def _run_bot_loop(self, emulator, jobs: dict[str, Any], logger: ProcessLogger) -> bool:
        """Run the main bot state loop; return False if it stopped on a failure."""
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
                        return False
                    logger.log(f"Restart #{consecutive_restarts} - attempting to recover")
                else:
                    consecutive_restarts = 0  # Reset counter on successful state

                # Check for error states that should stop execution
                if new_state in ["fail", None]:
                    logger.error(f"Critical error: state_tree returned '{new_state}' - stopping bot")
                    if new_state == "fail":
                        logger.add_restart_after_failure()
                    return False

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
                    return False

            # Note: Pause functionality removed in multiprocessing version
            # If pause is needed, use a separate mp.Event

        return True

    @staticmethod
    def _exit_on_signal(signum: int, _frame: object) -> None:
        """Turn SIGINT/SIGTERM into a clean SystemExit so ``finally`` can restore state."""
        raise SystemExit(128 + signum)

    def run(self) -> None:
        """Main worker process execution.

        Exits non-zero when setup fails or the loop stops on ``fail`` / five
        consecutive restarts, so a supervisor (the headless entry point) can
        report a failed run. Always stops the emulator on the way out so
        adapters can restore device state (e.g. ``wm`` overrides).
        """
        print("WorkerProcess run()...")
        attach_worker_file_logging(self.session_log_path)

        # Create logger that sends stats through queue
        logger = ProcessLogger(self.stats_queue)
        emulator = None

        try:
            emulator = self._setup_emulator(self.jobs, logger)
            if emulator is None:
                raise SystemExit(1)

            # The parent installs its handlers after start(), so the child gets
            # its own; a group signal then still runs the cleanup below.
            signal.signal(signal.SIGINT, self._exit_on_signal)
            signal.signal(signal.SIGTERM, self._exit_on_signal)

            if not self._run_bot_loop(emulator, self.jobs, logger):
                raise SystemExit(1)
        except SystemExit:
            raise
        except Exception as err:
            logger.error(str(err))
            traceback.print_exc()
            raise SystemExit(1) from err
        finally:
            if emulator is not None:
                try:
                    emulator.stop()
                except Exception:
                    logger.error("Failed to stop the emulator cleanly")
                    traceback.print_exc()
            logger.change_status("Bot stopped")


class _StoppableProcess(Protocol):
    """Structural interface for the process-lifecycle methods ``stop_worker_process`` needs.

    Satisfied by ``multiprocessing.Process`` (and ``WorkerProcess``), spawned context
    processes, and test fakes alike — so the helper depends on the contract, not the
    concrete class.
    """

    def is_alive(self) -> bool: ...
    def terminate(self) -> None: ...
    def join(self, timeout: float | None = ...) -> None: ...
    def kill(self) -> None: ...


class _Signal(Protocol):
    """Structural interface for the shutdown event — only ``set()`` is used here."""

    def set(self) -> None: ...


def stop_worker_process(
    process: _StoppableProcess | None,
    shutdown_event: _Signal | None = None,
    *,
    graceful_timeout: float = 2.0,
) -> None:
    """Stop the worker process via OS-level termination.

    Signals shutdown (belt-and-suspenders), then terminates and hard-kills if the
    process does not exit within ``graceful_timeout``. The OS interrupts any blocking
    call in the worker (sleeps, ADB/socket waits), so this does not depend on the
    worker cooperatively noticing the shutdown event.
    """
    if shutdown_event is not None:
        shutdown_event.set()
    if process is None or not process.is_alive():
        return
    try:
        process.terminate()  # SIGTERM / TerminateProcess
    except (AttributeError, OSError):
        # Not started (no popen) or already gone; nothing left to stop.
        return
    process.join(timeout=graceful_timeout)
    if process.is_alive():
        process.kill()  # SIGKILL
        process.join(timeout=graceful_timeout)
