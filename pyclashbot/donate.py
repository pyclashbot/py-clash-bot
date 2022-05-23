import time

from pyclashbot.client import (check_quit_key_press, click, refresh_screen,
                               screenshot, scroll_down)
from pyclashbot.image_rec import find_references
from pyclashbot.state import (check_if_on_clan_chat_page,
                              return_to_clash_main_menu)


def find_donates():
    references = [
        "donate_button_1.png",
        "donate_button_2.png",
        "donate_button_3.png",
        "donate_button_4.png",
        "donate_button_5.png",
        "donate_button_6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",
        "14.png",
        "15.png",
        "18.png",
        "19.png",
        "20.png",
    ]

    loops = 0
    while loops < 3:
        locations = find_references(
            screenshot=refresh_screen(),
            folder="donate",
            names=references,
            tolerance=0.99
        )
        for location in locations:
            if location is not None:
                return location
        scroll_down()
        loops = loops + 1
    return None


def click_donates(logger):

    # find+click donate
    donate_button_loc = find_donates()
    if donate_button_loc is not None:
        logger.log("Found a donate coord. Clicking it")
        click(x=donate_button_loc[1],
              y=donate_button_loc[0], clicks=3, interval=0.25)
        time.sleep(1)
    # find + click more donates button
    more_donates_button_loc = check_if_more_donates()
    if more_donates_button_loc is not None:
        logger.log("Detected off-screen donates. Clicking it")
        click(x=more_donates_button_loc[1], y=more_donates_button_loc[0])
        time.sleep(1)
    # find+click donate
    donate_button_loc = find_donates()
    if donate_button_loc is not None:
        logger.log("Found a donate coord. Clicking it")
        click(x=donate_button_loc[1],
              y=donate_button_loc[0], clicks=3, interval=0.25)
        time.sleep(1)
    # find + click more donates button
    more_donates_button_loc = check_if_more_donates()
    if more_donates_button_loc is not None:
        logger.log("Detected off-screen donates. Clicking it")
        click(x=more_donates_button_loc[1], y=more_donates_button_loc[0])
        time.sleep(1)
    # find+click donate
    donate_button_loc = find_donates()
    if donate_button_loc is not None:
        logger.log("Found a donate coord. Clicking it")
        click(x=donate_button_loc[1],
              y=donate_button_loc[0], clicks=3, interval=0.25)
        time.sleep(1)
    # find+click 'scroll to bottom arrow button'
    down_arrow_loc = check_if_clan_chat_down_arrow_exists()
    if down_arrow_loc is not None:
        logger.log("Found 'page to bottom' arrow. Clicking it")
        click(x=down_arrow_loc[1], y=down_arrow_loc[0])

    time.sleep(0.2)
    return_to_clash_main_menu()


def check_if_clan_chat_down_arrow_exists():
    current_image = screenshot()
    reference_folder = "check_if_clan_chat_down_arrow_exists"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    for location in locations:
        if location is not None:
            return location  # found a location
    return None


def getto_donate_page(logger):
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    click(317, 627)

    time.sleep(1)
    loops = 0
    while (not check_if_on_clan_chat_page()) and (loops < 20):
        time.sleep(1)
        click(x=317, y=627)

        time.sleep(1)
        click(x=393, y=580)

        time.sleep(1)
        loops = loops + 1
        check_quit_key_press()
    if check_if_on_clan_chat_page():
        return
    else:
        return "quit"


def check_if_more_donates():
    current_image = screenshot()
    reference_folder = "more_donates_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    for location in locations:
        if location is not None:
            return location  # found a location
    return None


# region donate_cards


def look_for_donates_by_card(logger):
    # region earthquake
    earthquake = look_for_earthquake()
    if earthquake is not None:
        logger.log("Found a request for earthquake.")
        logger.log(earthquake)
        click(x=earthquake[1], y=earthquake[0])

    # endregion
    # region ice_spirit
    ice_spirit = look_for_ice_spirit()
    if ice_spirit is not None:
        logger.log("Found a request for ice_spirit.")
        logger.log(ice_spirit)
        click(x=ice_spirit[1], y=ice_spirit[0])

    # endregion
    # region skeleton_barrel
    skeleton_barrel = look_for_skeleton_barrel()
    if skeleton_barrel is not None:
        logger.log("Found a request for skeleton_barrel.")
        logger.log(skeleton_barrel)
        click(x=skeleton_barrel[1], y=skeleton_barrel[0])

    # endregion
    # region zappies
    zappies = look_for_zappies()
    if zappies is not None:
        logger.log("Found a request for zappies.")
        logger.log(zappies)
        click(x=zappies[1], y=zappies[0])

    # endregion
    # region skeletons
    skeletons = look_for_skeletons()
    if skeletons is not None:
        logger.log("Found a request for skeletons.")
        logger.log(skeletons)
        click(x=skeletons[1], y=skeletons[0])

    # endregion
    # region mini_pekka
    mini_pekka = look_for_skeletons()
    if mini_pekka is not None:
        logger.log("Found a request for mini_pekka.")
        logger.log(mini_pekka)
        click(x=mini_pekka[1], y=mini_pekka[0])

    # endregion
    # region inferno_tower
    inferno_tower = look_for_inferno_tower()
    if inferno_tower is not None:
        logger.log("Found a request for infero_tower.")
        logger.log(inferno_tower)
        click(x=inferno_tower[1], y=inferno_tower[0])

    # endregion
    # region goblins
    goblins = look_for_goblins()
    if goblins is not None:
        logger.log("Found a request for goblins.")
        logger.log(goblins)
        click(x=goblins[1], y=goblins[0])

    # endregion
    # region bomber
    coords = look_for_bomber()
    if coords is not None:
        logger.log("Found a request for bomber.")
        logger.log(coords)
        click(x=coords[1], y=coords[0])

    # endregion
    # region goblin_gang
    coords = look_for_goblin_gang()
    if coords is not None:
        logger.log("Found a request for goblin_gang.")
        logger.log(coords)
        click(x=coords[1], y=coords[0])
    # endregion


def look_for_earthquake():
    references = [
        "earthquake.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_ice_spirit():
    references = [
        "ice_spirit.png",
        "ice_spirit_1.png",
        "ice_spirit_2.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_skeleton_barrel():
    references = [
        "skeleton_barrel.png",
        "skeleton_barrel_1.png",
        "skeleton_barrel_2.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_zappies():
    references = [
        "zappies.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_skeletons():
    references = [
        "skeletons.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_mini_pekka():
    references = [
        "mini_pekka.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_inferno_tower():
    references = [
        "inferno_tower.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_goblins():
    references = [
        "goblins.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_bomber():
    references = [
        "bomber.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_goblin_gang():
    references = [
        "goblin_gang.png",
    ]
    locations = find_references(
        screenshot=screenshot(region=(0, 0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


# endregion
