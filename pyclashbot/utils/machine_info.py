"""A module for gathering machine information."""

import ctypes
import logging
import platform
import subprocess

import psutil

from pyclashbot.utils.subprocess import run


def safe_get_user32():
    """Safely get user32 dll, return None if failed."""
    try:
        return ctypes.windll.user32
    except Exception:
        return None


def safe_get_screen_metrics(user32_dll, metric_index: int) -> int:
    """Safely get screen metrics, raise exception if failed."""
    if user32_dll is None:
        raise RuntimeError("User32 DLL not available")
    
    try:
        return user32_dll.GetSystemMetrics(metric_index)
    except Exception as e:
        raise RuntimeError(f"Failed to get screen metrics for index {metric_index}") from e


def check_hyper_v_enabled() -> bool:
    """Check if Hyper-V is enabled on the system."""
    try:
        _, result = run(
            [
                "powershell",
                '"Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V"',
            ],
        )

        # Check if Hyper-V is enabled based on the output
        return "State : Enabled" in result
    except (subprocess.CalledProcessError, Exception):
        return False


def safe_get_machine_info() -> dict:
    """Safely gather machine information with fallbacks for failures."""
    info = {}
    
    # Platform information - with consistent error handling
    try:
        info["os"] = platform.system()
    except Exception as e:
        logging.warning(f"Failed to get OS info: {e}")
        info["os"] = "UNKNOWN"
    
    try:
        info["os_version"] = platform.version()
    except Exception as e:
        logging.warning(f"Failed to get OS version: {e}")
        info["os_version"] = "UNKNOWN"
    
    try:
        info["os_machine"] = platform.machine()
    except Exception as e:
        logging.warning(f"Failed to get machine info: {e}")
        info["os_machine"] = "UNKNOWN"
    
    try:
        info["architecture"] = platform.architecture()[0]
    except (IndexError, Exception) as e:
        logging.warning(f"Failed to get architecture info: {e}")
        info["architecture"] = "UNKNOWN"
    
    try:
        info["processor"] = platform.processor()
    except Exception as e:
        logging.warning(f"Failed to get processor info: {e}")
        info["processor"] = "UNKNOWN"
    
    # Screen information - handle exceptions properly
    try:
        user32 = safe_get_user32()
        width = safe_get_screen_metrics(user32, 0)
        height = safe_get_screen_metrics(user32, 1)
        info["screensize"] = f"{width}, {height}"
        
        full_width = safe_get_screen_metrics(user32, 78)
        full_height = safe_get_screen_metrics(user32, 79)
        info["full_screensize"] = f"{full_width}, {full_height}"
    except RuntimeError as e:
        logging.warning(f"Failed to get screen metrics: {e}")
        info["screensize"] = "UNAVAILABLE"
        info["full_screensize"] = "UNAVAILABLE"
    
    # Memory information
    try:
        info["memory"] = int(psutil.virtual_memory().total)
    except Exception as e:
        logging.warning(f"Failed to get memory info: {e}")
        info["memory"] = -1
    
    # CPU information
    try:
        cpu_count = psutil.cpu_count(logical=False)
        info["cpu_count"] = int(cpu_count) if cpu_count is not None else 0
    except Exception as e:
        logging.warning(f"Failed to get CPU count: {e}")
        info["cpu_count"] = -1
    
    try:
        cpu_freq = psutil.cpu_freq()
        info["cpu_freq"] = float(cpu_freq.current if cpu_freq else 0.0)
    except Exception as e:
        logging.warning(f"Failed to get CPU frequency: {e}")
        info["cpu_freq"] = -1.0
    
    # Hyper-V check
    try:
        info["hyper-v_enabled"] = check_hyper_v_enabled()
    except Exception as e:
        logging.warning(f"Failed to check Hyper-V status: {e}")
        info["hyper-v_enabled"] = False
    
    return info


MACHINE_INFO: dict = safe_get_machine_info()

if __name__ == "__main__":
    print(MACHINE_INFO)
