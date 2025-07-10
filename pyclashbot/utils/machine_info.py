"""A module for gathering machine information."""

import configparser
import ctypes
import logging
import platform
import subprocess
from os.path import join

import psutil

from pyclashbot.memu.pmc import pmc
from pyclashbot.utils.subprocess import run

user32 = ctypes.windll.user32


memu_config = configparser.ConfigParser()
memu_config.read(
    join(pmc._get_memu_top_level(), "config.ini"),  # pylint: disable=protected-access
)


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
    except subprocess.CalledProcessError as e:
        logging.exception("Error executing command: %s", e)
        return False


MACHINE_INFO: dict[str, str | int | float] = {
    "os": platform.system(),
    "os_version": platform.version(),
    "os_machine": platform.machine(),
    "architecture": platform.architecture()[0],
    "processor": platform.processor(),
    "screensize": f"{user32.GetSystemMetrics(0)}, {user32.GetSystemMetrics(1)}",
    "full_screensize": f"{user32.GetSystemMetrics(78)}, {user32.GetSystemMetrics(79)}",
    "memory": int(psutil.virtual_memory().total),
    "cpu_count": int(psutil.cpu_count(logical=False)),
    "cpu_freq": float(psutil.cpu_freq().current),
    "memu_version": memu_config.get("reginfo", "version", fallback="unknown"),
    "hyper-v_enabled": check_hyper_v_enabled(),
}

if __name__ == "__main__":
    print(MACHINE_INFO)
