import subprocess

from cx_Freeze import Executable, setup

PRODUCT_NAME = "pycb"

try:
    VERSION = str(
        subprocess.check_output(
            ["git", "describe", "--abbrev=0"], stderr=subprocess.STDOUT
        )
    ).strip("'b\\n")
except subprocess.CalledProcessError:
    VERSION = "0.0.0"

build_exe_options = {
    "include_msvcr": True,
    "excludes": [
        "PySimpleGUI",
        "tkinter",
        "test",
        "setuptools",
        "pyclashbot.interface",
        "matplotlib",
    ],
}

exe = Executable(
    script="pyclashbot\\server.py",
    base="Win32GUI",  # none for debugging
    target_name=f"{PRODUCT_NAME}_back.exe",
)

setup(
    name=PRODUCT_NAME,
    version=VERSION,
    executables=[exe],
    options={"build_exe": build_exe_options},
)
