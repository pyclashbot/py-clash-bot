import random
import time

import numpy

from pyclashbot.card import check_for_card_in_hand
from pyclashbot.client import (check_quit_key_press, click, refresh_screen,
                               screenshot, scroll_down)
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location, pixel_is_equal)
from pyclashbot.state import check_if_in_battle, wait_for_clash_main_menu


def start_1v1_ranked(logger):
    check_quit_key_press()
    logger.log("Navigating to 1v1 ranked match")
    click(140, 440)
    wait_for_battle_start(logger)
    check_quit_key_press()


def start_2v2(logger):
    logger.log("Initiating 2v2 match from main menu")
    
    logger.log("Clicking party mode")
    time.sleep(1)
    click(284,449)
    
    find_and_click_2v2_quickmatch_button(logger)
    
    check_for_reward_limit()


#method to find and click the 2v2 quickmatch button in the party mode menu
def find_and_click_2v2_quickmatch_button(logger):
    #starts in the party mode
    #ends when loading a match
    logger.log("Finding and clicking 2v2 quickmatch button")
    button_coords=[]
    loops=0
    #repeatedly scroll down until we find coords for the 2v2 quickmatch button
    while button_coords==[]:
        loops=loops+1
        logger.log("Scrolling down")
        check_quit_key_press()
        time.sleep(1)
        scroll_down()
        button_coords=find_2v2_quick_match_button()
        if loops>20:
            return "restart"
    #once we find the coords, click them
    click(button_coords[0],button_coords[1],clicks=2,interval=0.25)
    logger.log("Done queueing a 2v2 quickmatch")


#method to find the 2v2 quickmatch button in the party mode menu
def find_2v2_quick_match_button():
    current_image = screenshot()
    reference_folder = "2v2_quick_match"
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
    
    coord= get_first_location(locations)
    if coord is None: return None
    return [coord[1]+200,coord[0]+50]



def find_party_button():
    current_image = screenshot()
    reference_folder = "party_button"
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
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    return get_first_location(locations)


def wait_for_battle_start(logger):
    logger.log("Waiting for battle start")
    n = 1
    n1 = 0
    check_quit_key_press()
    while n == 1:
        if check_if_in_battle():
            n = 0
        click(100, 100)
        time.sleep(0.25)
        n1 += 1
        if n1 > 120:
            logger.log("Waited longer than 30 sec for a fight")
            return "quit"
        refresh_screen()
        check_quit_key_press()


def fight_in_2v2(logger):
    check_quit_key_press()
    if check_if_hero_ability_is_available():
        click(346, 515)
        time.sleep(1)
    card_coord = random_card_coord_picker(logger)
    placement_coord = look_for_enemy_troops()
    if placement_coord is None:
        logger.log("picking random coord")
        placement_coord = random_placement_coord_maker()
    else:
        logger.log("picking coord: ", placement_coord)
        placement_coord[1] = placement_coord[1] + 30
    # pick card
    click(card_coord[0], card_coord[1], clicks=1, interval=0)
    # place card
    click(x=placement_coord[0], y=placement_coord[1], clicks=1, interval=0)


def look_for_enemy_troops():
    current_image = screenshot(region=(78, 141, 271, 356))

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
        "32.png",
        "33.png",
        "34.png",
        "14_10.png",
        "1_1.png",
        "1_2.png",
        "1_3.png",
        "1_4.png",
        "2_1.png",
        "2_3.png",
        "2_2.png",
        "3_1.png",
        "3_2.png",
        "3_3.png",
        "3_4.png",
        "3_5.png",
        "5_1.png",
        "5_2.png",
        "5_3.png",
        "5_4.png",
        "6_1.png",
        "6_2.png",
        "6_3.png",
        "6_4.png",
        "7_1.png",
        "7_2.png",
        "7_3.png",
        "7_4.png",
        "7_5.png",
        "8_1.png",
        "8_2.png",
        "8_3.png",
        "8_4.png",
        "9_1.png",
        "9_2.png",
        "9_3.png",
        "9_4.png",
        "10_1.png",
        "10_2.png",
        "10_3.png",
        "10_4.png",
        "11_1.png",
        "11_2.png",
        "11_3.png",
        "11_4.png",
        "11_5.png",
        "12_1.png",
        "12_2.png",
        "12_3.png",
        "12_4.png",
        "12_5.png",
        "12_6.png",
        "13_2.png",
        "13_3.png",
        "14_2.png",
        "14_3.png",
        "14_4.png",
        "14_5.png",
        "14_6.png",
        "14_7.png",
        "14_8.png",
        "14_9.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder="ENEMY_TROOP_IMAGES",
        names=references,
        tolerance=0.97
    )

    return get_first_location(locations, flip=True)


def leave_end_battle_window(logger):
    check_quit_key_press()
    logger.log("battle is over. return to clash main menu")
    click(81, 630)
    time.sleep(0.2)
    click(211, 580)
    wait_for_clash_main_menu(logger)
    check_quit_key_press()


def check_if_exit_battle_button_exists():
    current_image = screenshot()
    reference_folder = "exit_battle"
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
        tolerance=0.99
    )

    return check_for_location(locations)


def open_activity_log(logger):
    check_quit_key_press()
    click(x=360, y=99)

    time.sleep(1)
    check_quit_key_press()
    click(x=255, y=75)

    time.sleep(1)
    check_quit_key_press()


def check_if_past_game_is_win(logger):
    check_quit_key_press()
    open_activity_log(logger)
    iar = refresh_screen()

    for n in range(40, 130):
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if pixel_is_equal(pix, sentinel, 10):
            click(20, 507)

            return True
    time.sleep(1)
    click(385, 507)
    click(20, 507)
    return False


def random_card_coord_picker(logger):
    check_quit_key_press()
    n = random.randint(1, 4)
    coords = [1] * 2
    if n == 1:
        # logger.log("randomly selected card 1")
        coords[0] = 146
        coords[1] = 588
    elif n == 2:
        # logger.log("randomly selected card 2")
        coords[0] = 206
        coords[1] = 590
    elif n == 3:
        # logger.log("randomly selected card 3")
        coords[0] = 278
        coords[1] = 590
    elif n == 4:
        # logger.log("randomly selected card 4")
        coords[0] = 343
        coords[1] = 588
    check_quit_key_press()

    return coords


def random_placement_coord_maker():
    check_quit_key_press()
    n = random.randint(1, 6)
    coords = [1] * 2
    if n in {0, 1}:
        coords[0] = 55
        coords[1] = 333
    elif n == 2:
        coords[0] = 73
        coords[1] = 439
    elif n == 3:
        coords[0] = 177
        coords[1] = 502
    elif n == 4:
        coords[0] = 240
        coords[1] = 515
    elif n == 5:
        coords[0] = 346
        coords[1] = 429
    elif n == 6:
        coords[0] = 364
        coords[1] = 343
    check_quit_key_press()
    return coords


def check_for_reward_limit():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png"
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="reward_limit",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            click(211, 432)

            return True
    return False

# region fight


def check_if_hero_ability_is_available():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png"
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="hero_abilities",
        names=references,
        tolerance=0.97
    )
    return check_for_location(locations)


def play_card_at_a_random_coord(card_loc, random_coords):
    if card_loc is None:
        return
    click(x=card_loc[0], y=card_loc[1])
    time.sleep(0.25)
    # click placement
    placement_loc = random.choice(random_coords)
    click(x=placement_loc[0], y=placement_loc[1])


def play_card_on_enemy_with_offset(card_loc, enemy_troop_position, offset):
    if card_loc is None:
        return
    placement_loc = enemy_troop_position
    if placement_loc is None:
        placement_loc = random_placement_coord_maker()
    else:
        placement_loc[1] = 400 if placement_loc[1] < 300 else placement_loc[1] + offset
    if card_loc is not None:
        click(x=card_loc[0], y=card_loc[1])
    time.sleep(0.25)
    if placement_loc is not None:
        click(x=placement_loc[0], y=placement_loc[1])


def play_turret_card(card_loc):
    if card_loc is None:
        return
    return play_card_at_a_random_coord(
        card_loc,
        [
            [208, 401],
            [208, 372],
            [211, 393],
            [203, 380]
        ]
    )


def play_spawner_card(card_loc):
    if card_loc is None:
        return
    return play_card_at_a_random_coord(
        card_loc,
        [
            [86, 485],
            [139, 488],
            [174, 436],
            [265, 442],
            [281, 492],
            [341, 495]
        ]
    )


def play_hogs_card(card_loc):
    if card_loc is None:
        return
    return play_card_at_a_random_coord(
        card_loc,
        [
            [84, 340],
            [125, 340],
            [298, 340],
            [347, 340]
        ]
    )


def fight_with_deck_list(enemy_troop_position):

    # check for hero abilities
    ability_coords = check_if_hero_ability_is_available()
    if ability_coords:
        click(x=345, y=512)
        return
# expensive has prio
#     elite_barbs
    if (check_for_card_in_hand("elite_barbs") is not None):
        # logger.log("playing elite_barbs")
        card_loc = check_for_card_in_hand("elite_barbs")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     e_giant
    if (check_for_card_in_hand("e_giant") is not None):
        # logger.log("playing e_giant")
        card_loc = check_for_card_in_hand("e_giant")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     giant_skeleton
    if (check_for_card_in_hand("giant_skeleton") is not None):
        # logger.log("playing giant_skeleton")
        card_loc = check_for_card_in_hand("giant_skeleton")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     goblin_giant
    if (check_for_card_in_hand("goblin_giant") is not None):
        # logger.log("playing goblin_giant")
        card_loc = check_for_card_in_hand("goblin_giant")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     mega_knight
    if (check_for_card_in_hand("mega_knight") is not None):
        # logger.log("playing mega_knight")
        card_loc = check_for_card_in_hand("mega_knight")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     pekka
    if (check_for_card_in_hand("pekka") is not None):
        # logger.log("playing pekka")
        card_loc = check_for_card_in_hand("pekka")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     witch
    if (check_for_card_in_hand("witch") is not None):
        # logger.log("playing witch")
        card_loc = check_for_card_in_hand("witch")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     wizard
    if (check_for_card_in_hand("wizard") is not None):
        # logger.log("playing wizard")
        card_loc = check_for_card_in_hand("wizard")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     barb_hut
    if (check_for_card_in_hand("barb_hut") is not None):
        # logger.log("playing barb_hut")
        card_loc = check_for_card_in_hand("barb_hut")
        return play_spawner_card(card_loc)
#     royal_guards
    if (check_for_card_in_hand("royal_guards") is not None):
        # logger.log("playing royal_guards")
        card_loc = check_for_card_in_hand("royal_guards")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [212, 333],
                [205, 502]
            ]
        )
#     royal_giant
    if (check_for_card_in_hand("royal_giant") is not None):
        # logger.log("playing royal_giant")
        card_loc = check_for_card_in_hand("royal_giant")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [114, 346],
                [176, 336],
                [298, 336],
                [246, 339]
            ]
        )
# turrets
#     bomb_tower
    if (check_for_card_in_hand("bomb_tower") is not None):
        # logger.log("bomb_tower in decklist and hand.")
        card_loc = check_for_card_in_hand("bomb_tower")
        if card_loc is None:
            return

        return play_turret_card(card_loc)
#     cannon
    if (check_for_card_in_hand("cannon") is not None):
        # logger.log("cannon in decklist and hand.")
        card_loc = check_for_card_in_hand("cannon")
        if card_loc is None:
            return

        return play_turret_card(card_loc)
#     goblin_cage
    if (check_for_card_in_hand("goblin_cage") is not None):
        # logger.log("goblin_cage in decklist and hand.")
        card_loc = check_for_card_in_hand("goblin_cage")
        if card_loc is None:
            return

        return play_turret_card(card_loc)
#     inferno_tower
    if (check_for_card_in_hand("inferno_tower") is not None):
        # logger.log("inferno_tower in decklist and hand.")
        card_loc = check_for_card_in_hand("inferno_tower")
        if card_loc is None:
            return

        return play_turret_card(card_loc)
#     tesla
    if (check_for_card_in_hand("tesla") is not None):
        # logger.log("tesla in decklist and hand.")
        card_loc = check_for_card_in_hand("tesla")
        return play_turret_card(card_loc)
# goblin_barrels
#     goblin_drill
    if (check_for_card_in_hand("goblin_drill") is not None):
        # logger.log("found goblin_drill in decklist and hand")
        card_loc = check_for_card_in_hand("goblin_drill")
        return play_card_at_a_random_coord(
            card_loc, [
                [
                    96, 195], [
                    144, 193], [
                    125, 170], [
                        297, 220], [
                            319, 196], [
                                297, 165]])
#     miner
    if (check_for_card_in_hand("miner") is not None):
        # logger.log("found miner in decklist and hand")
        card_loc = check_for_card_in_hand("miner")
        return play_card_at_a_random_coord(
            card_loc, [
                [
                    96, 195], [
                    144, 193], [
                    125, 170], [
                        297, 220], [
                            319, 196], [
                                297, 165]])
#     goblin_barrel
    if (check_for_card_in_hand("goblin_barrel") is not None):
        # logger.log("found goblin_barrel in decklist and hand")
        card_loc = check_for_card_in_hand("goblin_barrel")
        return play_card_at_a_random_coord(
            card_loc, [
                [
                    120, 200], [
                    120, 200], [
                    297, 200], [
                        297, 200], [
                            353, 158], [
                                71, 166]])
# melee_tanks
#     barb_barrel
    if (check_for_card_in_hand("barb_barrel") is not None):
        # logger.log("playing barb_barrel")
        card_loc = check_for_card_in_hand("barb_barrel")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     bandit
    if (check_for_card_in_hand("bandit") is not None):
        # logger.log("playing bandit")
        card_loc = check_for_card_in_hand("bandit")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     barbs
    if (check_for_card_in_hand("barbs") is not None):
        # logger.log("playing barbs")
        card_loc = check_for_card_in_hand("barbs")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     bats
    if (check_for_card_in_hand("bats") is not None):
        # logger.log("playing bats")
        card_loc = check_for_card_in_hand("bats")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     dark_knight
    if (check_for_card_in_hand("dark_knight") is not None):
        # logger.log("playing dark_knight")
        card_loc = check_for_card_in_hand("dark_knight")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     e_spirit
    if (check_for_card_in_hand("e_spirit") is not None):
        # logger.log("playing e_spirit")
        card_loc = check_for_card_in_hand("e_spirit")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     fisherman
    if (check_for_card_in_hand("fisherman") is not None):
        # logger.log("playing fisherman")
        card_loc = check_for_card_in_hand("fisherman")
        offset = 90
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     giant
    if (check_for_card_in_hand("giant") is not None):
        # logger.log("playing giant")
        card_loc = check_for_card_in_hand("giant")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     goblins
    if (check_for_card_in_hand("goblins") is not None):
        # logger.log("playing goblins")
        card_loc = check_for_card_in_hand("goblins")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     golden_knight
    if (check_for_card_in_hand("golden_knight") is not None):
        # logger.log("playing golden_knight")
        card_loc = check_for_card_in_hand("golden_knight")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     guards
    if (check_for_card_in_hand("guards") is not None):
        # logger.log("playing guards")
        card_loc = check_for_card_in_hand("guards")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     heal_spirit
    if (check_for_card_in_hand("heal_spirit") is not None):
        # logger.log("playing heal_spirit")
        card_loc = check_for_card_in_hand("heal_spirit")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     healer
    if (check_for_card_in_hand("healer") is not None):
        # logger.log("playing healer")
        card_loc = check_for_card_in_hand("healer")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     ice_golem
    if (check_for_card_in_hand("ice_golem") is not None):
        # logger.log("playing ice_golem")
        card_loc = check_for_card_in_hand("ice_golem")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     ice_spirit
    if (check_for_card_in_hand("ice_spirit") is not None):
        # logger.log("playing ice_spirit")
        card_loc = check_for_card_in_hand("ice_spirit")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     knight
    if (check_for_card_in_hand("knight") is not None):
        # logger.log("playing knight")
        card_loc = check_for_card_in_hand("knight")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     lumberjack
    if (check_for_card_in_hand("lumberjack") is not None):
        # logger.log("playing lumberjack")
        card_loc = check_for_card_in_hand("lumberjack")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     mega_minion
    if (check_for_card_in_hand("mega_minion") is not None):
        # logger.log("playing mega_minion")
        card_loc = check_for_card_in_hand("mega_minion")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     mighty_miner
    if (check_for_card_in_hand("mighty_miner") is not None):
        # logger.log("playing mighty_miner")
        card_loc = check_for_card_in_hand("mighty_miner")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     mini_pekka
    if (check_for_card_in_hand("mini_pekka") is not None):
        # logger.log("playing mini_pekka")
        card_loc = check_for_card_in_hand("mini_pekka")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     minion_hoard
    if (check_for_card_in_hand("minion_hoard") is not None):
        # logger.log("playing minion_hoard")
        card_loc = check_for_card_in_hand("minion_hoard")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     minions
    if (check_for_card_in_hand("minions") is not None):
        # logger.log("playing minions")
        card_loc = check_for_card_in_hand("minions")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     prince
    if (check_for_card_in_hand("prince") is not None):
        # logger.log("playing prince")
        card_loc = check_for_card_in_hand("prince")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     royal_ghost
    if (check_for_card_in_hand("royal_ghost") is not None):
        # logger.log("playing royal_ghost")
        card_loc = check_for_card_in_hand("royal_ghost")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     skeleton_army
    if (check_for_card_in_hand("skeleton_army") is not None):
        # logger.log("playing skeleton_army")
        card_loc = check_for_card_in_hand("skeleton_army")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     skeleton_barrel
    if (check_for_card_in_hand("skeleton_barrel") is not None):
        # logger.log("playing skeleton_barrel")
        card_loc = check_for_card_in_hand("skeleton_barrel")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     skeleton_dragons
    if (check_for_card_in_hand("skeleton_dragons") is not None):
        # logger.log("playing skeleton_dragons")
        card_loc = check_for_card_in_hand("skeleton_dragons")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     skeleton_king
    if (check_for_card_in_hand("skeleton_king") is not None):
        # logger.log("playing skeleton_king")
        card_loc = check_for_card_in_hand("skeleton_king")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     skeletons
    if (check_for_card_in_hand("skeletons") is not None):
        # logger.log("playing skeletons")
        card_loc = check_for_card_in_hand("skeletons")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     valk
    if (check_for_card_in_hand("valk") is not None):
        # logger.log("playing valk")
        card_loc = check_for_card_in_hand("valk")
        offset = 25
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     archer_queen
    if (check_for_card_in_hand("archer_queen") is not None):
        # logger.log("playing archer_queen")
        card_loc = check_for_card_in_hand("archer_queen")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     archers
    if (check_for_card_in_hand("archers") is not None):
        # logger.log("playing archers")
        card_loc = check_for_card_in_hand("archers")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     baby_dragon
    if (check_for_card_in_hand("baby_dragon") is not None):
        # logger.log("playing baby_dragon")
        card_loc = check_for_card_in_hand("baby_dragon")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     bomber
    if (check_for_card_in_hand("bomber") is not None):
        # logger.log("playing bomber")
        card_loc = check_for_card_in_hand("bomber")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     bowler
    if (check_for_card_in_hand("bowler") is not None):
        # logger.log("playing bowler")
        card_loc = check_for_card_in_hand("bowler")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     cannon_cart
    if (check_for_card_in_hand("cannon_cart") is not None):
        # logger.log("playing cannon_cart")
        card_loc = check_for_card_in_hand("cannon_cart")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     dart_goblin
    if (check_for_card_in_hand("dart_goblin") is not None):
        # logger.log("playing dart_goblin")
        card_loc = check_for_card_in_hand("dart_goblin")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     e_dragon
    if (check_for_card_in_hand("e_dragon") is not None):
        # logger.log("playing e_dragon")
        card_loc = check_for_card_in_hand("e_dragon")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     e_wiz
    if (check_for_card_in_hand("e_wiz") is not None):
        # logger.log("playing e_wiz")
        card_loc = check_for_card_in_hand("e_wiz")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     elixer_golem
    if (check_for_card_in_hand("elixer_golem") is not None):
        # logger.log("playing elixer_golem")
        card_loc = check_for_card_in_hand("elixer_golem")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     executioner
    if (check_for_card_in_hand("executioner") is not None):
        # logger.log("playing executioner")
        card_loc = check_for_card_in_hand("executioner")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     fire_spirit
    if (check_for_card_in_hand("fire_spirit") is not None):
        # logger.log("playing fire_spirit")
        card_loc = check_for_card_in_hand("fire_spirit")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     firecracker
    if (check_for_card_in_hand("firecracker") is not None):
        # logger.log("playing firecracker")
        card_loc = check_for_card_in_hand("firecracker")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     flying_machine
    if (check_for_card_in_hand("flying_machine") is not None):
        # logger.log("playing flying_machine")
        card_loc = check_for_card_in_hand("flying_machine")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     hunter
    if (check_for_card_in_hand("hunter") is not None):
        # logger.log("playing hunter")
        card_loc = check_for_card_in_hand("hunter")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     ice_wizard
    if (check_for_card_in_hand("ice_wizard") is not None):
        # logger.log("playing ice_wizard")
        card_loc = check_for_card_in_hand("ice_wizard")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     inferno_dragon
    if (check_for_card_in_hand("inferno_dragon") is not None):
        # logger.log("playing inferno_dragon")
        card_loc = check_for_card_in_hand("inferno_dragon")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     magic_archer
    if (check_for_card_in_hand("magic_archer") is not None):
        # logger.log("playing magic_archer")
        card_loc = check_for_card_in_hand("magic_archer")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     mother_witch
    if (check_for_card_in_hand("mother_witch") is not None):
        # logger.log("playing mother_witch")
        card_loc = check_for_card_in_hand("mother_witch")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     musketeer
    if (check_for_card_in_hand("musketeer") is not None):
        # logger.log("playing musketeer")
        card_loc = check_for_card_in_hand("musketeer")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     night_witch
    if (check_for_card_in_hand("night_witch") is not None):
        # logger.log("playing night_witch")
        card_loc = check_for_card_in_hand("night_witch")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     sparky
    if (check_for_card_in_hand("sparky") is not None):
        # logger.log("playing sparky")
        card_loc = check_for_card_in_hand("sparky")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     spear_goblins
    if (check_for_card_in_hand("spear_goblins") is not None):
        # logger.log("playing spear_goblins")
        card_loc = check_for_card_in_hand("spear_goblins")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     three_musketeers
    if (check_for_card_in_hand("three_musketeers") is not None):
        # logger.log("playing three_musketeers")
        card_loc = check_for_card_in_hand("three_musketeers")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     goblin_gang
    if (check_for_card_in_hand("goblin_gang") is not None):
        # logger.log("playing goblin_gang")
        card_loc = check_for_card_in_hand("goblin_gang")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     rascals
    if (check_for_card_in_hand("rascals") is not None):
        # logger.log("playing rascals")
        card_loc = check_for_card_in_hand("rascals")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
#     zappies
    if (check_for_card_in_hand("zappies") is not None):
        # logger.log("playing zappies")
        card_loc = check_for_card_in_hand("zappies")
        offset = 100
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, offset)
# spawners
#     elixer_pump
    if (check_for_card_in_hand("elixer_pump") is not None):
        # logger.log("playing elixer_pump")
        card_loc = check_for_card_in_hand("elixer_pump")
        return play_spawner_card(card_loc)
#     furnace
    if (check_for_card_in_hand("furnace") is not None):
        # logger.log("playing furnace")
        card_loc = check_for_card_in_hand("furnace")
        return play_spawner_card(card_loc)
#     goblin_hut
    if (check_for_card_in_hand("goblin_hut") is not None):
        # logger.log("playing goblin_hut")
        card_loc = check_for_card_in_hand("goblin_hut")
        return play_spawner_card(card_loc)
#     tombstone
    if (check_for_card_in_hand("tombstone") is not None):
        # logger.log("playing tombstone")
        card_loc = check_for_card_in_hand("tombstone")
        return play_spawner_card(card_loc)
# hogs
#     balloon
    if (check_for_card_in_hand("balloon") is not None):
        # logger.log("playing balloon")
        card_loc = check_for_card_in_hand("balloon")
        return play_hogs_card(card_loc)
#     battle_ram
    if (check_for_card_in_hand("battle_ram") is not None):
        # logger.log("playing battle_ram")
        card_loc = check_for_card_in_hand("battle_ram")
        return play_hogs_card(card_loc)
#     hog
    if (check_for_card_in_hand("hog") is not None):
        # logger.log("playing hog")
        card_loc = check_for_card_in_hand("hog")
        return play_hogs_card(card_loc)
#     royal_hogs
    if (check_for_card_in_hand("royal_hogs") is not None):
        # logger.log("playing royal_hogs")
        card_loc = check_for_card_in_hand("royal_hogs")
        return play_hogs_card(card_loc)
#     ram_rider
    if (check_for_card_in_hand("ram_rider") is not None):
        # logger.log("playing ram_rider")
        card_loc = check_for_card_in_hand("ram_rider")
        return play_hogs_card(card_loc)
# spells

#     clone
    # we not gonna play clone
#     fireball
    if (check_for_card_in_hand("fireball") is not None):
        # logger.log("playing fireball")
        card_loc = check_for_card_in_hand("fireball")
        return play_card_at_a_random_coord(card_loc, [[122, 220], [298, 227]])
#     freeze
    if (check_for_card_in_hand("freeze") is not None):
        card_loc = check_for_card_in_hand("freeze")
        return play_card_on_enemy_with_offset(
            card_loc, enemy_troop_position, 0)
#     log
    if (check_for_card_in_hand("log") is not None):
        # logger.log("playing log")
        card_loc = check_for_card_in_hand("log")
        return play_card_at_a_random_coord(card_loc, [[122, 220], [298, 227]])


#     rage
    if (check_for_card_in_hand("rage") is not None):
        # logger.log("playing rage")
        card_loc = check_for_card_in_hand("rage")
        return play_spawner_card(card_loc)
#     rocket
    if (check_for_card_in_hand("rocket") is not None):
        # logger.log("playing rocket")
        card_loc = check_for_card_in_hand("rocket")
        return play_card_at_a_random_coord(card_loc, [[122, 220], [298, 227]])

#     tornado
    if (check_for_card_in_hand("tornado") is not None):
        # logger.log("playing tornado")
        card_loc = check_for_card_in_hand("tornado")
        return play_card_at_a_random_coord(card_loc, [[123, 252], [295, 245]])
#     earthquake
    if (check_for_card_in_hand("earthquake") is not None):
        # logger.log("playing earthquake")
        card_loc = check_for_card_in_hand("earthquake")
        return play_card_at_a_random_coord(card_loc, [[123, 252], [295, 245]])
#     graveyard
    if (check_for_card_in_hand("graveyard") is not None):
        # logger.log("playing graveyard")
        card_loc = check_for_card_in_hand("graveyard")
        return play_card_at_a_random_coord(card_loc, [[122, 220], [298, 227]])
#     lightning
    if (check_for_card_in_hand("lightning") is not None):
        # logger.log("playing lightning")
        card_loc = check_for_card_in_hand("lightning")
        return play_card_at_a_random_coord(card_loc, [[123, 252], [295, 245]])
#     royal_delivery
    if (check_for_card_in_hand("royal_delivery") is not None):
        # logger.log("playing royal_delivery")
        card_loc = check_for_card_in_hand("royal_delivery")
        return play_card_at_a_random_coord(card_loc, [[122, 220], [298, 227]])

# check for clusters
    clusters = check_board_for_clusters()
    if clusters is not None:
        #print("Found clusters")
        #     arrows
        if (check_for_card_in_hand("arrows") is not None):
            # logger.log("playing arrows")
            # click card
            card_loc = check_for_card_in_hand("arrows")
            placement = clusters
            if placement[1] < 250:
                return
            elif card_loc is not None:
                click(card_loc[0], card_loc[1])
                time.sleep(0.2)
                click(placement[0], placement[1])
                time.sleep(0.2)
            return
    #     poison
        if (check_for_card_in_hand("poison") is not None):
            # logger.log("playing poison")
            card_loc = check_for_card_in_hand("poison")
            placement = clusters
            if placement[1] < 250:
                return
            elif card_loc is not None:
                click(card_loc[0], card_loc[1])
                time.sleep(0.2)
                click(placement[0], placement[1])
                time.sleep(0.2)
            return
    #     zap
        if (check_for_card_in_hand("zap") is not None):
            # logger.log("playing zap")
            card_loc = check_for_card_in_hand("zap")
            placement = clusters
            if card_loc is not None:
                click(card_loc[0], card_loc[1])
                time.sleep(0.2)
                click(placement[0], placement[1])
                time.sleep(0.2)
            return
    #     snowball
        if (check_for_card_in_hand("snowball") is not None):
            # logger.log("playing snowball")
            card_loc = check_for_card_in_hand("snowball")
            placement = clusters
            if placement[1] < 200:
                return
            elif card_loc is not None:
                click(card_loc[0], card_loc[1])
                time.sleep(0.2)
                click(placement[0], placement[1])
                time.sleep(0.2)
            return


# etc
#     mortar
    if (check_for_card_in_hand("mortar") is not None):
        # logger.log("playing mortar")
        card_loc = check_for_card_in_hand("mortar")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [114, 346],
                [176, 336],
                [298, 336],
                [246, 339]
            ]
        )
#     princess
    if (check_for_card_in_hand("princess") is not None):
        # logger.log("playing princess")
        card_loc = check_for_card_in_hand("princess")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [114, 346],
                [176, 336],
                [298, 336],
                [246, 339]
            ]
        )
#     wall_breaker
    if (check_for_card_in_hand("wall_breaker") is not None):
        # logger.log("playing wall_breaker")
        card_loc = check_for_card_in_hand("wall_breaker")
        return play_card_at_a_random_coord(card_loc, [[212, 333], [205, 502]])
#     lavahound
    if (check_for_card_in_hand("lavahound") is not None):
        # logger.log("playing lavahound")
        card_loc = check_for_card_in_hand("lavahound")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [78, 502],
                [189, 502],
                [236, 507],
                [355, 497]
            ]
        )
#     golem
    if (check_for_card_in_hand("golem") is not None):
        # logger.log("playing golem")
        card_loc = check_for_card_in_hand("golem")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [78, 502],
                [189, 502],
                [236, 507],
                [355, 497]
            ]
        )
#     xbow
    if (check_for_card_in_hand("xbow") is not None):
        # logger.log("playing xbow")
        card_loc = check_for_card_in_hand("xbow")
        return play_card_at_a_random_coord(
            card_loc,
            [
                [114, 346],
                [176, 336],
                [298, 336],
                [246, 339]
            ]
        )
#     mirror
    # not gonna play mirror
# endregion


def find_cluster(x_region=[0, 100], y_region=[0, 100]):
    section1_pix_ar = []
    ss_img = screenshot()
    ss = numpy.asarray(ss_img)
    x = x_region[0]

    while x < x_region[1]:
        y = y_region[0]
        while y < y_region[1]:
            pix = ss[y][x]
            section1_pix_ar.append(pix)
            y = y + 1
        x = x + 1
    avg_pix = get_avg_pix(section1_pix_ar)
    return avg_pix


def get_avg_pix(ar):
    r_total = 0
    g_total = 0
    b_total = 0

    pixel_total = 0
    for pix in ar:
        # R color
        r_total = r_total + pix[0]
        # g
        g_total = g_total + pix[1]
        # b
        b_total = b_total + pix[2]
        # add pixel to count
        pixel_total = pixel_total + 1
    r_avg = r_total / pixel_total
    b_avg = b_total / pixel_total
    g_avg = g_total / pixel_total
    avg_pix = [r_avg, g_avg, b_avg]
    return avg_pix


def verify_cluster(RGB_ar):
    # print(RGB_ar)
    r = RGB_ar[0]
    g = RGB_ar[1]
    b = RGB_ar[2]
    if b + 10 > r:
        return False
    if g + 10 > r:
        return False
    if 130 > r:
        return False

    if check_if_pix_in_deadzone(RGB_ar, [169, 117, 63]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [191, 131, 51]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [209, 175, 67]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [160, 130, 69]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [155, 125, 66]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [172, 120, 67]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [152, 120, 74]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [196, 132, 53]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [162, 110, 61]):
        return False
    if check_if_pix_in_deadzone(RGB_ar, [150, 104, 55]):
        return False

    return True


def check_if_pix_in_deadzone(rgb_ar, pix_to_ignore):
    pix_r = rgb_ar[0]
    pix_g = rgb_ar[1]
    pix_b = rgb_ar[2]
    sent_r = pix_to_ignore[0]
    sent_g = pix_to_ignore[1]
    sent_b = pix_to_ignore[2]
    if (
            pix_r > sent_r -
            5) and (
            pix_r < sent_r +
            5) and (
                pix_g > sent_g -
                5) and (
                    pix_g < sent_g +
                    5) and (
                        pix_b > sent_b -
                        5) and (
                            pix_b < sent_b +
            5):
        return True
    return False


def check_region_for_cluster(x_region, y_region):
    cluster_RGB = find_cluster(x_region, y_region)
    if verify_cluster(cluster_RGB):
        x_coord = (x_region[1] + x_region[0]) / 2
        y_coord = (y_region[1] + y_region[0]) / 2
        coords = [x_coord, y_coord]
        return coords
    return None


def check_board_for_clusters():
    r1 = check_region_for_cluster([73, 123], [178, 228])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([73, 123], [229, 278])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([73, 123], [279, 328])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([73, 123], [329, 378])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([73, 123], [379, 428])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([73, 123], [429, 455])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([124, 173], [178, 228])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([124, 173], [229, 278])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([124, 173], [279, 328])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([124, 173], [329, 378])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([124, 173], [379, 428])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([124, 173], [429, 455])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([174, 223], [178, 228])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([174, 223], [229, 278])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([174, 223], [279, 328])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([174, 223], [329, 378])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([174, 223], [379, 428])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([174, 223], [429, 455])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([224, 273], [178, 228])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([224, 273], [229, 278])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([224, 273], [279, 328])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([224, 273], [329, 378])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([224, 273], [379, 428])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([224, 273], [429, 455])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([274, 323], [178, 228])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([274, 323], [229, 278])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([274, 323], [279, 328])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([274, 323], [329, 378])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([274, 323], [379, 428])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([274, 323], [429, 455])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([324, 350], [178, 228])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([324, 350], [229, 278])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([324, 350], [279, 328])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([324, 350], [329, 378])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([324, 350], [379, 428])
    if r1 is not None:
        return r1
    r1 = check_region_for_cluster([324, 350], [429, 455])
    if r1 is not None:
        return r1
