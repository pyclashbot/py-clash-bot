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
        "e1.png",
        "e2.png",
        "e3.png",
        "e4.png",
        "e5.png",
        "e6.png",
        "e7.png",
        "e8.png",
        "e9.png",
        "e10.png",
        "e11.png",
        "e12.png",
        "e13.png",
        "e14.png",
        "e15.png",
        "e16.png",
        "e17.png",
        "e18.png",
        "e19.png",
        "e20.png",
        "e21.png",
        "e22.png",
        "e23.png",
        "e24.png",
        "e25.png",
        "e26.png",
        "e27.png",
        "e28.png",
        "e29.png",
        "e30.png",
        "e31.png",
        "e32.png",
        "e33.png",
        "e34.png",
        "e35.png",
        "e36.png",
        "e37.png",
        "e38.png",
        "e39.png",
        "e40.png",
        "e41.png",
        "e42.png",
        "e43.png",
        "e44.png",
        "e45.png",
        "e46.png",
        "e47.png",
        "e48.png",
        "e49.png",
        "e50.png",
        "e51.png",
        "e52.png",
        "e53.png",
        "e54.png",
        "e55.png",
        "e56.png",
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
    n = 10
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
