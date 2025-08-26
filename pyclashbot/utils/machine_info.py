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


def safe_get_screen_metrics(user32_dll, metric_index: int) -> str:
    """Safely get screen metrics, return warning if failed."""
    try:
        if user32_dll is None:
            return "UNAVAILABLE"
        return str(user32_dll.GetSystemMetrics(metric_index))
    except Exception:
        return "ERROR"


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


def safe_get_machine_info() -> dict[str, str | int | float]:
    """Safely gather machine information with fallbacks for failures."""
    info: dict[str, str | int | float] = {}
    
    # Platform information
    try:
        info["os"] = platform.system()
    except Exception:
        info["os"] = "UNKNOWN"
    
    try:
        info["os_version"] = platform.version()
    except Exception:
        info["os_version"] = "UNKNOWN"
    
    try:
        info["os_machine"] = platform.machine()
    except Exception:
        info["os_machine"] = "UNKNOWN"
    
    try:
        info["architecture"] = platform.architecture()[0]
    except Exception:
        info["architecture"] = "UNKNOWN"
    
    try:
        info["processor"] = platform.processor()
    except Exception:
        info["processor"] = "UNKNOWN"
    
    # Screen information
    user32 = safe_get_user32()
    width = safe_get_screen_metrics(user32, 0)
    height = safe_get_screen_metrics(user32, 1)
    info["screensize"] = f"{width}, {height}"
    
    full_width = safe_get_screen_metrics(user32, 78)
    full_height = safe_get_screen_metrics(user32, 79)
    info["full_screensize"] = f"{full_width}, {full_height}"
    
    # Memory information
    try:
        info["memory"] = int(psutil.virtual_memory().total)
    except Exception:
        info["memory"] = -1
    
    # CPU information
    try:
        info["cpu_count"] = int(psutil.cpu_count(logical=False) or 0)
    except Exception:
        info["cpu_count"] = -1
    
    try:
        cpu_freq = psutil.cpu_freq()
        info["cpu_freq"] = float(cpu_freq.current if cpu_freq else 0.0)
    except Exception:
        info["cpu_freq"] = -1.0
    
    # Hyper-V check
    try:
        info["hyper-v_enabled"] = check_hyper_v_enabled()
    except Exception:
        info["hyper-v_enabled"] = False
    
    return info


MACHINE_INFO: dict[str, str | int | float] = safe_get_machine_info()

if __name__ == "__main__":
    print(MACHINE_INFO)
