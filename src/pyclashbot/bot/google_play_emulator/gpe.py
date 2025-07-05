import subprocess
import time

CLASH_ROYALE_PACKAGE = "com.supercell.clashroyale"


def adb(command):
    """Runs an adb command and returns the result."""
    return subprocess.run(f"adb {command}", shell=True, check=True)


def close_clash_royale_app():
    """Force stops the Clash Royale app."""
    print("Closing Clash Royale...")
    adb(f"shell am force-stop {CLASH_ROYALE_PACKAGE}")


def start_clash_royale():
    """Launches the Clash Royale app."""
    print("Starting Clash Royale...")
    adb(f"shell monkey -p {CLASH_ROYALE_PACKAGE} -c android.intent.category.LAUNCHER 1")


def is_connected():
    """Returns True if emulator is connected and not offline."""
    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    for line in result.stdout.strip().splitlines():
        if "localhost:6520" in line and "device" in line:
            return True
    return False


def connect():
    print("Connecting...")
    subprocess.run("adb disconnect localhost:6520", shell=True)
    subprocess.run("adb connect localhost:6520", shell=True)
    time.sleep(1)

    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    if "offline" in result.stdout:
        raise Exception("ADB device is offline.")
    print(result.stdout)


def click(x, y):
    adb(f"shell input tap {x} {y}")


def screenshot(output_path="screen.png"):
    adb("shell screencap -p /sdcard/screen.png")
    adb(f"pull /sdcard/screen.png {output_path}")


def swipe(x1, y1, x2, y2, duration_ms=300):
    adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration_ms}")


def set_screen_size(width, height):
    """
    Sets the emulator screen resolution (e.g., 1080x1920).
    May require reboot or app restart depending on the app.
    """
    print(f"Setting screen size to {width}x{height}...")
    adb(f"shell wm size {width}x{height}")


if __name__ == "__main__":
    connect()
    set_screen_size(900, 900)

