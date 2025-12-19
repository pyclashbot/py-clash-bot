import time
import traceback

from pyclashbot.bot.states import StateHistory, StateOrder, state_tree
from pyclashbot.emulators.adb import AdbController
from pyclashbot.emulators.bluestacks import BlueStacksEmulatorController
from pyclashbot.emulators.google_play import GooglePlayEmulatorController
from pyclashbot.emulators.memu import MemuEmulatorController, verify_memu_installation
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.thread import PausableThread, ThreadKilled


class WorkerThread(PausableThread):
    def __init__(self, logger: Logger, args, kwargs=None) -> None:
        super().__init__(args, kwargs)
        self.logger: Logger = logger
        self.in_a_clan = False

    def _create_google_play_emulator(self):
        """Create and return a Google Play emulator instance."""
        try:
            emulator = GooglePlayEmulatorController(logger=self.logger)
            print("Successfully created google play emulator")
            return emulator
        except Exception as e:
            print(f"Failed to create Google Play emulator: {e}")
            self.logger.change_status("Failed to start Google Play. Verify its installation!")
            return None

    def _create_memu_emulator(self, render_mode):
        """Create and return a MEmu emulator instance."""
        if not verify_memu_installation():
            self.logger.change_status("Memu is not installed! Please install it to use Memu Emulator Mode")
            return None

        return MemuEmulatorController(self.logger, render_mode)

    def _create_bluestacks_emulator(self, jobs):
        """Create and return a BlueStacks 5 emulator instance."""
        print("Creating BlueStacks 5 emulator")
        try:
            # Obtener configuración del renderer
            bs_mode = jobs.get("bluestacks_render_mode", "dx")
            if bs_mode == "opengl":
                bs_mode = "gl"
            elif bs_mode == "vulkan":
                bs_mode = "vlcn"
            else:
                bs_mode = "dx"
            
            render_settings = {"graphics_renderer": bs_mode}
            
            # Obtener nombre de instancia desde los trabajos
            instance_name = jobs.get("bluestacks_instance_name", "BlueStacks")
            if not instance_name or instance_name == "":
                instance_name = "BlueStacks"
            
            self.logger.log(f"Starting BlueStacks instance: {instance_name}")
            
            return BlueStacksEmulatorController(
                logger=self.logger, 
                instance_name=instance_name,
                render_settings=render_settings
            )
        except Exception as e:
            print(f"Failed to create BlueStacks 5 emulator: {e}")
            self.logger.change_status("Failed to start BlueStacks 5. Verify its installation!")
            return None

    def _create_adb_device(self, jobs):
        """Create and return an ADB Device controller."""
        print("Creating ADB Device controller")
        try:
            adb_serial = jobs.get("adb_serial", None)
            return AdbController(logger=self.logger, device_serial=adb_serial)
        except Exception as e:
            print(f"Failed to create ADB Device controller: {e}")
            self.logger.change_status("Failed to connect to ADB device. Check connection and ADB setup!")
            return None

    def _setup_emulator(self, jobs):
        """Set up the appropriate emulator based on job configuration."""
        # Determinar qué emulador está seleccionado
        emulator_selection = None
        
        if jobs.get("google_play_emulator_toggle"):
            emulator_selection = "Google Play"
        elif jobs.get("bluestacks_emulator_toggle"):
            emulator_selection = "BlueStacks 5"
        elif jobs.get("adb_toggle"):
            emulator_selection = "ADB Device"
        elif jobs.get("memu_emulator_toggle"):
            emulator_selection = "MEmu"
        else:
            # Por defecto, usar BlueStacks
            emulator_selection = "BlueStacks 5"

        print(f"Selected emulator: {emulator_selection}")

        if emulator_selection == "Google Play":
            return self._create_google_play_emulator()
        elif emulator_selection == "BlueStacks 5":
            return self._create_bluestacks_emulator(jobs)
        elif emulator_selection == "MEmu":
            render_mode = jobs.get("memu_render_mode", "opengl")
            return self._create_memu_emulator(render_mode)
        elif emulator_selection == "ADB Device":
            return self._create_adb_device(jobs)
        else:
            print(f"[!] Fatal error: Emulator {emulator_selection} is not supported!")
            self.logger.change_status(f"Emulator {emulator_selection} is not supported!")
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