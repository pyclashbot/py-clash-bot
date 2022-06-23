

import time

from pyclashbot.client import (check_quit_key_press, click, screenshot,
                               scroll_down, scroll_down_fast, scroll_up_fast)
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location)


def collect_bp(logger):
    time.sleep(1)
    logger.log("Collecting battlepass rewards")
    time.sleep(0.5)
    logger.log("Opening battlepass tab from clash main.")
    click(190, 150)
    time.sleep(2)
    # loops 5 times just bc
    logger.log("Beginning collection loop.")
    n = 5
    while n > 0:
        check_quit_key_press()
        n = n - 1
        coords = find_claim_buttons_with_duration()
        if coords is None:
            logger.log("No claim buttons found. Scrolling")
            scroll_down()
            time.sleep(1)

        else:
            logger.log("Claim coord found. Clicking it.")
            click(coords[1], coords[0] + 50)
            time.sleep(1)
            click(25, 100, clicks=20, interval=0.3)
            time.sleep(1)
            scroll_down()
            time.sleep(1)
    logger.log("Finished with collection loop.")
    time.sleep(1)
    click(210, 630)


def find_claim_buttons():
    check_quit_key_press()
    current_image = screenshot()
    reference_folder = "battlepass_claim_buttons"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",
        "14.png",
        "15.png",
        "16.png",
        "17.png",
        "18.png",
        "19.png",
        "20.png",
        "21.png",
        "22.png",
        "23.png",
        "24.png",
        "25.png",
        "26.png",
        "27.png",
        "28.png",
        "29.png",
        "30.png",
        "31.png",
        "32.png",
        "t1.png",
        "t2.png",
        "t3.png",
        "t4.png",
        "t5.png",
        "t6.png",
        "t7.png",
        "t8.png",
        "t9.png",
        "t10.png",
        "t11.png",
        "t12.png",
        "t13.png",
        "t14.png",
        "t15.png",
        "t16.png",
        "t17.png",
        "t18.png",
        "t19.png",
        "t20.png",
        "t21.png",
        "t22.png",
        "t23.png",
        "t24.png",
        "t25.png",
        "t26.png",
        "t27.png",
        "t28.png",
        "t29.png",
        "t30.png",
        "t31.png",
        "t32.png",
        "t33.png",
        "t34.png",
        "t35.png",
        "t36.png",
        "t37.png",
        "t38.png",
        "t39.png",
        "t40.png",
        "t41.png",
        "t42.png",
        "t43.png",
        "t44.png",
        "t45.png",
        "t46.png",
        "t47.png",
        "t48.png",
        "t49.png",
        "t50.png",
        "t51.png",
        "t52.png",
        "t53.png",
        "t54.png",
        "t55.png",
        "t56.png",
        "t57.png",
        "t58.png",
        "t59.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    return get_first_location(locations)


def find_claim_buttons_with_duration():
    n = 20
    coords = None
    while (n > 0) and (coords is None):
        n = n - 1
        coords = find_claim_buttons()
        time.sleep(0.2)
    return coords


def check_if_can_collect_bp():
    check_quit_key_press()
    current_image = screenshot()
    reference_folder = "claim_bp_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    return check_for_location(locations)
