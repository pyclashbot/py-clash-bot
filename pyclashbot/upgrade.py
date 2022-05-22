import time

from pyclashbot.client import click, screenshot, scroll_down
from pyclashbot.image_rec import find_references
from pyclashbot.state import check_if_on_clash_main_menu


def look_for_upgrades():
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
        "33.png",
        "34.png",
        "35.png",
        "36.png",
        "37.png",
        "38.png",
        "39.png",
        "40.png",
        "41.png",
        "42.png",
        "43.png",
        "44.png",
        "45.png",
        "46.png",
        "47.png",
        "48.png",
        "49.png",
        "50.png",
        "51.png",
        "52.png",
        "53.png",
        "54.png",
        "55.png",
        "56.png",
        "57.png",
        "58.png",
        "59.png",
        "60.png",
        "61.png",
        "62.png",
        "63.png",
        "64.png",
        "65.png",
        "66.png",
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="green_upgrade_button",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            # click(location[1],location[0])
            return location
    return None


def upgrade_cards_from_main():
    n = 0
    coords = look_for_upgrades()
    if coords is not None:
        click(coords[1], coords[0])
        time.sleep(0.2)
        coords = look_for_upgrade_button()
        if coords is not None:
            click(coords[1], coords[0])
            time.sleep(0.2)
    else:
        while (n < 20) and (coords is not None):
            scroll_down()
            coords = look_for_upgrades()
            time.sleep(0.2)
            n = n+1
        if coords is not None:
            click(coords[1], coords[0])
            time.sleep(0.2)
            coords = look_for_upgrade_button()
            if coords is not None:
                click(coords[1], coords[0])
                time.sleep(0.2)


def look_for_upgrade_button():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="upgrade_button",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return location
    return None


def get_to_card_page(logger):
    if not check_if_on_clash_main_menu():
        logger.log("Not on clash main.")
        return "quit"
    coords = find_card_page_logo()
    if coords is None:
        logger.log("Trouble locating card page.")
        return "quit"
    click(coords[1], coords[0])


def find_card_page_logo():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="card_page_logo",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            # click(location[1],location[0])
            return location
    return None
