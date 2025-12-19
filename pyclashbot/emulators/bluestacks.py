import csv
import io
import json
import os
import re
import subprocess
import time
import tempfile
import threading
import socket
import random
from contextlib import suppress
from os.path import normpath
from winreg import (
    HKEY_LOCAL_MACHINE,
    ConnectRegistry,
    OpenKey,
    QueryValueEx,
)

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.emulators.adb_base import AdbBasedController

DEBUG = False


class BlueStacksEmulatorController(AdbBasedController):
    """BlueStacks 5 controller using HD-Adb.

    - Read instance port from bluestacks.conf.
    - All ADB device commands are scoped with -s 127.0.0.1:<instance_port>.
    - Supports multiple instances dynamically.
    - Supports multiple bots running simultaneously with different instances.
    """

    # Directorios compartidos para coordinación entre bots // Shared directories for coordination between bots
    _SHARED_DIR = os.path.join(tempfile.gettempdir(), "pyclashbot_coordination")
    _PORTS_FILE = os.path.join(_SHARED_DIR, "adb_ports.json")
    _LOCKS_FILE = os.path.join(_SHARED_DIR, "instance_locks.json")
    _PORTS_LOCK = os.path.join(_SHARED_DIR, "ports.lock")
    
    def __init__(self, logger, instance_name: str = None, render_settings: dict | None = None):
        self.logger = logger
        self.expected_dims = (419, 633)  # Bypassing bs5's stupid dim limits

        # Use provided instance name or use a default
        self.instance_name = instance_name or "BlueStacks"
        self.internal_name: str | None = None
        self.instance_port: int | None = None
        self.device_serial: str | None = None  # "127.0.0.1:<port>"

        # Crear directorio compartido si no existe // Create shared directory if it doesn't exist
        os.makedirs(self._SHARED_DIR, exist_ok=True)
        
        # Obtener un puerto ADB server ÚNICO para este bot // Get a UNIQUE ADB server port for this bot
        self.adb_server_port = self._get_available_adb_port()
        self.adb_env = os.environ.copy()
        self.adb_env["ADB_SERVER_PORT"] = str(self.adb_server_port)

        # Do not auto-close BlueStacks 5 when controller is GC'd
        self._auto_stop_on_del = False

        self.render_settings = render_settings or {}

        # Crear un ID único para este bot // Create a unique ID for this bot
        self.bot_id = f"bot_{os.getpid()}_{int(time.time())}"
        self.instance_locked = False
        self.port_registered = False

        # Registrar nuestro puerto ADB en el sistema compartido // Register our ADB port in the shared system
        self._register_adb_port()

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
                    print("[BlueStacks 5] MimMetaData.json detected.")
                    break
                time.sleep(0.5)
            else:
                raise FileNotFoundError("[BlueStacks 5] MimMetaData.json not created within 10 seconds.")
        if DEBUG:
            print(f"[Bluestacks 5] DataDir: {dd}")
            print(f"[Bluestacks 5] bs_conf_path: {self.bs_conf_path}")
            print(f"[Bluestacks 5] mim_meta_path: {self.mim_meta_path}")

        # Check if selected instance is already in use by another bot
        if self._is_instance_locked(self.instance_name):
            self.logger.log(f"Advertencia: La instancia '{self.instance_name}' parece estar en uso por otro bot. // Warning: Instance '{self.instance_name}' appears to be in use by another bot.")
            self.logger.log("Intentando usar la instancia seleccionada de todos modos... // Trying to use the selected instance anyway...")
        
        # Buscar y configurar la instancia seleccionada por el usuario // Search and configure the user-selected instance
        self._ensure_managed_instance()
        
        if not self.instance_port:
            raise RuntimeError("No ADB port found for the target instance in bluestacks.conf.")
        self.device_serial = f"127.0.0.1:{self.instance_port}"

        # Lock the instance to prevent other bots from using it
        self._lock_instance()

        # Iniciar timer para renovar registros // Start timer to renew registrations
        self._start_registration_renewal()

        # Boot flow
        while self.restart() is False:
            print("[BlueStacks 5] Restart failed, retrying...")
            time.sleep(2)

    def __del__(self):
        """Cleanup: release all resources when controller is destroyed."""
        self._cleanup()

    def _cleanup(self):
        """Cleanup all resources."""
        self._release_instance_lock()
        self._unregister_adb_port()
        # NO matamos el ADB server porque podría ser usado por nosotros mismos // We did NOT kill the ADB server because it could be used by ourselves.

    def _get_available_adb_port(self) -> int:
        """Obtiene un puerto ADB server disponible. // Gets an available ADB server port."""
        # Puerto base para ADB servers de bots // Base port for bot ADB servers
        base_port = 5041
        
        # Limpiar registros expirados primero // Clean up expired registrations first
        self._cleanup_expired_registrations()
        
        # Obtener puertos actualmente registrados // Get currently registered ports
        registered_ports = self._get_registered_ports()
        
        # Buscar primer puerto disponible // Find first available port
        port = base_port
        while True:
            if port not in registered_ports:
                # Verificar si el puerto está realmente libre // Verify if port is actually free
                if not self._is_port_in_use(port):
                    return port
            
            # Si el puerto está registrado pero expirado, podemos usarlo // If port is registered but expired, we can use it
            if port in registered_ports:
                reg = registered_ports[port]
                if time.time() - reg.get('timestamp', 0) > 300:  # 5 minutos // 5 minutes
                    # Eliminar registro expirado // Remove expired registration
                    self._remove_port_registration(port)
                    return port
            
            port += 1
            
            # Limite de seguridad // Safety limit
            if port > 60000:
                raise RuntimeError("No hay puertos ADB disponibles // No ADB ports available")

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except socket.error:
                return True

    def _register_adb_port(self):
        """Registra nuestro puerto ADB en el sistema compartido. // Registers our ADB port in the shared system."""
        with self._get_file_lock(self._PORTS_LOCK):
            ports_data = self._read_ports_file()
            
            # Verificar que el puerto no esté siendo usado por otro bot activo // Verify port is not being used by another active bot
            if str(self.adb_server_port) in ports_data:
                existing = ports_data[str(self.adb_server_port)]
                if time.time() - existing.get('timestamp', 0) < 300:  # 5 minutos // 5 minutes
                    # Otro bot activo está usando este puerto // Another active bot is using this port
                    raise RuntimeError(f"Puerto ADB {self.adb_server_port} ya está en uso // ADB port {self.adb_server_port} is already in use")
            
            # Registrar nuestro puerto // Register our port
            ports_data[str(self.adb_server_port)] = {
                'bot_id': self.bot_id,
                'pid': os.getpid(),
                'timestamp': time.time(),
                'instance': self.instance_name if hasattr(self, 'instance_name') else 'unknown'
            }
            
            self._write_ports_file(ports_data)
            self.port_registered = True
            self.logger.log(f"Puerto ADB {self.adb_server_port} registrado para bot {self.bot_id} // ADB port {self.adb_server_port} registered for bot {self.bot_id}")

    def _unregister_adb_port(self):
        """Elimina nuestro registro de puerto ADB. // Removes our ADB port registration."""
        if not self.port_registered:
            return
            
        with self._get_file_lock(self._PORTS_LOCK):
            ports_data = self._read_ports_file()
            port_str = str(self.adb_server_port)
            
            if port_str in ports_data:
                # Verificar que sea NUESTRO registro // Verify it's OUR registration
                if ports_data[port_str].get('bot_id') == self.bot_id:
                    del ports_data[port_str]
                    self._write_ports_file(ports_data)
                    self.logger.log(f"Puerto ADB {self.adb_server_port} desregistrado // ADB port {self.adb_server_port} unregistered")
            
            self.port_registered = False

    def _renew_adb_port_registration(self):
        """Renueva el registro de nuestro puerto ADB. // Renews our ADB port registration."""
        if not self.port_registered:
            return
            
        with self._get_file_lock(self._PORTS_LOCK):
            ports_data = self._read_ports_file()
            port_str = str(self.adb_server_port)
            
            if port_str in ports_data:
                # Actualizar timestamp // Update timestamp
                ports_data[port_str]['timestamp'] = time.time()
                self._write_ports_file(ports_data)

    def _cleanup_expired_registrations(self):
        """Limpia registros expirados. // Cleans up expired registrations."""
        with self._get_file_lock(self._PORTS_LOCK):
            ports_data = self._read_ports_file()
            locks_data = self._read_locks_file()
            
            current_time = time.time()
            expired_ports = []
            
            # Limpiar puertos expirados // Clean up expired ports
            for port, data in list(ports_data.items()):
                if current_time - data.get('timestamp', 0) > 300:  # 5 minutos // 5 minutes
                    expired_ports.append(port)
            
            for port in expired_ports:
                del ports_data[port]
            
            # Limpiar locks expirados // Clean up expired locks
            for instance, data in list(locks_data.items()):
                if current_time - data.get('timestamp', 0) > 300:  # 5 minutos // 5 minutes
                    del locks_data[instance]
            
            self._write_ports_file(ports_data)
            self._write_locks_file(locks_data)

    def _get_registered_ports(self) -> dict:
        """Obtiene puertos actualmente registrados. // Gets currently registered ports."""
        ports_data = self._read_ports_file()
        return {int(k): v for k, v in ports_data.items()}

    def _read_ports_file(self) -> dict:
        """Lee el archivo de puertos. // Reads the ports file."""
        if not os.path.exists(self._PORTS_FILE):
            return {}
        try:
            with open(self._PORTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _write_ports_file(self, data: dict):
        """Escribe el archivo de puertos. // Writes the ports file."""
        with open(self._PORTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _read_locks_file(self) -> dict:
        """Lee el archivo de locks. // Reads the locks file."""
        if not os.path.exists(self._LOCKS_FILE):
            return {}
        try:
            with open(self._LOCKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _write_locks_file(self, data: dict):
        """Escribe el archivo de locks. // Writes the locks file."""
        with open(self._LOCKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_file_lock(self, lock_file: str):
        """Context manager para locks de archivo simple. // Context manager for simple file locks."""
        class FileLock:
            def __init__(self, lock_file):
                self.lock_file = lock_file
                
            def __enter__(self):
                max_attempts = 10
                for i in range(max_attempts):
                    try:
                        self.lock_fd = open(self.lock_file, 'x')
                        return self
                    except FileExistsError:
                        if i == max_attempts - 1:
                            raise RuntimeError(f"No se pudo obtener lock en {self.lock_file} // Could not obtain lock on {self.lock_file}")
                        time.sleep(0.1)
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.lock_fd.close()
                os.remove(self.lock_file)
        
        return FileLock(lock_file)

    def _start_registration_renewal(self):
        """Inicia un timer para renovar registros periódicamente. // Starts a timer to periodically renew registrations."""
        def renew_task():
            while getattr(self, 'port_registered', False) or getattr(self, 'instance_locked', False):
                time.sleep(60)  # Renovar cada minuto // Renew every minute
                try:
                    if getattr(self, 'port_registered', False):
                        self._renew_adb_port_registration()
                    if getattr(self, 'instance_locked', False):
                        self._renew_instance_lock()
                except:
                    pass
        
        self.renewal_thread = threading.Thread(target=renew_task, daemon=True)
        self.renewal_thread.start()

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
        )

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
        return new

    def _list_pie64_internals(self, conf_text: str) -> list[str]:
        names = set()
        for m in re.finditer(r"^bst\.instance\.(Pie64(?:_\d+)?)\.", conf_text, flags=re.M):
            names.add(m.group(1))
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
        """Read ADB port for an instance. ALWAYS prefer adb_port over status.adb_port."""
        text = self._read_text(conf_path)
        if not text:
            self.logger.log(f"[BlueStacks] No se pudo leer archivo de configuración: {conf_path} // Could not read configuration file: {conf_path}")
            return None
        
        internal = name_or_internal
        
        # Verificar si es un nombre interno válido (Pie64 o Pie64_XX) // Check if it's a valid internal name (Pie64 or Pie64_XX)
        pattern = rf"^bst\.instance\.{re.escape(internal)}\."
        if not re.search(pattern, text, flags=re.M):
            # Si no es nombre interno, buscar por display name // If not internal name, search by display name
            pattern = rf'^bst\.instance\.([^.=]+)\.display_name="{re.escape(name_or_internal)}"\s*$'
            m = re.search(pattern, text, flags=re.M)
            if m:
                internal = m.group(1)
                self.logger.log(f"[BlueStacks] Nombre interno encontrado para '{name_or_internal}': {internal} // Internal name found for '{name_or_internal}': {internal}")
        
        # BUSCAR AMBOS PUERTOS SIMULTÁNEAMENTE // SEARCH BOTH PORTS SIMULTANEOUSLY
        adb_port = None
        status_port = None
        
        # 1. Buscar adb_port (puerto REAL de conexión) // Search adb_port (REAL connection port)
        adb_port_key = f"bst.instance.{internal}.adb_port"
        adb_match = re.search(rf'^{re.escape(adb_port_key)}="(\d{{3,5}})"\s*$', text, flags=re.M)
        if adb_match:
            adb_port = int(adb_match.group(1))
            self.logger.log(f"[BlueStacks] Encontrado adb_port para {internal}: {adb_port} // Found adb_port for {internal}: {adb_port}")
        
        # 2. Buscar status.adb_port (puerto de estado/reservado) // Search status.adb_port (status/reserved port)
        status_key = f"bst.instance.{internal}.status.adb_port"
        status_match = re.search(rf'^{re.escape(status_key)}="(\d{{3,5}})"\s*$', text, flags=re.M)
        if status_match:
            status_port = int(status_match.group(1))
            self.logger.log(f"[BlueStacks] Encontrado status.adb_port para {internal}: {status_port} // Found status.adb_port for {internal}: {status_port}")
        
        # LÓGICA DE DECISIÓN INTELIGENTE: // INTELLIGENT DECISION LOGIC:
        # 1. PRIORIDAD: adb_port si existe y NO es 5555 // PRIORITY: adb_port if exists and is NOT 5555
        if adb_port is not None and adb_port != 5555:
            self.logger.log(f"[BlueStacks] Usando adb_port ({adb_port}) para {internal} // Using adb_port ({adb_port}) for {internal}")
            return adb_port
        
        # 2. Si adb_port es 5555 (valor por defecto/reservado) PERO status_port existe y NO es 5555 // If adb_port is 5555 (default/reserved) BUT status_port exists and is NOT 5555
        if adb_port == 5555 and status_port is not None and status_port != 5555:
            self.logger.log(f"[BlueStacks] adb_port es 5555 (reservado), usando status.adb_port ({status_port}) para {internal} // adb_port is 5555 (reserved), using status.adb_port ({status_port}) for {internal}")
            return status_port
        
        # 3. Si solo adb_port existe (aunque sea 5555) // If only adb_port exists (even if 5555)
        if adb_port is not None:
            self.logger.log(f"[BlueStacks] Usando adb_port ({adb_port}) para {internal} (única opción) // Using adb_port ({adb_port}) for {internal} (only option)")
            return adb_port
        
        # 4. Si solo status_port existe // If only status_port exists
        if status_port is not None:
            self.logger.log(f"[BlueStacks] Usando status.adb_port ({status_port}) para {internal} // Using status.adb_port ({status_port}) for {internal}")
            return status_port
        
        # 5. No se encontró ningún puerto // No port found
        self.logger.log(f"[BlueStacks] ERROR: No se encontró puerto ADB para {internal} // ERROR: No ADB port found for {internal}")
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
            return s.lower().replace("Ã—", "x").replace(" ", "")

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
                conf["Name"] = ui_name
                break
        with open(mim_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def _close_multi_instance_manager(self) -> None:
        """Close BlueStacks Multi-Instance Manager if it's open after renaming to update instance name in it."""
        subprocess.run(
            'taskkill /IM "HD-MultiInstanceManager.exe" /F', shell=True, capture_output=True, text=True, check=False
        )

    def _reuse_and_rename_internal(self, internal: str) -> bool:
        # NO reutilizar instancias, siempre usar la seleccionada por el usuario // DO NOT reuse instances, always use the user-selected one
        return False

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
            # Verificar si tiene cuentas de Google // Check if it has Google accounts
            if accounts.get(internal, "").strip() == "":
                # EXCLUIR instancias con nombres no deseados // EXCLUDE instances with unwanted names
                display_name = self._get_conf_value(conf, f"bst.instance.{internal}.display_name")
                if display_name and display_name not in ["BlueStacksxdxd", "BlueStacks"]:
                    return internal
        
        return None

    def _ensure_managed_instance(self):
        """Ensure the instance exists and is properly configured."""
        self.logger.log(f"Buscando instancia: '{self.instance_name}' // Searching for instance: '{self.instance_name}'")
        
        # PRIORIDAD 1: Usar la instancia seleccionada por el usuario // PRIORITY 1: Use the user-selected instance
        if self.instance_name and self.instance_name != "BlueStacks":
            # Buscar por display name en el archivo conf // Search by display name in the conf file
            text = self._read_text(self.bs_conf_path)
            if text:
                # Buscar el nombre interno por el display name // Find internal name by display name
                pattern = rf'bst\.instance\.([^.=]+)\.display_name="{re.escape(self.instance_name)}"'
                match = re.search(pattern, text)
                
                if match:
                    self.internal_name = match.group(1)
                    self.instance_port = self._read_instance_adb_port(self.bs_conf_path, self.internal_name)
                    self.device_serial = f"127.0.0.1:{self.instance_port}" if self.instance_port else None
                    self.logger.log(f"Encontrada instancia existente: {self.instance_name} -> {self.internal_name} // Found existing instance: {self.instance_name} -> {self.internal_name}")
                    return
        
        # PRIORIDAD 2: Buscar cualquier instancia disponible que NO esté bloqueada // PRIORITY 2: Search for any available instance NOT locked
        self.logger.log(f"Instancia '{self.instance_name}' no encontrada, buscando alternativas... // Instance '{self.instance_name}' not found, searching for alternatives...")
        
        # Buscar cualquier instancia Pie64 disponible // Search for any available Pie64 instance
        conf = self._read_text(self.bs_conf_path)
        if conf:
            # Buscar todas las instancias Pie64 // Search all Pie64 instances
            pie_list = self._list_pie64_internals(conf)
            
            for internal in pie_list:
                display_name = self._get_conf_value(conf, f"bst.instance.{internal}.display_name")
                
                # EXCLUIR instancias con nombres no deseados // EXCLUDE instances with unwanted names
                if display_name and display_name not in ["BlueStacksxdxd", "BlueStacks"]:
                    # Verificar si la instancia no está bloqueada por otro bot // Check if instance is not locked by another bot
                    if not self._is_instance_locked(display_name):
                        self.instance_name = display_name
                        self.internal_name = internal
                        self.instance_port = self._read_instance_adb_port(self.bs_conf_path, internal)
                        self.device_serial = f"127.0.0.1:{self.instance_port}" if self.instance_port else None
                        self.logger.log(f"Usando instancia disponible: {display_name} // Using available instance: {display_name}")
                        return
        
        # PRIORIDAD 3: Si todas están bloqueadas, usar la primera disponible ignorando locks // PRIORITY 3: If all are locked, use first available ignoring locks
        conf = self._read_text(self.bs_conf_path)
        if conf:
            pie_list = self._list_pie64_internals(conf)
            
            for internal in pie_list:
                display_name = self._get_conf_value(conf, f"bst.instance.{internal}.display_name")
                
                if display_name and display_name not in ["BlueStacksxdxd", "BlueStacks"]:
                    self.logger.log(f"Todas las instancias están bloqueadas, usando: {display_name} // All instances are locked, using: {display_name}")
                    self.instance_name = display_name
                    self.internal_name = internal
                    self.instance_port = self._read_instance_adb_port(self.bs_conf_path, internal)
                    self.device_serial = f"127.0.0.1:{self.instance_port}" if self.instance_port else None
                    return
        
        # Si no hay instancias disponibles, crear una nueva // If no instances available, create new one
        self.logger.log("No hay instancias disponibles, creando nueva... // No instances available, creating new one...")
        self._create_new_instance()

    def _create_new_instance(self):
        """Create a new BlueStacks instance."""
        self.logger.log(f"Creando nueva instancia BlueStacks: {self.instance_name} // Creating new BlueStacks instance: {self.instance_name}")
        
        # Open Multi-Instance Manager
        with suppress(Exception):
            os.startfile(os.path.join(self.base_folder, "HD-MultiInstanceManager.exe"))
        
        self.logger.show_temporary_action(
            message=f"Por favor crea una nueva instancia Pie64 llamada '{self.instance_name}' en BlueStacks Multi-Instance Manager,\n"
                    f"luego haz click en Retry. // Please create a new Pie64 instance named '{self.instance_name}' in BlueStacks Multi-Instance Manager,\n"
                    f"then click Retry.",
            action_text="Retry",
            callback=self._request_instance_creation_retry,
        )
        
        self.instance_creation_waiting = True
        while getattr(self, "instance_creation_waiting", False):
            time.sleep(0.5)

    def _request_instance_creation_retry(self):
        self.logger.log("[BlueStacks 5] Retry clicked - checking for new instance")
        self._request_instance_retry = True
        self.instance_creation_waiting = False
        
        # Check if instance was created
        if self._display_name_exists(self.bs_conf_path, self.instance_name):
            self.internal_name = self._find_internal_by_display_name(
                self.mim_meta_path, self.instance_name
            ) or self._find_internal_in_conf_by_display(self.bs_conf_path, self.instance_name)
            if self.internal_name:
                self.instance_port = self._read_instance_adb_port(self.bs_conf_path, self.internal_name)
                self.device_serial = f"127.0.0.1:{self.instance_port}" if self.instance_port else None
                self.logger.change_status(f"Instancia '{self.instance_name}' creada exitosamente. // Instance '{self.instance_name}' created successfully.")
                return True
        return False

    def _lock_instance(self):
        """Crea un lock para esta instancia en el sistema compartido. // Creates a lock for this instance in the shared system."""
        if not self.instance_name:
            return
        
        with self._get_file_lock(self._PORTS_LOCK):
            locks_data = self._read_locks_file()
            
            # Verificar si ya está bloqueada por otro bot activo // Check if already locked by another active bot
            if self.instance_name in locks_data:
                existing = locks_data[self.instance_name]
                if time.time() - existing.get('timestamp', 0) < 300:  # 5 minutos // 5 minutes
                    if existing.get('bot_id') != self.bot_id:
                        self.logger.log(f"Advertencia: Instancia '{self.instance_name}' ya bloqueada por otro bot // Warning: Instance '{self.instance_name}' already locked by another bot")
                        # Continuar de todos modos, pero con advertencia // Continue anyway, but with warning
            
            # Crear/actualizar nuestro lock // Create/update our lock
            locks_data[self.instance_name] = {
                'bot_id': self.bot_id,
                'pid': os.getpid(),
                'timestamp': time.time(),
                'adb_port': self.instance_port,
                'adb_server_port': self.adb_server_port
            }
            
            self._write_locks_file(locks_data)
            self.instance_locked = True
            self.logger.log(f"Instancia '{self.instance_name}' bloqueada por bot {self.bot_id} // Instance '{self.instance_name}' locked by bot {self.bot_id}")

    def _release_instance_lock(self):
        """Libera el lock de esta instancia. // Releases the lock for this instance."""
        if not self.instance_locked or not self.instance_name:
            return
        
        with self._get_file_lock(self._PORTS_LOCK):
            locks_data = self._read_locks_file()
            
            if self.instance_name in locks_data:
                # Verificar que sea NUESTRO lock // Verify it's OUR lock
                if locks_data[self.instance_name].get('bot_id') == self.bot_id:
                    del locks_data[self.instance_name]
                    self._write_locks_file(locks_data)
                    self.logger.log(f"Lock liberado para instancia '{self.instance_name}' // Lock released for instance '{self.instance_name}'")
            
            self.instance_locked = False

    def _renew_instance_lock(self):
        """Renueva el lock de esta instancia. // Renews the lock for this instance."""
        if not self.instance_locked or not self.instance_name:
            return
        
        with self._get_file_lock(self._PORTS_LOCK):
            locks_data = self._read_locks_file()
            
            if self.instance_name in locks_data:
                # Actualizar timestamp // Update timestamp
                locks_data[self.instance_name]['timestamp'] = time.time()
                self._write_locks_file(locks_data)

    def _is_instance_locked(self, instance_name: str) -> bool:
        """Verifica si una instancia está bloqueada por OTRO bot. // Checks if an instance is locked by ANOTHER bot."""
        if not instance_name:
            return False
        
        locks_data = self._read_locks_file()
        
        if instance_name not in locks_data:
            return False
        
        lock_data = locks_data[instance_name]
        
        # Verificar si es NUESTRO propio lock // Check if it's OUR own lock
        if lock_data.get('bot_id') == self.bot_id:
            return False  # No está bloqueado por OTRO bot // Not locked by ANOTHER bot
        
        # Verificar si el lock expiró // Check if lock expired
        if time.time() - lock_data.get('timestamp', 0) > 300:  # 5 minutos // 5 minutes
            return False  # Lock expirado // Lock expired
        
        # Verificar si el proceso que creó el lock todavía existe // Check if process that created lock still exists
        pid = lock_data.get('pid')
        if pid:
            try:
                result = subprocess.run(f'tasklist /fi "PID eq {pid}"', 
                                      shell=True, capture_output=True, text=True)
                if str(pid) not in result.stdout:
                    return False  # Proceso no existe // Process doesn't exist
            except:
                return False  # Error al verificar // Error checking
        
        # Instancia bloqueada por otro bot activo // Instance locked by another active bot
        return True

    def get_running_instances(self):
        """Get all running BlueStacks instances."""
        instances = []
        try:
            res = subprocess.run(
                'tasklist /v /fi "IMAGENAME eq HD-Player.exe" /fo csv',
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0 or not res.stdout:
                return instances
            
            reader = csv.reader(io.StringIO(res.stdout))
            next(reader, None)  # skip header
            for row in reader:
                if not row or len(row) < 9:
                    continue
                image = (row[0] if len(row) > 0 else "").strip().lower()
                window_title = (row[8] if len(row) > 8 else "").strip()
                if image == "hd-player.exe" and window_title:
                    # Try to find this instance in the config
                    internal = self._find_internal_in_conf_by_display(self.bs_conf_path, window_title)
                    if internal:
                        port = self._read_instance_adb_port(self.bs_conf_path, internal)
                        # Check if instance is locked
                        is_locked = self._is_instance_locked(window_title)
                        instances.append({
                            'display_name': window_title,
                            'internal_name': internal,
                            'adb_port': port,
                            'is_running': True,
                            'is_locked': is_locked
                        })
        except Exception as e:
            self.logger.log(f"Error getting running instances: {e}")
        
        return instances

    def list_available_instances(self):
        """List all available BlueStacks instances."""
        instances = []
        
        if not os.path.exists(self.bs_conf_path):
            return instances
        
        conf = self._read_text(self.bs_conf_path) or ""
        pie_list = self._list_pie64_internals(conf)
        
        for internal in pie_list:
            display_name = self._get_conf_value(conf, f"bst.instance.{internal}.display_name")
            if not display_name:
                display_name = internal
            
            # EXCLUIR instancias con nombres no deseados // EXCLUDE instances with unwanted names
            if display_name in ["BlueStacksxdxd", "BlueStacks"]:
                continue
            
            port = self._read_instance_adb_port(self.bs_conf_path, internal)
            
            # Check if instance is running
            is_running = False
            try:
                res = subprocess.run(
                    'tasklist /v /fi "IMAGENAME eq HD-Player.exe" /fo csv',
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode == 0 and res.stdout:
                    reader = csv.reader(io.StringIO(res.stdout))
                    next(reader, None)
                    for row in reader:
                        if row and len(row) >= 9:
                            window_title = (row[8] if len(row) > 8 else "").strip()
                            if window_title == display_name:
                                is_running = True
                                break
            except Exception:
                pass
            
            # Check if instance is locked
            is_locked = self._is_instance_locked(display_name)
            
            instances.append({
                'display_name': display_name,
                'internal_name': internal,
                'adb_port': port,
                'is_running': is_running,
                'is_locked': is_locked
            })
        
        return instances

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

        # Use dynamic resolution instead of hardcoded 2 cores, 2GB RAM
        # The bot will work with any instance configuration
        desired = {
            f"bst.instance.{internal}.fb_width": str(self.expected_dims[0]),
            f"bst.instance.{internal}.fb_height": str(self.expected_dims[1]),
            f"bst.instance.{internal}.dpi": "160",
            f"bst.instance.{internal}.max_fps": "40",
            f"bst.instance.{internal}.custom_resolution_selected": "1",
        }
        
        # IMPORTANTE: NO cambiar el display_name de la instancia // IMPORTANT: DO NOT change instance display_name
        # Solo cambiar si realmente no tiene display_name o está vacío // Only change if it really has no display_name or it's empty
        current_display = self._get_conf_value(conf, f"bst.instance.{internal}.display_name")
        if not current_display or current_display.strip() == "":
            desired[f"bst.instance.{internal}.display_name"] = self.instance_name

        for key, val in desired.items():
            cur = self._get_conf_value(conf, key)
            if cur != val:
                conf = self._set_conf_value(conf, key, val)
                changed = True

        # Apply renderer from render_settings
        desired_renderer = self.render_settings.get("graphics_renderer", "dx")
        desired_code = self._normalize_renderer(desired_renderer)
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
        conf, changed = self._compose_instance_conf(conf, internal, ensure_display=False)

        if changed:
            with suppress(Exception):
                with open(self.bs_conf_path, "w", encoding="utf-8") as f:
                    f.write(conf)
                self.logger.log(f"[BlueStacks 5] Configurada VM para '{internal}' // VM configured for '{internal}'")

    def _cmd_is_server_scoped(self, command: str) -> bool:
        c = command.strip()
        if c.startswith("-s "):
            return True
        first = c.split()[0] if c else ""
        return first in {"connect", "disconnect", "devices", "start-server", "kill-server", "version", "help", "keys"}

    def adb(self, command: str, binary_output: bool = False) -> subprocess.CompletedProcess:
        """
        Run an adb command via our private server. Device-scoped by default unless server-scoped.
        This is the abstract method implementation for AdbBasedController.
        """
        base = f'"{self.adb_path}" -P {self.adb_server_port} '
        if not self._cmd_is_server_scoped(command) and self.device_serial:
            base += f"-s {self.device_serial} "
        full = base + command
        if DEBUG:
            print(f"[Bluestacks 5/ADB] {full}")
        return subprocess.run(
            full, shell=True, capture_output=True, text=not binary_output, check=False, env=self.adb_env
        )

    def _check_app_installed(self, package_name: str) -> bool:
        """
        Check if app is installed via ADB.
        This is the abstract method implementation for AdbBasedController.
        """
        res = self.adb("shell pm list packages")
        return res.stdout is not None and package_name in res.stdout

    def adb_server(self, command: str) -> subprocess.CompletedProcess:
        full = f'"{self.adb_path}" -P {self.adb_server_port} {command}'
        if DEBUG:
            print(f"[Bluestacks 5/ADB-SRV] {full}")
        return subprocess.run(full, shell=True, capture_output=True, text=True, check=False, env=self.adb_env)

    def _reset_adb_server(self) -> None:
        """Resetea NUESTRO ADB server (no mata servers de otros bots). // Resets OUR ADB server (doesn't kill other bots' servers)."""
        # Solo matamos nuestro propio server // We only kill our own server
        try:
            self.adb_server("kill-server")
        except:
            pass

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
        
        # Solo resetear nuestro propio ADB server // Only reset our own ADB server
        self._reset_adb_server()
        
        # Intentar desconectar primero (solo nuestra conexión) // Try to disconnect first (only our connection)
        self.adb_server(f"disconnect {self.device_serial}")
        time.sleep(0.2)
        
        # Conectar // Connect
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
        
        return ok

    def _is_this_instance_running(self) -> bool:
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
            next(reader, None)
            for row in reader:
                if not row or len(row) < 9:
                    continue
                image = (row[0] if len(row) > 0 else "").strip().lower()
                window_title = (row[8] if len(row) > 8 else "").strip()
                if image == "hd-player.exe" and window_title == self.instance_name:
                    return True
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
        # Solo detenemos si es NUESTRA instancia // We only stop if it's OUR instance
        if title == self.instance_name:
            subprocess.run(
                f'taskkill /fi "WINDOWTITLE eq {title}" /IM "HD-Player.exe" /F',
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )

    def restart(self) -> bool:
        start_ts = time.time()
        self.logger.change_status(f"Starting BlueStacks 5 emulator ({self.instance_name})...")

        self.logger.change_status(f"Stopping {self.instance_name} instance...")
        self.stop()

        self.logger.change_status(f"Launching BlueStacks 5 ({self.instance_name})...")
        self.start()

        # Wait for only our instance
        boot_timeout = 180
        t0 = time.time()
        while not self._is_this_instance_running():
            if time.time() - t0 > boot_timeout:
                self.logger.change_status("Timeout waiting for instance to start - retrying...")
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
                return False
            time.sleep(1)

        # Launch Clash Royale
        clash_pkg = "com.supercell.clashroyale"
        self.logger.change_status("Launching Clash Royale...")

        # Use inherited start_app which handles installation check
        if not self.start_app(clash_pkg):
            self.logger.log("Waiting for app installation...")
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
            self.click(5, 350)  # Use inherited click

        self.logger.change_status("Timeout waiting for Clash main menu - retrying...")
        return False


if __name__ == "__main__":
    pass