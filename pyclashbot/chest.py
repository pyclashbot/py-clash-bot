import time

from pyclashbot.client import check_quit_key_press, click, screenshot
from pyclashbot.image_rec import find_references


def check_if_unlock_chest_button_exists():
    current_image = screenshot()
    reference_folder = "unlock_chest_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png"
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            # found a location
            click(x=210, y=455)

            return True
    return False


def look_for_clock():
    current_image = screenshot(region=(35, 490, 360, 40))
    reference_folder = "unlocking_chest_images"
    references = [
        "chest_unlocking_1.png",
        "chest_unlocking_2.png",
        "chest_unlocking_3.png",
        "chest_unlocking_4.png",
        "chest_unlocking_5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            # found a location
            return True
    return False


def check_if_has_chest_unlocking():
    n = 5
    while n != 0:
        if look_for_clock():
            return True
        else:
            n = n-1
            time.sleep(0.2)


def open_chests(logger):
    logger.log("clicking chest1")
    click(78, 554)

    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    click(20, 556, 20, 0.05)
    logger.log("clicking chest2")
    click(162, 549)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    click(20, 556, 20, 0.05)

    logger.log("clicking chest3")
    click(263, 541)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    click(20, 556, 20, 0.05)
    logger.log("clicking chest4")
    click(349, 551)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    click(20, 556, 20, 0.05)
