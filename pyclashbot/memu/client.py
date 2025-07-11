"""Module for interacting with the memu client"""  # noqa: INP001

import time

from numpy import ndarray

from pyclashbot.memu.pmc import pmc
from pyclashbot.memu.screenshot import memu_screen_capture


def save_screenshot(vm_index):
    image_name = f"image{vm_index}.png"
    print(
        pmc.send_adb_command_vm(
            vm_index=vm_index,
            command=f"exec-out screencap -p /sdcard/pictures/{image_name}",
        ),
    )


def screenshot(vm_index: int) -> ndarray:
    """Method to return a screenshot of a given region

    Args:
    ----
        vm_index (int): Index of the VM to take a screenshot of

    Returns:
    -------
        numpy.ndarray: Screenshot of the given region

    """
    return memu_screen_capture[vm_index]


def click(vm_index, x_coord, y_coord, clicks=1, interval=0.1):
    """Method for clicking a given coordinate

    Args:
    ----
        vm_index (int): Index of the VM to click on
        x_coord (int): X coordinate of the click
        y_coord (int): Y coordinate of the click
        clicks (int, optional): Amount of clicks. Defaults to 1.
        interval (float, optional): Interval between clicks. Defaults to 0.1.

    """
    if clicks == 1:
        send_click(vm_index, x_coord, y_coord)
    else:
        for _ in range(clicks):
            send_click(vm_index, x_coord, y_coord)
            time.sleep(interval)


def scroll(vm_index, start_x, start_y, end_x, end_y):
    send_swipe(vm_index, start_x, start_y, end_x, end_y)


def scroll_up_fast(vm_index):
    """Method for scrolling up faster when interacting with a scrollable menu"""
    send_swipe(vm_index, 215, 100, 215, 500)


def custom_swipe(vm_index, start_x, start_y, end_x, end_y, count=1, delay=0):
    for _ in range(count):
        send_swipe(vm_index, start_x, start_y, end_x, end_y)
        time.sleep(delay)


def scroll_up(vm_index):
    """Method for scrolling up faster when interacting with a scrollable menu"""
    send_swipe(vm_index, 215, 300, 215, 400)


def scroll_up_a_little(vm_index):
    send_swipe(vm_index, 215, 300, 215, 320)


def scroll_up_on_left_side_of_screen(vm_index):
    """Method for scrolling up faster when interacting with a scrollable menu"""
    send_swipe(vm_index, 66, 300, 66, 400)


def scroll_down(vm_index):
    """Method for scrolling down faster when interacting with a scrollable menu"""
    send_swipe(vm_index, 215, 400, 215, 300)

    # click deadspace to stop the scroll
    click(vm_index, 10, 200)


def scroll_down_in_request_page(vm_index):
    """Method for scrolling down faster when interacting with a scrollable menu"""
    # vertical swipe
    send_swipe(vm_index, 43, 350, 43, 140)

    # horizontal swipe to stop the scroll
    send_swipe(vm_index, 100, 385, 330, 385)


def scroll_down_fast_on_left_side_of_screen(vm_index):
    """Method for scrolling down even faster when interacting with a
    scrollable menu using the left side of the screen
    """
    send_swipe(vm_index, 66, 400, 66, 300)


def scroll_slowly_in_shop_page(vm_index, direction):
    """Method for scrolling down even faster when interacting with a
    scrollable menu using the left side of the screen
    """
    if direction == "down":
        send_swipe(vm_index, 66, 400, 66, 200)
    else:
        send_swipe(vm_index, 66, 200, 66, 400)

    # click deadspace to stop the scroll
    click(vm_index, 10, 200)


def scroll_all_the_way_in_shop_page(vm_index, direction):
    """Method for scrolling down even faster when interacting with a
    scrollable menu using the left side of the screen
    """
    for _ in range(13):
        if direction == "up":
            print("scrolling all the way up in shop page")
            send_swipe(vm_index, 66, 60, 66, 400)
        else:
            print("scrolling all the way down in shop page")
            send_swipe(vm_index, 66, 400, 66, 60)

    # click deadspace to stop the scroll


def send_swipe(
    vm_index: int,
    x_coord1: int,
    y_coord1: int,
    x_coord2: int,
    y_coord2: int,
):
    """Method for sending a swipe command to the given vm

    Args:
    ----
        vm_index (int): Index of the vm to send the command to
        x_coord1 (int): X coordinate of the start of the swipe
        y_coord1 (int): Y coordinate of the start of the swipe
        x_coord2 (int): X coordinate of the end of the swipe
        y_coord2 (int): Y coordinate of the end of the swipe

    """
    pmc.send_adb_command_vm(
        vm_index=vm_index,
        command=f"shell input swipe {x_coord1} {y_coord1} {x_coord2} {y_coord2}",
    )


def send_click(vm_index, x_coord, y_coord):
    """Method for sending a click command to the given vm

    Args:
    ----
        vm_index (int): Index of the vm to send the command to
        x_coord (int): X coordinate of the click
        y_coord (int): Y coordinate of the click

    """
    pmc.send_adb_command_vm(
        vm_index=vm_index,
        command=f"shell input tap {x_coord} {y_coord}",
    )


def send_text(vm_index, text: str):
    """Method for sending a text command to the given vm

    Args:
    ----
        vm_index (int): Index of the vm to send the command to
        text (str): Text to send

    """
    # replace spaces with %s
    text = text.replace(" ", "%s")

    # delimiter for new lines
    delimiter = "\\n"

    # split the text into lines
    lines = text.split(delimiter)

    # if only one line of text:
    if len(lines) == 1:
        pmc.send_adb_command_vm(
            vm_index=vm_index,
            command=f"shell input text {lines[0]}",
        )
        return

    index = 0
    line_count = len(lines)
    for line in lines:
        # type the line
        pmc.send_adb_command_vm(
            vm_index=vm_index,
            command=f"shell input text {line}",
        )

        # if last line, skip adding the new line character
        if index == line_count - 1:
            break

        # add the new line
        send_newline_char(vm_index)

        index += 1


def send_newline_char(vm_index):
    """Method for sending a newline character to the given vm"""
    return pmc.send_adb_command_vm(
        vm_index=vm_index,
        command="shell input keyevent KEYCODE_NUMPAD_ENTER",
    )


def test_screenshot(vm_index):
    """
    Just tests for whether or not the image is of valid size, and isnt all black
    returns:bool: True if the image is valid, False otherwise
    """

    # grab image
    img = screenshot(vm_index)

    # check size
    width, height = img.shape[1], img.shape[0]
    expected_w, expected_h = 419, 633
    if width != expected_w or height != expected_h:
        print(f"Screenshot size is not as expected. Expected: {expected_w}x{expected_h}, got: {width}x{height}")
        return False

    # sample random pixels
    black = [255, 255, 255]
    sample_pixels = []
    for x in range(0, width - 1, 100):
        for y in range(0, height - 1, 100):
            pixel = img[y][x]
            sample_pixels.append(pixel)

    # count black pixels, false if too many
    is_black_count = sum([1 for pixel in sample_pixels if all(pixel == black)])
    is_black_ratio = is_black_count / len(sample_pixels)
    if is_black_ratio > 0.5:
        print(f"Screenshot is mostly black (ratio of {is_black_ratio}), something went wrong.")
        return False

    # image must be valid
    return True


if __name__ == "__main__":
    scroll_all_the_way_in_shop_page(0, "up")
    scroll_all_the_way_in_shop_page(0, "down")
