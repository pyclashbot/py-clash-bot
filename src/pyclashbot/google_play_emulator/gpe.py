import os
import subprocess
import time
import subprocess
import numpy as np
import cv2

from pyclashbot.google_play_emulator.gpe_path_manager import GPEPathManager

gpe_path_manager = GPEPathManager()
CLASH_ROYALE_PACKAGE = "com.supercell.clashroyale"
EMULATOR_PATH = gpe_path_manager.get_emulator_path()
EXPECTED_SCREEN_DIMS = (419, 633)


def adb(command):
    """Runs an adb command, prints and returns its output."""
    result = subprocess.run(
        f"adb {command}", shell=True, capture_output=True, text=True
    )

    return result


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


def connect():
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


def restart_emulator():
    start_time = time.time()

    # close emulator
    print("Restarting emulator...")
    while is_emulator_running():
        print("Emulator is running, closing it...")
        close_emulator()

    # boot emulator
    start_emulator()
    while not is_emulator_running():
        print("waiting for emualtor boot...")
        time.sleep(0.3)
    print("Emulator back running!")

    # reconect to adb
    while not is_connected():
        connect()
        print("Done connecting to emulator")

    # configure emulator
    for i in range(3):
        resize_emualtor()
        time.sleep(1)

    print("Done resizing emulator")

    print(f"Fully restarted emulator in {time.time() - start_time:.2f} seconds")


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
    expected_dims = (expected_dims[1], expected_dims[0])
    image = screenshot()
    dims = image.shape[:2]
    print(f"Image of size {dims} received, expected {expected_dims}")
    if dims != expected_dims:
        return False

    return True


if __name__ == "__main__":
    # test_screenshot()
    # start_clash_royale()
    print(valid_screen_size((633, 419)))
