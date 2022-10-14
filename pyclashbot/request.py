import time

from pyclashbot.client import (check_quit_key_press, click, refresh_screen,
                               scroll_down)
from pyclashbot.image_rec import (find_references, get_first_location,
                                  pixel_is_equal)
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
        "ifhy_1.png",
        "ifhy_2.png",
        "ifhy_3.png",
        "ifhy_4.png",
        "ifhy_5.png",
        "ifhy_6.png",
        "ifhy_7.png",
        "ifhy_8.png",
        "iuyfgh_1.png",
        "iuyfgh_2.png",
        "iuyfgh_3.png",
        "iuyfgh_4.png",
        "iuyfgh_5.png",
        "iuyfgh_6.png",
        "iuyfgh_7.png",
        "iuyfgh_8.png",
        "royal_guards_1.png",
        "royal_guards_2.png",
        "royal_guards_3.png",
        "royal_guards_4.png",
        "royal_guards_5.png",
        "royal_guards_6.png",
        "royal_guards_7.png",
        "royal_guards_8.png",
        "telotet_1.png",
        "telotet_2.png",
        "telotet_3.png",
        "telotet_4.png",
        "telotet_5.png",
        "telotet_6.png",
        "telotet_7.png",
        "telotet_8.png",
        "22.png",
        "23.png",
        "24.png",
        "25.png",
        "26.png",
    ]
    locations = find_references(
        screenshot=refresh_screen(),
        folder="request_button",
        names=references,
        tolerance=0.97
    )
    return get_first_location(locations)


#method to request a random card
def request_random_card(logger):
    #starts on the request screen (the one with a bunch of pictures of the cards)
    #ends back on the clash main menu
    logger.log("Requesting a random card.")
    
    #scroll a little for randomness
    n=Random().randint(0,500)
    pyautogui.moveTo(203,552)
    time.sleep(0.33)
    pyautogui.dragTo(203,552-n,0.33)
    
    logger.log("Looking for card to request.")
    has_card_to_request=False
    while not(has_card_to_request):
        #click random coord in region of card selection
        click(Random().randint(72,343),Random().randint(264,570))
        time.sleep(3)
        
        #check if request button appears
        request_button_coord=look_for_request_button()
        
        if request_button_coord is not None:
            has_card_to_request=True
    logger.log("Found a satisfactory card to request.")

    #click request button
    click(request_button_coord[1],request_button_coord[0])


def request_random_card_from_clash_main(logger):
    logger.log("Moving to clan chat page")
    click(x=317, y=627)

    time.sleep(1)
    while not check_if_on_clan_chat_page():
        click(x=317, y=627)
        scroll_down()
        time.sleep(2)
    logger.log("Requesting a random card")
    # clicking request button in bottom left
    click(x=86, y=564)
    
    request_random_card(logger)
    
    return_to_clash_main_menu()


def request_from_clash_main_menu(card_to_request, logger):
    logger.log("Moving to clan chat page")
    click(x=317, y=627)

    time.sleep(1)
    while not check_if_on_clan_chat_page():
        click(x=317, y=627)
        scroll_down()
        time.sleep(2)
    log = "requesting: " + str(card_to_request)
    logger.log(log)
    # clicking request button in bottom left
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
    else:
        return "quit"
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
    while True:
        references = [
            "archers.png",
            "archers_1.png",
            "archers_2.png",
            "archers_3.png",
            "archers_4.png",
            "archers_5.png",
            "archers_6.png",
            "archers_7.png",
            "archers_8.png",

        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# giant


def scroll_till_find_giant():
    loops = 0
    while True:
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

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# arrows


def scroll_till_find_arrows():
    loops = 0
    while True:
        references = [
            "arrows.png",
            "arrows_1.png",
            "arrows_2.png",
            "arrows_3.png",
            "arrows_4.png",
            "arrows_5.png",
            "arrows_6.png",
            "arrows_7.png",
            "arrows_8.png",

        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# barb_hut


def scroll_till_find_barb_hut():
    loops = 0
    while True:
        references = [
            "barb_hut_1.png",
            "barb_hut_2.png",
            "barb_hut_3.png",
            "barb_hut_4.png",
            "barb_hut_5.png",
            "barb_hut_6.png",
            "barb_hut_7.png",
            "barb_hut_8.png",
            "barb_hut_9.png",

        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# barbs


def scroll_till_find_barbs():
    loops = 0
    while True:
        references = [
            "barbs.png",
            "barbs_1.png",
            "barbs_2.png",
            "barbs_3.png",
            "barbs_4.png",
            "barbs_5.png",
            "barbs_6.png",
            "barbs_7.png",
            "barbs_8.png",

        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# bats


def scroll_till_find_bats():
    loops = 0
    while True:
        references = [
            "bats.png",
            "bats_1.png",
            "bats_2.png",
            "bats_3.png",
            "bats_4.png",
            "bats_5.png",
            "bats_6.png",
            "bats_7.png",
            "bats_8.png",

        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# bomb_tower


def scroll_till_find_bomb_tower():
    loops = 0
    while True:
        references = [
            "bomb_tower.png",
            "bomb_tower_1.png",
            "bomb_tower_2.png",
            "bomb_tower_3.png",
            "bomb_tower_4.png",
            "bomb_tower_5.png",
            "bomb_tower_6.png",
            "bomb_tower_7.png",
            "bomb_tower_8.png",

        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# bomber


def scroll_till_find_bomber():
    loops = 0
    while True:
        references = [
            "bomber.png",
            "bomber_1.png",
            "bomber_2.png",
            "bomber_3.png",
            "bomber_4.png",
            "bomber_5.png",
            "bomber_6.png",
            "bomber_7.png",
            "bomber_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# cannon


def scroll_till_find_cannon():
    loops = 0
    while True:
        references = [
            "cannon.png",
            "cannon_1.png",
            "cannon_2.png",
            "cannon_3.png",
            "cannon_4.png",
            "cannon_5.png",
            "cannon_6.png",
            "cannon_7.png",
            "cannon_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# dart_goblin


def scroll_till_find_dart_goblin():
    loops = 0
    while True:
        references = [
            "dart_goblin.png",
            "dart_goblin_1.png",
            "dart_goblin_2.png",
            "dart_goblin_3.png",
            "dart_goblin_4.png",
            "dart_goblin_5.png",
            "dart_goblin_6.png",
            "dart_goblin_7.png",
            "dart_goblin_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# e_spirit


def scroll_till_find_e_spirit():
    loops = 0
    while True:
        references = [
            "e_spirit.png",
            "e_spirit_1.png",
            "e_spirit_2.png",
            "e_spirit_3.png",
            "e_spirit_4.png",
            "e_spirit_5.png",
            "e_spirit_6.png",
            "e_spirit_7.png",
            "e_spirit_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# earthquake


def scroll_till_find_earthquake():
    loops = 0
    while True:
        references = [
            "earthquake.png",
            "earthquake_1.png",
            "earthquake_2.png",
            "earthquake_3.png",
            "earthquake_4.png",
            "earthquake_5.png",
            "earthquake_6.png",
            "earthquake_7.png",
            "earthquake_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# elite_barbs


def scroll_till_find_elite_barbs():
    loops = 0
    while True:
        references = [
            "elite_barbs.png",
            "elite_barbs_1.png",
            "elite_barbs_2.png",
            "elite_barbs_3.png",
            "elite_barbs_4.png",
            "elite_barbs_5.png",
            "elite_barbs_6.png",
            "elite_barbs_7.png",
            "elite_barbs_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# elixer_golem


def scroll_till_find_elixer_golem():
    loops = 0
    while True:
        references = [
            "elixer_golem.png",
            "elixer_golem_1.png",
            "elixer_golem_2.png",
            "elixer_golem_3.png",
            "elixer_golem_4.png",
            "elixer_golem_5.png",
            "elixer_golem_6.png",
            "elixer_golem_7.png",
            "elixer_golem_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# elixer_pump


def scroll_till_find_elixer_pump():
    loops = 0
    while True:
        references = [
            "elixer_pump.png",
            "elixer_pump_1.png",
            "elixer_pump_2.png",
            "elixer_pump_3.png",
            "elixer_pump_4.png",
            "elixer_pump_5.png",
            "elixer_pump_6.png",
            "elixer_pump_7.png",
            "elixer_pump_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# flying_machine


def scroll_till_find_flying_machine():
    loops = 0
    while True:
        references = [
            "flying_machine.png",
            "flying_machine_1.png",
            "flying_machine_2.png",
            "flying_machine_3.png",
            "flying_machine_4.png",
            "flying_machine_5.png",
            "flying_machine_6.png",
            "flying_machine_7.png",
            "flying_machine_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# furnace


def scroll_till_find_furnace():
    loops = 0
    while True:
        references = [
            "furnace.png",
            "furnace_1.png",
            "furnace_2.png",
            "furnace_3.png",
            "furnace_4.png",
            "furnace_5.png",
            "furnace_6.png",
            "furnace_7.png",
            "furnace_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# goblin_cage


def scroll_till_find_goblin_cage():
    loops = 0
    while True:
        references = [
            "goblin_cage.png",
            "goblin_cage_1.png",
            "goblin_cage_2.png",
            "goblin_cage_3.png",
            "goblin_cage_4.png",
            "goblin_cage_5.png",
            "goblin_cage_6.png",
            "goblin_cage_7.png",
            "goblin_cage_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# goblin_hut


def scroll_till_find_goblin_hut():
    loops = 0
    while True:
        references = [
            "goblin_hut.png",
            "goblin_hut_1.png",
            "goblin_hut_2.png",
            "goblin_hut_3.png",
            "goblin_hut_4.png",
            "goblin_hut_5.png",
            "goblin_hut_6.png",
            "goblin_hut_7.png",
            "goblin_hut_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# goblins


def scroll_till_find_goblins():
    loops = 0
    while True:
        references = [
            "goblins.png",
            "goblins_1.png",
            "goblins_2.png",
            "goblins_3.png",
            "goblins_4.png",
            "goblins_5.png",
            "goblins_6.png",
            "goblins_7.png",
            "goblins_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# heal_spirit


def scroll_till_find_heal_spirit():
    loops = 0
    while True:
        references = [
            "heal_spirit.png",
            "heal_spirit_1.png",
            "heal_spirit_2.png",
            "heal_spirit_3.png",
            "heal_spirit_4.png",
            "heal_spirit_5.png",
            "heal_spirit_6.png",
            "heal_spirit_7.png",
            "heal_spirit_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# healer


def scroll_till_find_healer():
    loops = 0
    while True:
        references = [
            "healer.png",
            "healer_1.png",
            "healer_2.png",
            "healer_3.png",
            "healer_4.png",
            "healer_5.png",
            "healer_6.png",
            "healer_7.png",
            "healer_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# ice_golem


def scroll_till_find_ice_golem():
    loops = 0
    while True:
        references = [
            "ice_golem.png",
            "ice_golem_1.png",
            "ice_golem_2.png",
            "ice_golem_3.png",
            "ice_golem_4.png",
            "ice_golem_5.png",
            "ice_golem_6.png",
            "ice_golem_7.png",
            "ice_golem_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# ice_spirit


def scroll_till_find_ice_spirit():
    loops = 0
    while True:
        references = [
            "ice_spirit.png",
            "ice_spirit_1.png",
            "ice_spirit_2.png",
            "ice_spirit_3.png",
            "ice_spirit_4.png",
            "ice_spirit_5.png",
            "ice_spirit_6.png",
            "ice_spirit_7.png",
            "ice_spirit_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# knight


def scroll_till_find_knight():
    loops = 0
    while True:
        references = [
            "knight.png",
            "knight_1.png",
            "knight_2.png",
            "knight_3.png",
            "knight_4.png",
            "knight_5.png",
            "knight_6.png",
            "knight_7.png",
            "knight_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# mega_minion


def scroll_till_find_mega_minion():
    loops = 0
    while True:
        references = [
            "mega_minion.png",
            "mega_minion_1.png",
            "mega_minion_2.png",
            "mega_minion_3.png",
            "mega_minion_4.png",
            "mega_minion_5.png",
            "mega_minion_6.png",
            "mega_minion_7.png",
            "mega_minion_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# minion_hoard


def scroll_till_find_minion_hoard():
    loops = 0
    while True:
        references = [
            "minion_hoard.png",
            "minion_hoard_1.png",
            "minion_hoard_2.png",
            "minion_hoard_3.png",
            "minion_hoard_4.png",
            "minion_hoard_5.png",
            "minion_hoard_6.png",
            "minion_hoard_7.png",
            "minion_hoard_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# minions


def scroll_till_find_minions():
    loops = 0
    while True:
        references = [
            "minions.png",
            "minions_1.png",
            "minions_2.png",
            "minions_3.png",
            "minions_4.png",
            "minions_5.png",
            "minions_6.png",
            "minions_7.png",
            "minions_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# mortar


def scroll_till_find_mortar():
    loops = 0
    while True:
        references = [
            "mortar.png",
            "mortar_1.png",
            "mortar_2.png",
            "mortar_3.png",
            "mortar_4.png",
            "mortar_5.png",
            "mortar_6.png",
            "mortar_7.png",
            "mortar_8.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# musketeer


def scroll_till_find_musketeer():
    loops = 0
    while True:
        references = [
            "musketeer.png",
            "musketeer_1.png",
            "musketeer_2.png",
            "musketeer_3.png",
            "musketeer_4.png",
            "musketeer_5.png",
            "musketeer_6.png",
            "musketeer_7.png",
            "musketeer_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# rascals


def scroll_till_find_rascals():
    loops = 0
    while True:
        references = [
            "rascals.png",
            "rascals_1.png",
            "rascals_2.png",
            "rascals_3.png",
            "rascals_4.png",
            "rascals_5.png",
            "rascals_6.png",
            "rascals_7.png",
            "rascals_8.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# rocket


def scroll_till_find_rocket():
    loops = 0
    while True:
        references = [
            "rocket.png",
            "rocket_1.png",
            "rocket_2.png",
            "rocket_3.png",
            "rocket_4.png",
            "rocket_5.png",
            "rocket_6.png",
            "rocket_7.png",
            "rocket_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# royal_delivery


def scroll_till_find_royal_delivery():
    loops = 0
    while True:
        references = [
            "royal_delivery.png",
            "royal_delivery_1.png",
            "royal_delivery_2.png",
            "royal_delivery_3.png",
            "royal_delivery_4.png",
            "royal_delivery_5.png",
            "royal_delivery_6.png",
            "royal_delivery_7.png",
            "royal_delivery_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# royal_giant


def scroll_till_find_royal_giant():
    loops = 0
    while True:
        references = [
            "royal_giant.png",
            "royal_giant_1.png",
            "royal_giant_2.png",
            "royal_giant_3.png",
            "royal_giant_4.png",
            "royal_giant_5.png",
            "royal_giant_6.png",
            "royal_giant_7.png",
            "royal_giant_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# royal_hogs


def scroll_till_find_royal_hogs():
    loops = 0
    while True:
        references = [
            "royal_hogs.png",
            "royal_hogs_1.png",
            "royal_hogs_2.png",
            "royal_hogs_3.png",
            "royal_hogs_4.png",
            "royal_hogs_5.png",
            "royal_hogs_6.png",
            "royal_hogs_7.png",
            "royal_hogs_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# skeleton_barrel


def scroll_till_find_skeleton_barrel():
    loops = 0
    while True:
        references = [
            "skeleton_barrel.png",
            "skeleton_barrel_1.png",
            "skeleton_barrel_2.png",
            "skeleton_barrel_3.png",
            "skeleton_barrel_4.png",
            "skeleton_barrel_5.png",
            "skeleton_barrel_6.png",
            "skeleton_barrel_7.png",
            "skeleton_barrel_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# skeleton_dragons


def scroll_till_find_skeleton_dragons():
    loops = 0
    while True:
        references = [
            "skeleton_dragons.png",
            "skeleton_dragons_1.png",
            "skeleton_dragons_2.png",
            "skeleton_dragons_3.png",
            "skeleton_dragons_4.png",
            "skeleton_dragons_5.png",
            "skeleton_dragons_6.png",
            "skeleton_dragons_7.png",
            "skeleton_dragons_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# skeletons


def scroll_till_find_skeletons():
    loops = 0
    while True:
        references = [
            "skeletons.png",
            "skeletons_1.png",
            "skeletons_2.png",
            "skeletons_3.png",
            "skeletons_4.png",
            "skeletons_5.png",
            "skeletons_6.png",
            "skeletons_7.png",
            "skeletons_8.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# snowball


def scroll_till_find_snowball():
    loops = 0
    while True:
        references = [
            "snowball.png",
            "snowball_1.png",
            "snowball_2.png",
            "snowball_3.png",
            "snowball_4.png",
            "snowball_5.png",
            "snowball_6.png",
            "snowball_7.png",
            "snowball_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# spear_goblins


def scroll_till_find_spear_goblins():
    loops = 0
    while True:
        references = [
            "spear_goblins.png",
            "spear_goblins_1.png",
            "spear_goblins_2.png",
            "spear_goblins_3.png",
            "spear_goblins_4.png",
            "spear_goblins_5.png",
            "spear_goblins_6.png",
            "spear_goblins_7.png",
            "spear_goblins_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# tombstone


def scroll_till_find_tombstone():
    loops = 0
    while True:
        references = [
            "tombstone.png",
            "tombstone_1.png",
            "tombstone_2.png",
            "tombstone_3.png",
            "tombstone_4.png",
            "tombstone_5.png",
            "tombstone_6.png",
            "tombstone_7.png",
            "tombstone_8.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# wizard


def scroll_till_find_wizard():
    loops = 0
    while True:
        references = [
            "wizard.png",
            "wizard_1.png",
            "wizard_2.png",
            "wizard_3.png",
            "wizard_4.png",
            "wizard_5.png",
            "wizard_6.png",
            "wizard_7.png",
            "wizard_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# zappies


def scroll_till_find_zappies():
    loops = 0
    while True:
        references = [
            "zappies.png",
            "zappies_1.png",
            "zappies_2.png",
            "zappies_3.png",
            "zappies_4.png",
            "zappies_5.png",
            "zappies_6.png",
            "zappies_7.png",
            "zappies_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# fire_spirit


def scroll_till_find_fire_spirit():
    loops = 0
    while True:
        references = [
            "fire_spirit.png",
            "fire_spirit_1.png",
            "fire_spirit_2.png",
            "fire_spirit_3.png",
            "fire_spirit_4.png",
            "fire_spirit_5.png",
            "fire_spirit_6.png",
            "fire_spirit_7.png",
            "fire_spirit_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# fireball


def scroll_till_find_fireball():
    loops = 0
    while True:
        references = [
            "fireball.png",
            "fireball_1.png",
            "fireball_2.png",
            "fireball_3.png",
            "fireball_4.png",
            "fireball_5.png",
            "fireball_6.png",
            "fireball_7.png",
            "fireball_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# valk


def scroll_till_find_valk():
    loops = 0
    while True:
        references = [
            "valk.png",
            "valk_1.png",
            "valk_2.png",
            "valk_3.png",
            "valk_4.png",
            "valk_5.png",
            "valk_6.png",
            "valk_7.png",
            "valk_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# goblin_gang


def scroll_till_find_goblin_gang():
    loops = 0
    while True:
        references = [
            "goblin_gang.png",
            "goblin_gang_1.png",
            "goblin_gang_2.png",
            "goblin_gang_3.png",
            "goblin_gang_4.png",
            "goblin_gang_5.png",
            "goblin_gang_6.png",
            "goblin_gang_7.png",
            "goblin_gang_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# zap


def scroll_till_find_zap():
    loops = 0
    while True:
        references = [
            "zap.png",
            "zap_1.png",
            "zap_2.png",
            "zap_3.png",
            "zap_4.png",
            "zap_5.png",
            "zap_6.png",
            "zap_7.png",
            "zap_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"
# inferno_tower


def scroll_till_find_inferno_tower():
    loops = 0
    while True:
        references = [
            "inferno_tower.png",
            "inferno_tower_1.png",
            "inferno_tower_2.png",
            "inferno_tower_3.png",
            "inferno_tower_4.png",
            "inferno_tower_5.png",
            "inferno_tower_6.png",
            "inferno_tower_7.png",
            "inferno_tower_8.png",


        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        location = get_first_location(locations)
        if location is not None:
            return location
        scroll_down()
        loops += 1
        if loops > 20:
            return "quit"

# endregion
