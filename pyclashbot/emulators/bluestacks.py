import csv
import io
import json
import os
import re
import subprocess
import time
from contextlib import suppress
from os.path import normpath
from winreg import (
    HKEY_LOCAL_MACHINE,
    ConnectRegistry,
    OpenKey,
    QueryValueEx,
)

import cv2
import numpy as np

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators.base import BaseEmulatorController
from pyclashbot.utils.graphics_detection import GraphicsDetector

DEBUG = False


class BlueStacksEmulatorController(BaseEmulatorController):
    """BlueStacks 5 controller using HD-Adb.

    - Read instance port from bluestacks.conf.
    - All ADB device commands are scoped with -s 127.0.0.1:<instance_port>.
    - Start/stop only this instance. Allows for future multi instance implementation for farming multiple accounts.
    """

    def __init__(self, logger, render_settings: dict | None = None):
        self.logger = logger

        # Set default graphics renderer if not specified
        if render_settings is None:
            best_api = GraphicsDetector.get_best_default_api("bluestacks")
            # Convert API name to BlueStacks format
            api_mapping = {"directx": "dx", "opengl": "gl", "vulkan": "vlcn"}
            render_settings = {"graphics_renderer": api_mapping.get(best_api, "dx")}
            self.logger.log(
                f"Auto-detected graphics renderer for BlueStacks: {best_api} -> {render_settings['graphics_renderer']}"
            )
        elif "graphics_renderer" in render_settings:
            # Validate the provided renderer
            api_mapping_reverse = {"dx": "directx", "gl": "opengl", "vlcn": "vulkan"}
            current_api = api_mapping_reverse.get(
                render_settings["graphics_renderer"], render_settings["graphics_renderer"]
            )
            corrected_api = GraphicsDetector.get_corrected_api(current_api, "bluestacks")
            api_mapping = {"directx": "dx", "opengl": "gl", "vulkan": "vlcn"}
            corrected_renderer = api_mapping.get(corrected_api, "dx")
            if corrected_renderer != render_settings["graphics_renderer"]:
                self.logger.log(
                    f"Graphics renderer corrected from {render_settings['graphics_renderer']} to {corrected_renderer} for BlueStacks"
                )
                render_settings["graphics_renderer"] = corrected_renderer

        self.expected_dims = (419, 633)  # Bypassing bs5's stupid dim limits

        self.instance_name = "pyclashbot-96"
        self.internal_name: str | None = None
        self.instance_port: int | None = None
        self.device_serial: str | None = None  # "127.0.0.1:<port>"

        self.adb_server_port: int = 5041
        self.adb_env = os.environ.copy()
        self.adb_env["ADB_SERVER_PORT"] = str(self.adb_server_port)

        # Do not auto-close BlueStacks 5 when controller is GC'd
        self._auto_stop_on_del = False  # yes it leaks, no I don't want to talk about it

        self.render_settings = render_settings or {}

        # Clean up our target instance only
        self.stop()
        while self._is_this_instance_running():  # Because Windows: I'm closing, also Windows: isn't closing
            self.stop()
            time.sleep(1)

        # Discover install
        install_base = self._find_install_location()
        self.base_folder = install_base
        if DEBUG:
            print(f"[Bluestacks 5] InstallDir: {install_base}")

        self.emulator_executable_path = os.path.join(install_base, "HD-Player.exe")
        self.adb_path = os.path.join(install_base, "HD-Adb.exe")
        if DEBUG:
            print(f"[Bluestacks 5] HD-Player: {self.emulator_executable_path}")
            print(f"[Bluestacks 5] HD-Adb: {self.adb_path}")
        for path in [install_base, self.emulator_executable_path, self.adb_path]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Required file or directory not found: {path}")

        # Config paths from registry DataDir
        data_dir = self._get_bluestacks_registry_value("DataDir")
        dd = normpath(str(data_dir)) if data_dir else None
        if not dd:
            raise FileNotFoundError("BlueStacks DataDir not found in registry.")

        self.bs_conf_path = os.path.join(os.path.dirname(dd), "bluestacks.conf")
        self.mim_meta_path = os.path.join(dd, "UserData", "MimMetaData.json")
        if not os.path.isfile(self.mim_meta_path):
            print(
                f"[Bluestacks 5] MimMetaData.json not found at {self.mim_meta_path}. Launching Multi-Instance Manager to create it..."
            )
            with suppress(Exception):
                os.startfile(os.path.join(self.base_folder, "HD-MultiInstanceManager.exe"))
            deadline = time.time() + 10
            while time.time() < deadline:
                if os.path.isfile(self.mim_meta_path):
                    print("[Bluestacks 5] MimMetaData.json detected.")
                    break
                time.sleep(0.5)
            else:
                raise FileNotFoundError("[Bluestacks 5] MimMetaData.json not created within 10 seconds.")
        if DEBUG:
            print(f"[Bluestacks 5] DataDir: {dd}")
            print(f"[Bluestacks 5] bs_conf_path: {self.bs_conf_path}")
            print(f"[Bluestacks 5] mim_meta_path: {self.mim_meta_path}")

        # Resolve instance and its ADB port
        self._ensure_managed_instance()
        if not self.instance_port:
            raise RuntimeError("No ADB port found for the target instance in bluestacks.conf.")
        self.device_serial = f"127.0.0.1:{self.instance_port}"

        # Reset our private adb server
        self._reset_adb_server()

        # Boot flow
        while self.restart() is False:
            print("[BlueStacks 5] Restart failed, retrying...")
            time.sleep(2)

    def _find_install_location(self) -> str:
        """Locate BlueStacks 5 installation folder from registry."""
        install_dir = self._get_bluestacks_registry_value("InstallDir")
        if not install_dir:
            raise FileNotFoundError("BlueStacks 5 installation not found (InstallDir missing).")
        base = normpath(str(install_dir))
        if os.path.isdir(base) and os.path.isfile(os.path.join(base, "HD-Player.exe")):
            return base
        raise FileNotFoundError(
            "BlueStacks 5 installation not found (HD-Player.exe missing)."
        )  # Seriously wtf happened better reinstall to fix

    def _get_bluestacks_registry_value(self, value_name: str) -> str | None:
        """Read a BlueStacks_nxt registry value from HKLM."""
        reg_paths = [r"SOFTWARE\BlueStacks_nxt"]
        with suppress(FileNotFoundError, OSError):
            reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            for subkey in reg_paths:
                with suppress(FileNotFoundError, OSError):
                    with OpenKey(reg, subkey) as k:
                        val = QueryValueEx(k, value_name)[0]
                        if isinstance(val, str) and val.strip():
                            return val
        return None

    def _read_text(self, path: str) -> str | None:
        if not os.path.isfile(path):
            return None
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def _read_json(self, path: str) -> dict:
        if not os.path.isfile(path):
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _get_conf_value(self, conf_text: str, key: str) -> str | None:
        m = re.search(rf'^{re.escape(key)}="([^"]*)"', conf_text, flags=re.M)
        return m.group(1) if m else None

    def _set_conf_value(self, conf_text: str, key: str, val: str) -> str:
        pat = rf'^(?P<k>{re.escape(key)})="[^"]*"'
        repl = rf'\g<k>="{val}"'
        new, n = re.subn(pat, repl, conf_text, flags=re.M)
        if n == 0:
            if not new.endswith("\n"):
                new += "\n"
            new += f'{key}="{val}"\n'
            # bad solution but fuck it, it works
        return new

    def _list_pie64_internals(self, conf_text: str) -> list[str]:
        names = set()
        for m in re.finditer(r"^bst\.instance\.(Pie64(?:_\d+)?)\.", conf_text, flags=re.M):
            names.add(m.group(1))
        # change this and then spend an afternoon wondering why nothing starts
        return sorted(
            names, key=lambda s: (0 if "_" in s else 1, int(s.split("_")[1]) if "_" in s else -1), reverse=True
        )

    def _find_internal_in_conf_by_display(self, conf_path: str, display_name: str) -> str | None:
        text = self._read_text(conf_path) or ""
        m = re.search(rf'^bst\.instance\.([^.=]+)\.display_name="{re.escape(display_name)}"\s*$', text, flags=re.M)
        return m.group(1) if m else None

    def _find_internal_by_display_name(self, mim_path: str, display_name: str) -> str | None:
        data = self._read_json(mim_path)
        org = data.get("Organization") if isinstance(data, dict) else None
        if not isinstance(org, list):
            return None
        for it in org:
            if isinstance(it, dict) and it.get("Name") == display_name:
                return it.get("InstanceName")
        return None

    def _read_instance_adb_port(self, conf_path: str, name_or_internal: str) -> int | None:
        # Just dont touch
        text = self._read_text(conf_path)
        if not text:
            return None
        internal = name_or_internal
        if not re.search(rf"^bst\.instance\.{re.escape(internal)}\.", text, flags=re.M):
            m = re.search(
                rf'^bst\.instance\.([^.=]+)\.display_name="{re.escape(name_or_internal)}"\s*$', text, flags=re.M
            )
            if m:
                internal = m.group(1)
        for key in (f"bst.instance.{internal}.status.adb_port", f"bst.instance.{internal}.adb_port"):
            m = re.search(rf'^{re.escape(key)}="(\d{{3,5}})"\s*$', text, flags=re.M)
            if m:
                try:
                    return int(m.group(1))
                except Exception:
                    return None
        return None

    def _normalize_renderer(self, desired: str | None) -> str:
        s = str(desired or "").strip().lower()
        alias = {
            "gl": "gl",
            "dx": "dx",
            "vlcn": "vlcn",
        }
        code = alias.get(s, "dx")
        if DEBUG:
            print(f"[Bluestacks 5] Renderer requested='{s}' normalized='{code}'")
        return code

    def _ensure_custom_resolution(self, conf_text: str, token: str = "418 x 633") -> str:
        existing = self._get_conf_value(conf_text, "bst.custom_resolutions")

        def norm(s: str) -> str:
            return s.lower().replace("Ã—", "x").replace(" ", "")  # Because of Unicode stuff

        want = norm(token)
        if not existing:
            return self._set_conf_value(conf_text, "bst.custom_resolutions", token)
        toks = [t.strip() for t in re.split(r"[;,]\s*|\n", existing) if t.strip()]
        if any(norm(t) == want for t in toks):
            return conf_text
        toks.append(token)
        return self._set_conf_value(conf_text, "bst.custom_resolutions", "; ".join(toks))

    def _display_name_exists(self, conf_path: str, display_name: str) -> bool:
        text = self._read_text(conf_path) or ""
        return (
            re.search(rf'^bst\.instance\.[^.=]+\.display_name="{re.escape(display_name)}"\s*$', text, flags=re.M)
            is not None
        )

    def _update_mim_name(self, mim_path: str, internal_name: str, ui_name: str) -> None:
        data = self._read_json(mim_path)
        data.setdefault("Organization", [])
        org = data["Organization"]
        for conf in org:
            if conf.get("InstanceName") == internal_name:
                conf["Name"] = ui_name  # rename here so the Instance Manager stops gaslighting us
                break
        with open(mim_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _close_multi_instance_manager(self) -> None:
        """Close BlueStacks Multi-Instance Manager if it's open after renaiming to update instance name in it."""
        subprocess.run(
            'taskkill /IM "HD-MultiInstanceManager.exe" /F', shell=True, capture_output=True, text=True, check=False
        )

    def _reuse_and_rename_internal(self, internal: str) -> bool:
        conf = self._read_text(self.bs_conf_path)
        if not conf:
            return False

        # Stop just this instance
        current_display = self._get_conf_value(conf, f"bst.instance.{internal}.display_name") or internal
        self.stop(display_name=current_display)

        conf = self._read_text(self.bs_conf_path) or ""
        conf, changed = self._compose_instance_conf(conf, internal, ensure_display=True)
        if changed:
            with open(self.bs_conf_path, "w", encoding="utf-8") as f:
                f.write(conf)
        self._update_mim_name(self.mim_meta_path, internal, self.instance_name)

        # Cache internals
        self.internal_name = internal
        self.instance_port = self._read_instance_adb_port(self.bs_conf_path, internal)
        self.device_serial = f"127.0.0.1:{self.instance_port}" if self.instance_port else None

        self.logger.log(
            f"[BlueStacks 5] Reused instance '{internal}' as '{self.instance_name}'. Port={self.instance_port}"
        )
        with suppress(Exception):
            self._close_multi_instance_manager()
        return True

    def _pick_unlinked_pie64(self) -> str | None:
        conf = self._read_text(self.bs_conf_path)
        if not conf:
            return None
        pie_list = self._list_pie64_internals(conf)
        if not pie_list:
            return None
        ga_re = re.compile(r'^bst\.instance\.([^.=]+)\.google_account_logins="(.*)"\s*$', re.M)
        accounts = {m.group(1): m.group(2) for m in ga_re.finditer(conf)}
        for internal in pie_list:
            if accounts.get(internal, "").strip() == "":
                return internal  # hoping it won't fuck up someones VM
        return None

    def _ensure_managed_instance(self):
        # If display entry exists
        if self._display_name_exists(self.bs_conf_path, self.instance_name):
            self.internal_name = self._find_internal_by_display_name(
                self.mim_meta_path, self.instance_name
            ) or self._find_internal_in_conf_by_display(self.bs_conf_path, self.instance_name)
            if self.internal_name:
                self.instance_port = self._read_instance_adb_port(self.bs_conf_path, self.internal_name)
            return

        # Try to reuse an existing "clean" Pie64 instance
        internal = self._pick_unlinked_pie64()
        if internal and self._reuse_and_rename_internal(internal):
            return

        # Open Multi-Instance Manager and prompt user to create a clean Pie64.
        while True:
            self._request_instance_retry = False
            self.logger.show_temporary_action(
                message="Open BlueStacks Multi-Instance Manager and create a fresh Pie64 instance wihtout logging into any google accounts, then click Retry.",
                action_text="Retry",
                callback=self._request_instance_creation_retry,
            )
            self.logger.log("[BlueStacks 5] No clean Pie64 instance found. Opening Multi-Instance Manager...")
            with suppress(Exception):
                os.startfile(os.path.join(self.base_folder, "HD-MultiInstanceManager.exe"))

            # Wait for user action via Retry callback
            self.instance_creation_waiting = True
            while getattr(self, "instance_creation_waiting", False):
                time.sleep(0.5)

            # User clicked Retry check again for a clean instance outside the callback
            if getattr(self, "_request_instance_retry", False):
                # If our display name exists, resolve internal and port
                if self._display_name_exists(self.bs_conf_path, self.instance_name):
                    internal = self._find_internal_by_display_name(
                        self.mim_meta_path, self.instance_name
                    ) or self._find_internal_in_conf_by_display(self.bs_conf_path, self.instance_name)
                    if internal:
                        self.internal_name = internal
                        self.instance_port = self._read_instance_adb_port(self.bs_conf_path, internal)
                        self.device_serial = f"127.0.0.1:{self.instance_port}" if self.instance_port else None
                        with suppress(Exception):
                            self._close_multi_instance_manager()
                        self.logger.change_status("Clean Pie64 instance detected - continuing...")
                        return

                # Otherwise try to reuse an unlinked Pie64
                internal = self._pick_unlinked_pie64()
                if internal and self._reuse_and_rename_internal(internal):
                    self.logger.change_status("Prepared clean Pie64 instance - continuing...")
                    return

                self.logger.log("[BlueStacks 5] Still no clean Pie64 instance. Please try again.")

    def _request_instance_creation_retry(self):
        self.logger.log("[BlueStacks 5] Retry clicked - rechecking for clean Pie64 instance")
        self._request_instance_retry = True
        self.instance_creation_waiting = False

    def _apply_renderer_setting(self) -> None:
        desired = self.render_settings["graphics_renderer"]
        desired_code = self._normalize_renderer(desired)
        if not self.bs_conf_path:
            return
        internal = self.internal_name or self._find_internal_in_conf_by_display(self.bs_conf_path, self.instance_name)
        if not internal:
            return
        conf = self._read_text(self.bs_conf_path) or ""
        current_display = self._get_conf_value(conf, f"bst.instance.{internal}.display_name") or internal
        self.stop(display_name=current_display)
        new_conf = self._set_conf_value(conf, f"bst.instance.{internal}.graphics_renderer", desired_code)
        if new_conf != conf:
            with suppress(Exception):
                with open(self.bs_conf_path, "w", encoding="utf-8") as f:
                    f.write(new_conf)
                self.logger.log(f"[BlueStacks 5] graphics_renderer set to {desired_code} for {internal}")

    def _compose_instance_conf(self, conf: str, internal: str, ensure_display: bool = True) -> tuple[str, bool]:
        """Return (new_conf, changed) with required BlueStacks settings applied, including renderer."""
        changed = False

        # Ensure global Bs5 ADB access is enabled
        if (self._get_conf_value(conf, "bst.enable_adb_access") or "0") != "1":
            conf = self._set_conf_value(conf, "bst.enable_adb_access", "1")
            changed = True

        # Ensure custom resolution entry exists
        new_conf = self._ensure_custom_resolution(conf, "418 x 633")
        if new_conf != conf:
            conf = new_conf
            changed = True

        desired = {
            f"bst.instance.{internal}.cpus": "2",
            f"bst.instance.{internal}.ram": "2048",
            f"bst.instance.{internal}.fb_width": str(self.expected_dims[0]),
            f"bst.instance.{internal}.fb_height": str(self.expected_dims[1]),
            f"bst.instance.{internal}.dpi": "160",
            f"bst.instance.{internal}.max_fps": "40",
            f"bst.instance.{internal}.custom_resolution_selected": "1",
        }
        if ensure_display:
            desired[f"bst.instance.{internal}.display_name"] = self.instance_name

        for key, val in desired.items():
            cur = self._get_conf_value(conf, key)
            if cur != val:
                conf = self._set_conf_value(conf, key, val)
                changed = True

        # Apply renderer from render_settings
        desired = self.render_settings["graphics_renderer"]
        desired_code = self._normalize_renderer(desired)
        cur = self._get_conf_value(conf, f"bst.instance.{internal}.graphics_renderer")
        if cur != desired_code:
            conf = self._set_conf_value(conf, f"bst.instance.{internal}.graphics_renderer", desired_code)
            changed = True

        return conf, changed

    def _enforce_instance_config(self) -> None:
        """Re-check and fix drifted VM settings before each start."""
        if not self.bs_conf_path:
            return
        internal = self.internal_name or self._find_internal_in_conf_by_display(self.bs_conf_path, self.instance_name)
        if not internal:
            return

        conf = self._read_text(self.bs_conf_path) or ""
        conf, changed = self._compose_instance_conf(conf, internal, ensure_display=True)

        if changed:
            with suppress(Exception):
                with open(self.bs_conf_path, "w", encoding="utf-8") as f:
                    f.write(conf)
                self.logger.log(f"[BlueStacks 5] Enforced VM config for '{internal}'")

    def _cmd_is_server_scoped(self, command: str) -> bool:
        c = command.strip()
        if c.startswith("-s "):
            return True
        first = c.split()[0] if c else ""
        return first in {"connect", "disconnect", "devices", "start-server", "kill-server", "version", "help", "keys"}

    def adb(self, command: str, binary_output: bool = False) -> subprocess.CompletedProcess:
        """Run an adb command via our private server. Device-scoped by default unless server-scoped."""
        base = f'"{self.adb_path}" -P {self.adb_server_port} '
        if not self._cmd_is_server_scoped(command) and self.device_serial:
            base += f"-s {self.device_serial} "
        full = base + command
        if DEBUG:
            print(f"[Bluestacks 5/ADB] {full}")
        return subprocess.run(
            full, shell=True, capture_output=True, text=not binary_output, check=False, env=self.adb_env
        )

    def adb_server(self, command: str) -> subprocess.CompletedProcess:
        full = f'"{self.adb_path}" -P {self.adb_server_port} {command}'
        if DEBUG:
            print(f"[Bluestacks 5/ADB-SRV] {full}")
        return subprocess.run(full, shell=True, capture_output=True, text=True, check=False, env=self.adb_env)

    def _reset_adb_server(self) -> None:
        with suppress(Exception):
            self.adb_server("kill-server")  # Cause ADB loves to randomly fuck around

    def _refresh_instance_port(self):
        """Re-read the instance port and update device_serial."""
        if not self.internal_name:
            return
        new_port = self._read_instance_adb_port(self.bs_conf_path, self.internal_name)
        if new_port and new_port != self.instance_port:
            self.instance_port = new_port
            self.device_serial = f"127.0.0.1:{self.instance_port}"
            if DEBUG:
                print(f"[Bluestacks 5] Refreshed instance port -> {self.device_serial}")

    def _connect(self) -> bool:
        """Connect only to this instance's port."""
        if not self.device_serial:
            return False
        self._reset_adb_server()
        self.adb_server(f"disconnect {self.device_serial}")
        time.sleep(0.2)
        self.adb_server(f"connect {self.device_serial}")
        state = self.adb("get-state")
        ok = (state.returncode == 0) and (state.stdout and "device" in state.stdout)
        if not ok:
            self._refresh_instance_port()
            if self.device_serial:
                self.adb_server(f"disconnect {self.device_serial}")
                time.sleep(0.2)
                self.adb_server(f"connect {self.device_serial}")
                state = self.adb("get-state")
                ok = (state.returncode == 0) and (state.stdout and "device" in state.stdout)
        return ok  # False means ADB is in a mood again

    def _is_this_instance_running(self) -> bool:
        title = self.instance_name
        try:
            res = subprocess.run(
                'tasklist /v /fi "IMAGENAME eq HD-Player.exe" /fo csv',
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0 or not res.stdout:
                return False
            reader = csv.reader(io.StringIO(res.stdout))
            next(reader, None)  # skip header
            for row in reader:
                if not row:
                    continue
                image = (row[0] if len(row) > 0 else "").strip().lower()
                window_title = (row[-1] if len(row) > 0 else "").strip()
                if image == "hd-player.exe" and window_title == title:
                    return True  # yes, I parsed CSV from tasklist. no, I'm not proud of it
        except Exception:
            return False
        return False

    def start(self):
        """Start only this instance. Enforce config just before launching."""
        with suppress(Exception):
            self._enforce_instance_config()

        args = []
        if self.internal_name:
            args = ["--instance", self.internal_name]
        cmd = '"' + self.emulator_executable_path + '"' + (" " + " ".join(args) if args else "")
        subprocess.Popen(cmd, shell=True)
        time.sleep(5)

    def stop(self, display_name: str | None = None):
        """Stop only this instance using the window title match."""
        title = display_name or self.instance_name
        subprocess.run(
            f'taskkill /fi "WINDOWTITLE eq {title}" /IM "HD-Player.exe" /F',
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )

    def restart(self) -> bool:
        start_ts = time.time()
        self.logger.change_status("Starting BlueStacks 5 emulator restart process...")

        self.logger.change_status("Stopping pyclashbot BlueStacks 5 instance...")
        self.stop()

        self.logger.change_status("Launching BlueStacks 5 (pyclashbot-96)...")
        self.start()

        # Wait for only our instance
        boot_timeout = 180
        t0 = time.time()
        while not self._is_this_instance_running():
            if time.time() - t0 > boot_timeout:
                self.logger.change_status("Timeout waiting for pyclashbot instance to start - retrying...")
                return False
            time.sleep(0.5)

        # Refresh port after boot
        self._refresh_instance_port()
        if not self.device_serial:
            self.logger.change_status("No ADB port resolved for this instance.")
            return False

        # Connect ADB scoped to our device
        self.logger.change_status(f"Connecting ADB to {self.device_serial} ...")
        t1 = time.time()
        while not self._connect():
            if time.time() - t1 > 60:
                self.logger.change_status("Failed to connect ADB to BlueStacks 5 - retrying...")
                return False  # if this makes issues big problems
            time.sleep(1)

        # Launch Clash Royale
        clash_pkg = "com.supercell.clashroyale"
        self.logger.change_status("Launching Clash Royale...")
        for _ in range(3):
            self.start_app(clash_pkg)
            time.sleep(5)

        # Wait for main menu
        self.logger.change_status("Waiting for Clash Royale main menu...")
        deadline = time.time() + 240
        while time.time() < deadline:
            if check_if_on_clash_main_menu(self):
                self.logger.change_status("Clash Royale main menu detected")
                dur = f"{time.time() - start_ts:.1f}s"
                self.logger.log(f"BlueStacks 5 restart completed in {dur}")
                return True
            self.click(5, 350)

        self.logger.change_status("Timeout waiting for Clash main menu - retrying...")
        return False

    def click(self, x_coord: int, y_coord: int, clicks: int = 1, interval: float = 0.0):
        for _ in range(max(1, clicks)):
            self.adb(f"shell input tap {x_coord} {y_coord}")
            if clicks <= 1:
                break
            time.sleep(max(0.0, interval))

    def swipe(self, x_coord1: int, y_coord1: int, x_coord2: int, y_coord2: int):
        self.adb(f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}")

    def screenshot(self) -> np.ndarray:
        # Verify device state on the scoped serial
        state = self.adb("get-state")
        if state.returncode != 0 or not state.stdout or "device" not in state.stdout:
            self._connect()
            state = self.adb("get-state")
            if state.returncode != 0 or not state.stdout or "device" not in state.stdout:
                raise RuntimeError("ADB device not ready on the instance port")

        result = self.adb("exec-out screencap -p", binary_output=True)
        if result.returncode != 0 or not result.stdout:
            err = result.stderr if result.stderr else b"Unknown ADB error"
            raise RuntimeError(f"ADB screencap failed: {err}")

        arr = np.frombuffer(result.stdout, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode screenshot image")
        return img

    def start_app(self, package_name: str):
        res = self.adb("shell pm list packages")
        if res.stdout and package_name not in res.stdout:
            return self._wait_for_clash_installation(package_name)
        self.adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

    def _wait_for_clash_installation(self, package_name: str):
        self.current_package_name = package_name
        self.logger.show_temporary_action(
            message="Clashroyal not installed - install the app and complete tutorial before retrying",
            action_text="Retry",
            callback=self._retry_installation_check,
        )
        self.logger.log(f"[BlueStacks 5] {package_name} not installed.")
        self._request_restart = False
        self.installation_waiting = True
        while self.installation_waiting:
            time.sleep(0.5)
        if getattr(self, "_request_restart", False):
            self.logger.change_status("Restarting BlueStacks...")
            self._request_restart = False
            return self.restart()
        self.logger.log("[BlueStacks 5] Installation confirmed, continuing...")
        return True

    def _retry_installation_check(self):
        self.logger.log(
            "[BlueStacks 5] Retry clicked, restarting the startup process..."
        )  # full restart because people might close emulator
        self._request_restart = True
        self.installation_waiting = False


if __name__ == "__main__":
    pass
