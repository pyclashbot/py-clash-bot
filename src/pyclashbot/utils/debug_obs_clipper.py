import time
import pygetwindow as gw
import pyautogui


def obs_window_exists():
    if get_obs_window_name() is None:
        return False
    return True


def get_obs_window_name():
    ws = gw.getAllTitles()
    for w in ws:
        if "OBS" in w and "(64-bit, windows)" in w:
            return w
    return None


def orientate_obs_window():
    try:
        window_name = get_obs_window_name()

        if window_name is None:
            return False

        window = gw.getWindowsWithTitle(window_name)[0]

        if window is None:
            return False

        window.resizeTo(200, 200)
        window.moveTo(0, 970)
    except:
        return False

    return True


def clip_that():
    if not obs_window_exists():
        return False

    if not orientate_obs_window():
        return False

    time.sleep(2)

    # click save replay button
    origin = pyautogui.position()
    pyautogui.click(856, 1248)
    time.sleep(0.2)
    pyautogui.moveTo(origin.x, origin.y)
    time.sleep(0.2)

    for _ in range(10):
        print('Saved an obs clip!!!')


if __name__ == "__main__":
    print(orientate_obs_window())


