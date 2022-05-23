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
    current_image = screenshot()
    reference_folder = "unlocking_chest_images"
    references = [
        "clock1.png",
        "clock2.png",
        "clock3.png",
        "clock4.png",
        "clock5.png",
        "clock6.png",
        "clock7.png",
        "clock8.png",
        "clock9.png",
        "clock10.png",
        "clock11.png",
        "clock12.png",
        "clock13.png",
        "clock14.png",
        "clock15.png",
        "clock16.png",
        "clock17.png",
        "clock18.png",
        "clock19.png",
        "clock20.png",
        "clock21.png",
        "clock22.png",
        "clock23.png",
        "clock24.png",
        "clock25.png",
        "clock26.png",
        "clock27.png",
        "clock28.png",
        "clock29.png",
        "clock30.png",
        "clock31.png",
        "clock32.png",
        "clock33.png",
        "clock34.png",
        "clock35.png",
        "clock36.png",
        "clock37.png",
        "clock38.png",
        "clock39.png",
        "clock40.png",
        "clock41.png",
        "clock42.png",
        "clock43.png",
        "clock44.png",
        "clock45.png",
        "clock46.png",
        "clock47.png",
        "clock48.png",
        "clock49.png",
        "clock50.png",
        "clock51.png",
        "clock52.png",
        "clock53.png",
        "clock54.png",
        "clock55.png",
        "clock56.png",
        "clock57.png",
        "clock58.png",
        "clock59.png",
        "clock60.png",
        "clock61.png",
        "clock62.png",
        "clock63.png",
        "clock64.png",
        "clock65.png",
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
    n=5
    while n != 0:
        if look_for_clock():
            return True
        else:
            n=n-1
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
