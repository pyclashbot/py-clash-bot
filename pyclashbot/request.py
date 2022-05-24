import time

from pyclashbot.client import (check_quit_key_press, click, refresh_screen,
                               scroll_down)
from pyclashbot.image_rec import find_references, get_first_location, pixel_is_equal
from pyclashbot.state import (check_if_on_clan_chat_page,
                              return_to_clash_main_menu)


# region request_cards
def check_if_can_request(logger):
    iar = refresh_screen()
    pix1 = iar[612][326]
    pix2 = iar[606][334]
    pix3 = iar[608][326]
    sentinel = [1] * 3
    sentinel[0] = 49
    sentinel[1] = 186
    sentinel[2] = 71
    check_quit_key_press()

    if not pixel_is_equal(pix1, sentinel, 10):
        return False
    if not pixel_is_equal(pix2, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    check_quit_key_press()
    return True


def look_for_request_button():
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
    ]
    locations = find_references(
        screenshot=refresh_screen(),
        folder="request_button",
        names=references,
        tolerance=0.99
    )
    return get_first_location(locations)


def request_from_clash_main_menu(card_to_request, logger):
    logger.log("Moving to clan chat page")
    click(x=317, y=627)

    time.sleep(1)
    while not check_if_on_clan_chat_page():
        click(x=317, y=627)

        time.sleep(2)
    log = "requesting: " + str(card_to_request)
    logger.log(log)
    click(x=86, y=564)

    # scroll till find card +click card
    coords = scroll_to_request_card(card_to_request)
    if coords == "quit":
        return "quit"
    if coords is not None:
        click(x=coords[1], y=coords[0])
        time.sleep(2)
    # click request
    coords = look_for_request_button()
    if coords is not None:
        click(x=coords[1], y=coords[0])

        time.sleep(2)
    return_to_clash_main_menu()


def scroll_to_request_card(card_to_request):
    if card_to_request == "archers":
        return scroll_till_find_archers()
    if card_to_request == "arrows":
        return scroll_till_find_arrows()
    if card_to_request == "barb_hut":
        return scroll_till_find_barb_hut()
    if card_to_request == "barbs":
        return scroll_till_find_barbs()
    if card_to_request == "bats":
        return scroll_till_find_bats()
    if card_to_request == "bomb_tower":
        return scroll_till_find_bomb_tower()
    if card_to_request == "bomber":
        return scroll_till_find_bomber()
    if card_to_request == "cannon":
        return scroll_till_find_cannon()
    if card_to_request == "dart_goblin":
        return scroll_till_find_dart_goblin()
    if card_to_request == "e_spirit":
        return scroll_till_find_e_spirit()
    if card_to_request == "earthquake":
        return scroll_till_find_earthquake()
    if card_to_request == "elite_barbs":
        return scroll_till_find_elite_barbs()
    if card_to_request == "elixer_golem":
        return scroll_till_find_elixer_golem()
    if card_to_request == "elixer_pump":
        return scroll_till_find_elixer_pump()
    if card_to_request == "flying_machine":
        return scroll_till_find_flying_machine()
    if card_to_request == "furnace":
        return scroll_till_find_furnace()
    if card_to_request == "giant":
        return scroll_till_find_giant()
    if card_to_request == "goblin_cage":
        return scroll_till_find_goblin_cage()
    if card_to_request == "goblin_hut":
        return scroll_till_find_goblin_hut()
    if card_to_request == "goblins":
        return scroll_till_find_goblins()
    if card_to_request == "heal_spirit":
        return scroll_till_find_heal_spirit()
    if card_to_request == "healer":
        return scroll_till_find_healer()
    if card_to_request == "ice_golem":
        return scroll_till_find_ice_golem()
    if card_to_request == "ice_spirit":
        return scroll_till_find_ice_spirit()
    if card_to_request == "knight":
        return scroll_till_find_knight()
    if card_to_request == "mega_minion":
        return scroll_till_find_mega_minion()
    if card_to_request == "minion_hoard":
        return scroll_till_find_minion_hoard()
    if card_to_request == "minions":
        return scroll_till_find_minions()
    if card_to_request == "mortar":
        return scroll_till_find_mortar()
    if card_to_request == "musketeer":
        return scroll_till_find_musketeer()
    if card_to_request == "rascals":
        return scroll_till_find_rascals()
    if card_to_request == "rocket":
        return scroll_till_find_rocket()
    if card_to_request == "royal_delivery":
        return scroll_till_find_royal_delivery()
    if card_to_request == "royal_giant":
        return scroll_till_find_royal_giant()
    if card_to_request == "royal_hogs":
        return scroll_till_find_royal_hogs()
    if card_to_request == "skeleton_barrel":
        return scroll_till_find_skeleton_barrel()
    if card_to_request == "skeleton_dragons":
        return scroll_till_find_skeleton_dragons()
    if card_to_request == "skeletons":
        return scroll_till_find_skeletons()
    if card_to_request == "snowball":
        return scroll_till_find_snowball()
    if card_to_request == "spear_goblins":
        return scroll_till_find_spear_goblins()
    if card_to_request == "tombstone":
        return scroll_till_find_tombstone()
    if card_to_request == "wizard":
        return scroll_till_find_wizard()
    if card_to_request == "zappies":
        return scroll_till_find_zappies()
    if card_to_request == "fire_spirit":
        return scroll_till_find_fire_spirit()
    if card_to_request == "fireball":
        return scroll_till_find_fireball()
    if card_to_request == "valk":
        return scroll_till_find_valk()
    if card_to_request == "goblin_gang":
        return scroll_till_find_goblin_gang()
    if card_to_request == "zap":
        return scroll_till_find_zap()
    if card_to_request == "inferno_tower":
        return scroll_till_find_inferno_tower()

# archers


def scroll_till_find_archers():
    loops = 0
    n = None
    while (n is None):
        references = [
            "archers.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# giant


def scroll_till_find_giant():
    loops = 0
    n = None
    while (n is None):
        references = [
            "giant_1.png",
            "giant_2.png",
            "giant_3.png",
            "giant_4.png",
            "giant_5.png",
            "giant_6.png",
            "giant_7.png",
            "giant_8.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# arrows


def scroll_till_find_arrows():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "arrows.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# barb_hut


def scroll_till_find_barb_hut():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "barb_hut.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# barbs


def scroll_till_find_barbs():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "barbs.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# bats


def scroll_till_find_bats():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "bats.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# bomb_tower


def scroll_till_find_bomb_tower():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "bomb_tower.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# bomber


def scroll_till_find_bomber():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "bomber.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# cannon


def scroll_till_find_cannon():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "cannon.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# dart_goblin


def scroll_till_find_dart_goblin():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "dart_goblin.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# e_spirit


def scroll_till_find_e_spirit():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "e_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# earthquake


def scroll_till_find_earthquake():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "earthquake.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# elite_barbs


def scroll_till_find_elite_barbs():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "elite_barbs.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# elixer_golem


def scroll_till_find_elixer_golem():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "elixer_golem.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# elixer_pump


def scroll_till_find_elixer_pump():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "elixer_pump.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# flying_machine


def scroll_till_find_flying_machine():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "flying_machine.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# furnace


def scroll_till_find_furnace():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "furnace.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# goblin_cage


def scroll_till_find_goblin_cage():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "goblin_cage.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# goblin_hut


def scroll_till_find_goblin_hut():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "goblin_hut.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# goblins


def scroll_till_find_goblins():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "goblins.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# heal_spirit


def scroll_till_find_heal_spirit():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "heal_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# healer


def scroll_till_find_healer():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "healer.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# ice_golem


def scroll_till_find_ice_golem():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "ice_golem.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# ice_spirit


def scroll_till_find_ice_spirit():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "ice_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# knight


def scroll_till_find_knight():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "knight.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# mega_minion


def scroll_till_find_mega_minion():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "mega_minion.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# minion_hoard


def scroll_till_find_minion_hoard():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "minion_hoard.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# minions


def scroll_till_find_minions():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "minions.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# mortar


def scroll_till_find_mortar():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "mortar.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# musketeer


def scroll_till_find_musketeer():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "musketeer.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# rascals


def scroll_till_find_rascals():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "rascals.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# rocket


def scroll_till_find_rocket():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "rocket.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# royal_delivery


def scroll_till_find_royal_delivery():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "royal_delivery.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# royal_giant


def scroll_till_find_royal_giant():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "royal_giant.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# royal_hogs


def scroll_till_find_royal_hogs():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "royal_hogs.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# skeleton_barrel


def scroll_till_find_skeleton_barrel():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "skeleton_barrel.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# skeleton_dragons


def scroll_till_find_skeleton_dragons():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "skeleton_dragons.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# skeletons


def scroll_till_find_skeletons():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "skeletons.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# snowball


def scroll_till_find_snowball():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "snowball.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# spear_goblins


def scroll_till_find_spear_goblins():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "spear_goblins.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# tombstone


def scroll_till_find_tombstone():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "tombstone.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# wizard


def scroll_till_find_wizard():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "wizard.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# zappies


def scroll_till_find_zappies():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "zappies.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# fire_spirit


def scroll_till_find_fire_spirit():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "fire_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# fireball


def scroll_till_find_fireball():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "fireball.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# valk


def scroll_till_find_valk():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "valk.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# goblin_gang


def scroll_till_find_goblin_gang():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "goblin_gang.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# zap


def scroll_till_find_zap():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "zap.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"
# inferno_tower


def scroll_till_find_inferno_tower():
    loops = 0
    n = None
    while (n is None) and (loops < 50):
        references = [
            "inferno_tower.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n = location
                if n is not None:
                    return n
        scroll_down()
        loops += 1
    return "quit"

# endregion
