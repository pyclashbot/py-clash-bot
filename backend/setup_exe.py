import subprocess

from cx_Freeze import Executable, setup

PRODUCT_NAME = "neoui"

try:
    VERSION = str(
        subprocess.check_output(
            ["git", "describe", "--abbrev=0"], stderr=subprocess.STDOUT
        )
    ).strip("'b\\n")
except subprocess.CalledProcessError:
    VERSION = "0.0.0"

build_exe_options = {"excludes": ["tkinter", "test", "unittest", "setuptools"]}

exe = Executable(
    script="bot\\__main__.py",
    base="Win32GUI",  # none for debugging
    target_name=f"{PRODUCT_NAME}_back.exe",
)

setup(
    name=PRODUCT_NAME,
    version=VERSION,
    executables=[exe],
    options={"build_exe": build_exe_options},
)
