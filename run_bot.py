import os
import sys
import runpy
import traceback
from datetime import datetime


def setup_environment():
    """
    Make the environment inside the .app predictable:
    - Ensure PATH includes Homebrew locations (for your dev machine).
    - If bundled platform-tools exist (adb inside the app), put them on PATH.
    - This function runs before pyclashbot is imported.
    """
    # Base dir for PyInstaller bundle
    if getattr(sys, "frozen", False):
        # When frozen, sys.executable is the app's Mach-O
        base_dir = os.path.dirname(sys.executable)
        # In a one-folder bundle, PyInstaller extracts libs under _MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base_dir = meipass
    else:
        # When run as a normal script
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # 1) Fix PATH on macOS so adb is visible when launched from Finder
    if sys.platform == "darwin":
        extra_paths = [
            "/opt/homebrew/bin",  # Apple Silicon Homebrew
            "/usr/local/bin",     # Intel Homebrew / older setups
        ]
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = os.pathsep.join(extra_paths + [current_path])

    # 2) If we bundled platform-tools inside the app, prepend them to PATH
    platform_tools_dir = os.path.join(base_dir, "platform-tools")
    if os.path.isdir(platform_tools_dir):
        os.environ["PATH"] = os.pathsep.join([platform_tools_dir, os.environ["PATH"]])

    # Return base_dir in case you want it later
    return base_dir


def main():
    base_dir = setup_environment()

    try:
        # This exactly emulates: python -m pyclashbot
        runpy.run_module("pyclashbot", run_name="__main__")
    except Exception:
        # If something goes wrong when launched from Finder,
        # write the full traceback to a log file so it's debuggable.
        try:
            log_dir = os.path.expanduser("~/Library/Logs")
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "ClashBot-error.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write("\n===== ClashBot crash: {} =====\n".format(datetime.now().isoformat()))
                traceback.print_exc(file=f)
        except Exception:
            # If logging itself fails, just give up silently.
            pass
        # Re-raise so PyInstaller exits instead of hanging
        raise


if __name__ == "__main__":
    main()