import webbrowser
import pygetwindow as gw
import os
import subprocess
import time
import subprocess
import numpy as np
import FreeSimpleGUI as sg
import cv2

from pyclashbot.google_play_emulator.gpe_path_manager import GPEPathManager

gpe_path_manager = GPEPathManager()
CLASH_ROYALE_PACKAGE = "com.supercell.clashroyale"
EMULATOR_PATH = gpe_path_manager.get_emulator_path()
EXPECTED_SCREEN_DIMS = (419, 633)
GOOGLE_PLAY_PROCESS_NAME = "Google Play Games on PC Emulator"  # window title keyword
ADB_INSTRUCTIONS_LINK = "https://docs.google.com/document/d/1tOtS39xtcIYMwFraxiEL3UhXKFPvOX_rDwON1iyxiOY/edit?usp=sharing"


def adb(command):
    """Runs an adb command, prints and returns its output."""
    result = subprocess.run(
        f"adb {command}", shell=True, capture_output=True, text=True
    )

    return result


def invalid__gpe_ratio_popup():
    layout = [
        [sg.Text("Warning! Your Google Play Emulator aspect ratio is invalid.")],
        [sg.Text("Please ensure the emulator is running in the correct orientation.")],
        # lets make an image
        [
            sg.Image(
                filename=r"src\pyclashbot\google_play_emulator\assets\display_ratio_tut_image.png"
            )
        ],
        [
            sg.Text(
                "Right click the Google Play Emulator from your system tray to\nmanually adjust the display ratio to 9:16 (Portrait)!\nThen, restart the bot."
            )
        ],
        [
            sg.Button("Continue"),
        ],
    ]

    window = sg.Window("Invalid GPE Ratio", layout, modal=True)

    while True:
        event, _ = window.read()
        print(f"Event: {event}")
        if event in (sg.WIN_CLOSED, "Continue"):
            print("closing invalid gpe ratio popup")
            break

    window.close()


def missing_adb_installation_popup():
    layout = [
        [sg.Text("Warning!")],
        [
            sg.Text(
                "ADB is not installed, or not set in your PATH environment\nvariable."
            )
        ],
        [sg.Image(filename=r"src\pyclashbot\google_play_emulator\assets\adb_logo.png")],
        [
            sg.Button("Intructions"),
            sg.Button("Install Link"),
            sg.Button("Continue"),
        ],
    ]

    window = sg.Window("Invalid ADB Installation", layout, modal=True)

    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Continue"):
            break
        elif event == "Intructions":
            webbrowser.open(ADB_INSTRUCTIONS_LINK)
        elif event == "Install Link":
            webbrowser.open(
                "https://developer.android.com/studio/releases/platform-tools"
            )

    window.close()


def validate_display_ratio():
    if not valid_gpe_ratio():
        invalid__gpe_ratio_popup()


def close_clash_royale_app():
    """Force stops the Clash Royale app."""
    start_time = time.time()
    print("Closing Clash Royale...")
    adb(f"shell am force-stop {CLASH_ROYALE_PACKAGE}")
    print(f"Closed Clash Royale in {time.time() - start_time:.2f} seconds")


def start_clash_royale():
    """Launches the Clash Royale app."""
    start_time = time.time()
    print("Starting Clash Royale...")
    output = adb(
        f"shell monkey -p {CLASH_ROYALE_PACKAGE} -c android.intent.category.LAUNCHER 1"
    )
    print(f"Started Clash Royale in {time.time() - start_time:.2f} seconds")


def is_connected():
    """Returns True if emulator is connected and not offline."""
    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    for line in result.stdout.strip().splitlines():
        print(line)
        if "localhost:6520" in line and "device" in line:
            return True
    return False


def test_abd():
    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    std_out = result.stdout.strip()
    error = result.stderr.strip()
    if "'adb' is not recognized as an internal or external command" in error:
        print(f"Looks like adb isnt installed")
        missing_adb_installation_popup()


def connect():
    print("Connecting...")
    subprocess.run("adb disconnect localhost:6520", shell=True)
    subprocess.run("adb connect localhost:6520", shell=True)
    time.sleep(1)

    result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    if "offline" in result.stdout:
        print("[!] Emulator is offline. Please check the connection.")

    elif "localhost:6520" in result.stdout and "device" in result.stdout:
        print("Connected to emulator at localhost:6520")
        return True

    return False


def click(x, y, clicks=1, interval=0.1):
    for i in range(clicks):
        adb(f"shell input tap {x} {y}")
        if clicks == 1:
            break
        time.sleep(interval)


def screenshot():
    """
    Captures a screenshot from the emulator and returns it as a NumPy BGR image (OpenCV format).
    """

    result = subprocess.run(
        "adb exec-out screencap -p", shell=True, capture_output=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"ADB screenshot failed: {result.stderr.decode()}")

    # Convert bytes to NumPy array
    img_array = np.frombuffer(result.stdout, dtype=np.uint8)

    # Decode PNG to image
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # bgr to rgb
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if img is None:
        raise ValueError("Failed to decode screenshot")

    return img


def scroll(x1, y1, x2, y2, duration_ms=300):
    adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration_ms}")


def set_screen_size(width, height):
    print(f"Setting screen size to {width}x{height}...")
    adb(f"shell wm size {width}x{height}")


def resize_emualtor(width=None, height=None):
    default = EXPECTED_SCREEN_DIMS
    if None in [width, height]:
        width, height = default
    print(f"Resizing emulator to {width}x{height}...")
    set_screen_size(width, height)


def close_emulator():
    """
    Closes the Google Play Games Developer Emulator by killing the 'crosvm.exe' process.
    """
    print("Closing emulator (crosvm.exe)...")
    result = subprocess.run(
        'taskkill /f /im "crosvm.exe"', shell=True, capture_output=True, text=True
    )

    if result.returncode == 0:
        print("Emulator closed successfully.")
    else:
        # print(f"Failed to close emulator:\n{result.stderr.strip()}")
        pass


def start_emulator():
    """
    Starts the emulator using the Windows shell to open the shortcut.
    """
    print("Starting emulator...")

    if not os.path.exists(EMULATOR_PATH):
        raise FileNotFoundError(f"Emulator shortcut not found at: {EMULATOR_PATH}")

    os.startfile(EMULATOR_PATH)
    time.sleep(5)


def restart_emulator(logger=None):
    start_time = time.time()

    # close emulator
    if logger is None:print("Restarting emulator...")
    else: logger.log("Restarting emulator...")
    while is_emulator_running():
        if logger is None:print("Closing emulator...")
        else:logger.log("Closing emulator...")
        close_emulator()

    # boot emulator
    if logger is None:print("Starting emulator...")
    start_emulator()
    while not is_emulator_running():
        if logger is None:print("Waiting for emulator to start...")
        else:logger.log("Waiting for emulator to start...")
        time.sleep(0.3)

    # wait for window to appear
    while find_window(GOOGLE_PLAY_PROCESS_NAME) is None:
        if logger is None:print("Waiting for emulator window to appear...")
        else:logger.log("Waiting for emulator window to appear...")
        time.sleep(0.3)

    # reconect to adb
    while not is_connected():
        connect()

    # configure emulator
    for i in range(3):
        resize_emualtor()
        time.sleep(1)

    # validate emulator
    validate_display_ratio()

    # validate image size
    if not valid_screen_size(EXPECTED_SCREEN_DIMS):
        if logger is None:print(
            f"[!] Warning! Emulator screen size is not {EXPECTED_SCREEN_DIMS}. "
            "Please check the emulator settings."
        )
        else:logger.log(
            f"[!] Warning! Emulator screen size is not {EXPECTED_SCREEN_DIMS}. "
            "Please check the emulator settings."
        )

    if logger is None:print(f"testing adb...")
    else:logger.log(f"testing adb...")
    test_abd()
    if logger is None:print(f"tested adb")
    else:logger.log(f"tested adb")


    if logger is None:print(f"Fully restarted emulator in {time.time() - start_time:.2f} seconds")
    else:logger.log(f"Fully restarted emulator in {time.time() - start_time:.2f} seconds")


def is_emulator_running():
    result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
    return "crosvm.exe" in result.stdout


def test_screenshot():
    """
    Displays a screenshot. Shows pixel coords and color on hover.
    Prints [x, y] : [r, g, b] on left-click.
    Press any key to exit.
    """
    connect()

    img = screenshot()
    print(f"Got a screenshot of size {img.shape[0]}x{img.shape[1]}")

    window_name = "Screenshot"

    def mouse_handler(event, x, y, flags, param):
        b, g, r = img[y, x]
        # if event == cv2.EVENT_MOUSEMOVE:
        # print(f"Mouse at ({x}, {y}) ({r}, {g}, {b})", end='\r')

        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"[{x},{y}] : [{b}, {g},{r}]")

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_handler)

    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def valid_screen_size(expected_dims: tuple):
    # reverse expected_dims just because that's how cv2 works
    print("Validating screen size...")
    expected_dims = (expected_dims[1], expected_dims[0])
    image = screenshot()
    dims = image.shape[:2]
    print(f"Image of size {dims} received, expected {expected_dims}")
    if dims != expected_dims:
        return False

    return True


def find_window(title_keyword):
    windows = gw.getWindowsWithTitle(title_keyword)
    return windows[0] if windows else None


def get_google_play_dims():
    win = find_window(GOOGLE_PLAY_PROCESS_NAME)
    return (win.width, win.height) if win else (0, 0)


def valid_gpe_ratio():
    dims = get_google_play_dims()
    if 0 in dims:
        print(
            "[!] Warning! Google Play Emulator window not found or has zero dimensions."
        )
        return False
    ratio = dims[0] / dims[1]

    print(f"Read dims of {dims} with ratio of {ratio}")

    # landscape = 5.714285714285714
    # portrait = 0.5551643192488263

    if ratio > 1 or ratio < 0.3:
        return False

    return True


if __name__ == "__main__":
    test_abd()
