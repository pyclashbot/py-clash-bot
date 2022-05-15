import time
from image_rec import find_references
import pyautogui
import random


def random_placement_coord_maker():

    n = random.randint(1, 6)
    coords = [1] * 2
    if n == 0:
        coords[0] = 55
        coords[1] = 333
    if n == 1:
        coords[0] = 55
        coords[1] = 333
    if n == 2:
        coords[0] = 73
        coords[1] = 439
    if n == 3:
        coords[0] = 177
        coords[1] = 502
    if n == 4:
        coords[0] = 240
        coords[1] = 515
    if n == 5:
        coords[0] = 346
        coords[1] = 429
    if n == 6:
        coords[0] = 364
        coords[1] = 343

    return coords

# region fight


def fight_with_deck_list(deck_list, enemy_troop_position):
    placement_coords = enemy_troop_position
    # turrets
    # if tesla in deck and in hand
    if (check_if_card_in_deck(deck_list, "tesla")) and (check_for_card_in_hand("tesla") is not None):
        print("Decided to play tesla")
        card_coords = check_for_card_in_hand("tesla")
        placement_coords = [212, 385]
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# melee tanks
     # if bandit in deck and bandit in hand
    if (check_if_card_in_deck(deck_list, "bandit")) and (check_for_card_in_hand("bandit") is not None):
        print("Decided to play bandit")
        card_coords = check_for_card_in_hand("bandit")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+45
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if dark_knight in deck and dark_knight in hand
    if (check_if_card_in_deck(deck_list, "dark_knight")) and (check_for_card_in_hand("dark_knight") is not None):
        print("Decided to play dark_knight")
        card_coords = check_for_card_in_hand("dark_knight")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if fire_spirit in deck and fire_spirit in hand
    if (check_if_card_in_deck(deck_list, "fire_spirit")) and (check_for_card_in_hand("fire_spirit") is not None):
        print("Decided to play fire_spirit")
        card_coords = check_for_card_in_hand("fire_spirit")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+30
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if mega_knight in deck and mega_knight in hand
    if (check_if_card_in_deck(deck_list, "mega_knight")) and (check_for_card_in_hand("mega_knight") is not None):
        print("Decided to play mega_knight")
        card_coords = check_for_card_in_hand("mega_knight")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1] + 30
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if mini_pekka in deck and mini_pekka in hand
    if (check_if_card_in_deck(deck_list, "mini_pekka")) and (check_for_card_in_hand("mini_pekka") is not None):
        print("Decided to play mini_pekka")
        card_coords = check_for_card_in_hand("mini_pekka")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if pekka in deck and pekka in hand
    if (check_if_card_in_deck(deck_list, "pekka")) and (check_for_card_in_hand("pekka") is not None):
        print("Decided to play pekka")
        card_coords = check_for_card_in_hand("pekka")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if royal_ghost in deck and royal_ghost in hand
    if (check_if_card_in_deck(deck_list, "royal_ghost")) and (check_for_card_in_hand("royal_ghost") is not None):
        print("Decided to play royal_ghost")
        card_coords = check_for_card_in_hand("royal_ghost")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if royal_recruits in deck and in hand
    if (check_if_card_in_deck(deck_list, "royal_recruits")) and (check_for_card_in_hand("royal_recruits") is not None):
        print("Decided to play royal_recruits")
        card_coords = check_for_card_in_hand("royal_recruits")
        placement_coords = [215, 390]
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if valk in deck and valk in hand
    if (check_if_card_in_deck(deck_list, "valk")) and (check_for_card_in_hand("valk") is not None):
        print("Decided to play valk")
        card_coords = check_for_card_in_hand("valk")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if barb_barrel in deck and in hand
    if (check_if_card_in_deck(deck_list, "barb_barrel")) and (check_for_card_in_hand("barb_barrel") is not None) and (placement_coords is not None):
        print("Decided to play barb_barrel")
        card_coords = check_for_card_in_hand("barb_barrel")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+30
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# ranged
    # if e_wiz in deck and e_wiz in hand
    if (check_if_card_in_deck(deck_list, "e_wiz")) and (check_for_card_in_hand("e_wiz") is not None):
        print("Decided to play e_wiz")
        card_coords = check_for_card_in_hand("e_wiz")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+25
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if firecracker in deck and firecracker in hand
    if (check_if_card_in_deck(deck_list, "firecracker")) and (check_for_card_in_hand("firecracker") is not None):
        print("Decided to play firecracker")
        card_coords = check_for_card_in_hand("firecracker")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if goblin_gang in deck and goblin_gang in hand
    if (check_if_card_in_deck(deck_list, "goblin_gang")) and (check_for_card_in_hand("goblin_gang") is not None):
        print("Decided to play goblin_gang")
        card_coords = check_for_card_in_hand("goblin_gang")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+35
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if mother_witch in deck and in hand
    if (check_if_card_in_deck(deck_list, "mother_witch")) and (check_for_card_in_hand("mother_witch") is not None):
        print("Decided to play mother_witch")
        card_coords = check_for_card_in_hand("mother_witch")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if musketeer in deck and musketeer in hand
    if (check_if_card_in_deck(deck_list, "musketeer")) and (check_for_card_in_hand("musketeer") is not None):
        print("Decided to play musketeer")
        card_coords = check_for_card_in_hand("musketeer")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if night_witch in deck and in hand
    if (check_if_card_in_deck(deck_list, "night_witch")) and (check_for_card_in_hand("night_witch") is not None):
        print("Decided to play night_witch")
        card_coords = check_for_card_in_hand("night_witch")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if witch in deck and in hand
    if (check_if_card_in_deck(deck_list, "witch")) and (check_for_card_in_hand("witch") is not None):
        print("Decided to play witch")
        card_coords = check_for_card_in_hand("witch")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if archer_queen in deck and archer_queen in hand
    if (check_if_card_in_deck(deck_list, "archer_queen")) and (check_for_card_in_hand("archer_queen") is not None):
        print("Decided to play archer_queen")
        card_coords = check_for_card_in_hand("archer_queen")

        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# spells
    # if fireball in deck and in hand
    if (check_if_card_in_deck(deck_list, "fireball")) and (check_for_card_in_hand("fireball") is not None):
        print("Decided to play fireball")
        card_coords = check_for_card_in_hand("fireball")
        n99 = random.randint(1, 2)
        if n99 == 1:
            placement_coords = [97, 203]
        if n99 == 2:
            placement_coords = [320, 208]
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if poison in deck and in hand
    if (check_if_card_in_deck(deck_list, "poison")) and (check_for_card_in_hand("poison") is not None):
        print("Decided to play poison")
        card_coords = check_for_card_in_hand("poison")
        n99 = random.randint(1, 2)
        if n99 == 1:
            placement_coords = [97, 203]
        if n99 == 2:
            placement_coords = [320, 208]
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# hogs
    # if battle_ram in deck and battle_ram in hand
    if (check_if_card_in_deck(deck_list, "battle_ram")) and (check_for_card_in_hand("battle_ram") is not None):
        print("Decided to play archer_queen")
        card_coords = check_for_card_in_hand("archer_queen")
        placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if hog in deck and hog in hand
    if (check_if_card_in_deck(deck_list, "hog")) and (check_for_card_in_hand("hog") is not None):
        print("Decided to play hog")
        card_coords = check_for_card_in_hand("hog")
        placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if ram_rider in deck and ram_rider in hand
    if (check_if_card_in_deck(deck_list, "ram_rider")) and (check_for_card_in_hand("ram_rider") is not None):
        print("Decided to play ram_rider")
        card_coords = check_for_card_in_hand("ram_rider")
        placement_coords = random_placement_coord_maker()
        # click card
        if card_coords is not None:
            pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return

    print("No moves found. Waiting")
    time.sleep(3)
# endregion


def add_card_to_deck(deck_list, card):
    if deck_list[0] == "empty":
        deck_list[0] = card
        return deck_list
    if deck_list[1] == "empty":
        deck_list[1] = card
        return deck_list
    if deck_list[2] == "empty":
        deck_list[2] = card
        return deck_list
    if deck_list[3] == "empty":
        deck_list[3] = card
        return deck_list
    if deck_list[4] == "empty":
        deck_list[4] = card
        return deck_list
    if deck_list[5] == "empty":
        deck_list[5] = card
        return deck_list
    if deck_list[6] == "empty":
        deck_list[6] = card
        return deck_list
    if deck_list[7] == "empty":
        deck_list[7] = card
        return deck_list
    return deck_list

# region deck card checks


def check_deck_for_zap(deck_image):
    references = [
        "zap_1.png",
        "zap_2.png",
        "zap_3.png",
        "zap_4.png",
        "zap_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found zap in deck")
            return location
    return None


def check_deck_for_witch(deck_image):
    references = [
        "witch_1.png",
        "witch_2.png",
        "witch_3.png",
        "witch_4.png",
        "witch_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found witch in deck")
            return location
    return None


def check_deck_for_golden_knight(deck_image):
    references = [
        "golden_knight_1.png",
        "golden_knight_2.png",
        "golden_knight_3.png",
        "golden_knight_4.png",
        "golden_knight_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found golden knight in deck")
            return location
    return None


def check_deck_for_royal_hogs(deck_image):
    references = [
        "royal_hogs_1.png",
        "royal_hogs_2.png",
        "royal_hogs_3.png",
        "royal_hogs_4.png",
        "royal_hogs_5.png",
        "royal_hogs_6.png",
        "royal_hogs_7.png",
        "royal_hogs_8.png",
        "royal_hogs_9.png",
        "royal_hogs_10.png",
        "royal_hogs_11.png",
        "royal_hogs_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal hogs in deck")
            return location
    return None


def check_deck_for_royal_giant(deck_image):
    references = [
        "royal_giant_1.png",
        "royal_giant_2.png",
        "royal_giant_3.png",
        "royal_giant_4.png",
        "royal_giant_5.png",
        "royal_giant_6.png",
        "royal_giant_7.png",
        "royal_giant_8.png",
        "royal_giant_9.png",
        "royal_giant_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal giant in deck")
            return location
    return None


def check_deck_for_cannon(deck_image):
    references = [
        "cannon_1.png",
        "cannon_2.png",
        "cannon_3.png",
        "cannon_4.png",
        "cannon_5.png",
        "cannon_6.png",
        "cannon_7.png",
        "cannon_8.png",
        "cannon_9.png",
        "cannon_10.png",
        "cannon_11.png",
        "cannon_12.png",
        "cannon_13.png",
        "cannon_14.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found cannon in deck")
            return location
    return None


def check_deck_for_fireball(deck_image):
    references = [
        "fireball_1.png",
        "fireball_2.png",
        "fireball_3.png",
        "fireball_4.png",
        "fireball_5.png",
        "fireball_6.png",
        "fireball_7.png",
        "fireball_8.png",
        "fireball_9.png",
        "fireball_10.png",
        "fireball_11.png",
        "fireball_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found fireball in deck")
            return location
    return None


def check_deck_for_earthquake(deck_image):
    references = [
        "earthquake_1.png",
        "earthquake_2.png",
        "earthquake_3.png",
        "earthquake_4.png",
        "earthquake_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found earthquake in deck")
            return location
    return None


def check_deck_for_log(deck_image):
    references = [
        "log_1.png",
        "log_2.png",
        "log_3.png",
        "log_4.png",
        "log_5.png",
        "log_6.png",
        "log_7.png",
        "log_8.png",
        "log_9.png",
        "log_10.png",
        "log_11.png",
        "log_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found log in deck")
            return location
    return None


def check_deck_for_baby_dragon(deck_image):
    references = [
        "baby_dragon_1.png",
        "baby_dragon_2.png",
        "baby_dragon_3.png",
        "baby_dragon_4.png",
        "baby_dragon_5.png",
        "baby_dragon_6.png",
        "baby_dragon_7.png",
        "baby_dragon_8.png",
        "baby_dragon_9.png",
        "baby_dragon_10.png",
        "baby_dragon_11.png",
        "baby_dragon_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found baby dragon in deck")
            return location
    return None


def check_deck_for_pekka(deck_image):
    references = [
        "pekka_1.png",
        "pekka_2.png",
        "pekka_3.png",
        "pekka_5.png",
        "pekka_6.png",
        "pekka_7.png",
        "pekka_8.png",
        "pekka_9.png",
        "pekka_10.png",
        "pekka_11.png",
        "pekka_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found pekka in deck")
            return location
    return None


def check_deck_for_mother_witch(deck_image):
    references = [
        "mother_witch_1.png",
        "mother_witch_2.png",
        "mother_witch_3.png",
        "mother_witch_4.png",
        "mother_witch_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mother witch in deck")
            return location
    return None


def check_deck_for_goblin_hut(deck_image):
    references = [
        "goblin_hut_1.png",
        "goblin_hut_2.png",
        "goblin_hut_3.png",
        "goblin_hut_4.png",
        "goblin_hut_5.png",
        "goblin_hut_6.png",
        "goblin_hut_7.png",
        "goblin_hut_8.png",
        "goblin_hut_9.png",
        "goblin_hut_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin hut in deck")
            return location
    return None


def check_deck_for_mighty_miner(deck_image):
    references = [
        "mighty_miner_1.png",
        "mighty_miner_2.png",
        "mighty_miner_3.png",
        "mighty_miner_4.png",
        "mighty_miner_5.png",
        "mighty_miner_6.png",
        "mighty_miner_7.png",
        "mighty_miner_8.png",
        "mighty_miner_9.png",
        "mighty_miner_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mighty miner in deck")
            return location
    return None


def check_deck_for_fisherman(deck_image):
    references = [
        "fisherman_1.png",
        "fisherman_2.png",
        "fisherman_3.png",
        "fisherman_4.png",
        "fisherman_5.png",
        "fisherman_6.png",
        "fisherman_7.png",
        "fisherman_8.png",
        "fisherman_9.png",
        "fisherman_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found fisherman in deck")
            return location
    return None


def check_deck_for_inferno_tower(deck_image):
    references = [
        "inferno_tower_1.png",
        "inferno_tower_2.png",
        "inferno_tower_3.png",
        "inferno_tower_4.png",
        "inferno_tower_5.png",
        "inferno_tower_6.png",
        "inferno_tower_7.png",
        "inferno_tower_8.png",
        "inferno_tower_9.png",
        "inferno_tower_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found inferno tower in deck")
            return location
    return None


def check_deck_for_archers(deck_image):
    references = [
        "archers_1.png",
        "archers_2.png",
        "archers_3.png",
        "archers_4.png",
        "archers_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found archers in deck")
            return location
    return None


def check_deck_for_bats(deck_image):
    references = [
        "bats_1.png",
        "bats_2.png",
        "bats_3.png",
        "bats_4.png",
        "bats_5.png",
        "bats_6.png",
        "bats_7.png",
        "bats_8.png",
        "bats_9.png",
        "bats_10.png",
        "bats_11.png",
        "bats_12.png",
        "bats_13.png",
        "bats_14.png",
        "bats_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bats in deck")
            return location
    return None


def check_deck_for_tombstone(deck_image):
    references = [
        "tombstone_1.png",
        "tombstone_2.png",
        "tombstone_3.png",
        "tombstone_4.png",
        "tombstone_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found tombstone in deck")
            return location
    return None


def check_deck_for_e_giant(deck_image):
    references = [
        "e_giant_1.png",
        "e_giant_2.png",
        "e_giant_3.png",
        "e_giant_4.png",
        "e_giant_5.png",
        "e_giant_6.png",
        "e_giant_7.png",
        "e_giant_8.png",
        "e_giant_9.png",
        "e_giant_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found e giant in deck")
            return location
    return None


def check_deck_for_rocket(deck_image):
    references = [
        "rocket_1.png",
        "rocket_2.png",
        "rocket_3.png",
        "rocket_4.png",
        "rocket_5.png",
        "rocket_6.png",
        "rocket_7.png",
        "rocket_8.png",
        "rocket_9.png",
        "rocket_10.png",
        "rocket_11.png",
        "rocket_12.png",
        "rocket_13.png",
        "rocket_14.png",
        "rocket_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found rocket in deck")
            return location
    return None


def check_deck_for_graveyard(deck_image):
    references = [
        "graveyard_1.png",
        "graveyard_2.png",
        "graveyard_3.png",
        "graveyard_4.png",
        "graveyard_5.png",
        "graveyard_6.png",
        "graveyard_7.png",
        "graveyard_8.png",
        "graveyard_9.png",
        "graveyard_10.png",
        "graveyard_11.png",
        "graveyard_12.png",
        "graveyard_13.png",
        "graveyard_14.png",
        "graveyard_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found graveyard in deck")
            return location
    return None


def check_deck_for_healer(deck_image):
    references = [
        "healer_1.png",
        "healer_2.png",
        "healer_3.png",
        "healer_4.png",
        "healer_5.png",
        "healer_6.png",
        "healer_7.png",
        "healer_8.png",
        "healer_9.png",
        "healer_10.png",
        "healer_11.png",
        "healer_12.png",
        "healer_13.png",
        "healer_14.png",
        "healer_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found healer in deck")
            return location
    return None


def check_deck_for_barb_barrel(deck_image):
    references = [
        "barb_barrel_1.png",
        "barb_barrel_2.png",
        "barb_barrel_3.png",
        "barb_barrel_4.png",
        "barb_barrel_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found barb barrel in deck")
            return location
    return None


def check_deck_for_archer_queen(deck_image):
    references = [
        "archer_queen_1.png",
        "archer_queen_2.png",
        "archer_queen_3.png",
        "archer_queen_4.png",
        "archer_queen_5.png",
        "archer_queen_6.png",
        "archer_queen_7.png",
        "archer_queen_8.png",
        "archer_queen_9.png",
        "archer_queen_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found archer queen in deck")
            return location
    return None


def check_deck_for_e_wiz(deck_image):
    references = [
        "e_wiz_1.png",
        "e_wiz_2.png",
        "e_wiz_3.png",
        "e_wiz_4.png",
        "e_wiz_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found e wiz in deck")
            return location
    return None


def check_deck_for_battle_ram(deck_image):
    references = [
        "battle_ram_1.png",
        "battle_ram_2.png",
        "battle_ram_3.png",
        "battle_ram_4.png",
        "battle_ram_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found battle ram in deck")
            return location
    return None


def check_deck_for_spear_goblins(deck_image):
    references = [
        "spear_goblins_1.png",
        "spear_goblins_2.png",
        "spear_goblins_3.png",
        "spear_goblins_4.png",
        "spear_goblins_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found spear goblins in deck")
            return location
    return None


def check_deck_for_arrows(deck_image):
    references = [
        "arrows_1.png",
        "arrows_2.png",
        "arrows_3.png",
        "arrows_4.png",
        "arrows_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found arrows in deck")
            return location
    return None


def check_deck_for_skeleton_army(deck_image):
    references = [
        "skeleton_army_1.png",
        "skeleton_army_2.png",
        "skeleton_army_3.png",
        "skeleton_army_4.png",
        "skeleton_army_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton army in deck")
            return location
    return None


def check_deck_for_wizard(deck_image):
    references = [
        "wizard_1.png",
        "wizard_2.png",
        "wizard_3.png",
        "wizard_4.png",
        "wizard_5.png",
        "wizard_6.png",
        "wizard_7.png",
        "wizard_8.png",
        "wizard_9.png",
        "wizard_10.png",
        "wizard_11.png",
        "wizard_12.png",
        "wizard_13.png",
        "wizard_14.png",
        "wizard_15.png",
        "wizard_16.png",
        "wizard_17.png",
        "wizard_18.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found wizard in deck")
            return location
    return None


def check_deck_for_skeleton_dragons(deck_image):
    references = [
        "skeleton_dragons_1.png",
        "skeleton_dragons_2.png",
        "skeleton_dragons_3.png",
        "skeleton_dragons_4.png",
        "skeleton_dragons_5.png",
        "skeleton_dragons_6.png",
        "skeleton_dragons_7.png",
        "skeleton_dragons_8.png",
        "skeleton_dragons_9.png",
        "skeleton_dragons_10.png",
        "skeleton_dragons_11.png",
        "skeleton_dragons_12.png",
        "skeleton_dragons_13.png",
        "skeleton_dragons_14.png",
        "skeleton_dragons_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton dragons in deck")
            return location
    return None


def check_deck_for_prince(deck_image):
    references = [
        "prince_1.png",
        "prince_2.png",
        "prince_3.png",
        "prince_4.png",
        "prince_5.png",
        "prince_6.png",
        "prince_7.png",
        "prince_8.png",
        "prince_9.png",
        "prince_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found prince in deck")
            return location
    return None


def check_deck_for_goblin_giant(deck_image):
    references = [
        "goblin_giant_1.png",
        "goblin_giant_2.png",
        "goblin_giant_3.png",
        "goblin_giant_4.png",
        "goblin_giant_5.png",
        "goblin_giant_6.png",
        "goblin_giant_7.png",
        "goblin_giant_8.png",
        "goblin_giant_9.png",
        "goblin_giant_10.png",
        "goblin_giant_11.png",
        "goblin_giant_12.png",
        "goblin_giant_13.png",
        "goblin_giant_14.png",
        "goblin_giant_15.png",
        "goblin_giant_16.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin giant in deck")
            return location
    return None


def check_deck_for_zappies(deck_image):
    references = [
        "zappies_1.png",
        "zappies_2.png",
        "zappies_3.png",
        "zappies_4.png",
        "zappies_5.png",
        "zappies_6.png",
        "zappies_7.png",
        "zappies_8.png",
        "zappies_9.png",
        "zappies_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found zappies in deck")
            return location
    return None


def check_deck_for_lavahound(deck_image):
    references = [
        "lavahound_1.png",
        "lavahound_2.png",
        "lavahound_3.png",
        "lavahound_4.png",
        "lavahound_5.png",
        "lavahound_6.png",
        "lavahound_7.png",
        "lavahound_8.png",
        "lavahound_9.png",
        "lavahound_10.png",
        "lavahound_11.png",
        "lavahound_12.png",
        "lavahound_13.png",
        "lavahound_14.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found lavahound in deck")
            return location
    return None


def check_deck_for_lightning(deck_image):
    references = [
        "lightning_1.png",
        "lightning_2.png",
        "lightning_3.png",
        "lightning_4.png",
        "lightning_5.png",
        "lightning_6.png",
        "lightning_7.png",
        "lightning_8.png",
        "lightning_9.png",
        "lightning_10.png",
        "lightning_11.png",
        "lightning_12.png",
        "lightning_13.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found lightning in deck")
            return location
    return None


def check_deck_for_executioner(deck_image):
    references = [
        "executioner_1.png",
        "executioner_2.png",
        "executioner_3.png",
        "executioner_4.png",
        "executioner_5.png",
        "executioner_6.png",
        "executioner_7.png",
        "executioner_8.png",
        "executioner_9.png",
        "executioner_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found executioner in deck")
            return location
    return None


def check_deck_for_goblin_drill(deck_image):
    references = [
        "goblin_drill_1.png",
        "goblin_drill_2.png",
        "goblin_drill_3.png",
        "goblin_drill_4.png",
        "goblin_drill_5.png",
        "goblin_drill_6.png",
        "goblin_drill_7.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin drill in deck")
            return location
    return None


def check_deck_for_rage(deck_image):
    references = [
        "rage_1.png",
        "rage_2.png",
        "rage_4.png",
        "rage_5.png",
        "rage_6.png",
        "rage_7.png",
        "rage_8.png",
        "rage_9.png",
        "rage_10.png",
        "rage_11.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found rage in deck")
            return location
    return None


def check_deck_for_clone(deck_image):
    references = [
        "clone_1.png",
        "clone_2.png",
        "clone_3.png",
        "clone_5.png",
        "clone_6.png",
        "clone_7.png",
        "clone_8.png",
        "clone_9.png",
        "clone_10.png",
        "clone_11.png",
        "clone_12.png",
        "clone_13.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found clone in deck")
            return location
    return None


def check_deck_for_goblin_barrel(deck_image):
    references = [
        "goblin_barrel_1.png",
        "goblin_barrel_2.png",
        "goblin_barrel_3.png",
        "goblin_barrel_4.png",
        "goblin_barrel_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin barrel in deck")
            return location
    return None


def check_deck_for_minion_hoard(deck_image):
    references = [
        "minion_hoard_1.png",
        "minion_hoard_2.png",
        "minion_hoard_3.png",
        "minion_hoard_4.png",
        "minion_hoard_5.png",
        "minion_hoard_6.png",
        "minion_hoard_7.png",
        "minion_hoard_8.png",
        "minion_hoard_9.png",
        "minion_hoard_10.png",
        "minion_hoard_11.png",
        "minion_hoard_12.png",
        "minion_hoard_13.png",
        "minion_hoard_14.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found minion hoard in deck")
            return location
    return None


def check_deck_for_barbs(deck_image):
    references = [
        "barbs_1.png",
        "barbs_2.png",
        "barbs_3.png",
        "barbs_4.png",
        "barbs_5.png",
        "barbs_6.png",
        "barbs_7.png",
        "barbs_8.png",
        "barbs_9.png",
        "barbs_10.png",
        "barbs_11.png",
        "barbs_12.png",
        "barbs_13.png",
        "barbs_14.png",
        "barbs_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found barbs in deck")
            return location
    return None


def check_deck_for_tornado(deck_image):
    references = [
        "tornado_1.png",
        "tornado_2.png",
        "tornado_3.png",
        "tornado_4.png",
        "tornado_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found tornado in deck")
            return location
    return None


def check_deck_for_skeleton_barrel(deck_image):
    references = [
        "skeleton_barrel_1.png",
        "skeleton_barrel_2.png",
        "skeleton_barrel_3.png",
        "skeleton_barrel_4.png",
        "skeleton_barrel_5.png",
        "skeleton_barrel_6.png",
        "skeleton_barrel_7.png",
        "skeleton_barrel_8.png",
        "skeleton_barrel_9.png",
        "skeleton_barrel_10.png",
        "skeleton_barrel_11.png",
        "skeleton_barrel_12.png",
        "skeleton_barrel_13.png",
        "skeleton_barrel_14.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton barrel in deck")
            return location
    return None


def check_deck_for_miner(deck_image):
    references = [
        "miner_1.png",
        "miner_2.png",
        "miner_3.png",
        "miner_4.png",
        "miner_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found miner in deck")
            return location
    return None


def check_deck_for_skeletons(deck_image):
    references = [
        "skeletons_1.png",
        "skeletons_2.png",
        "skeletons_3.png",
        "skeletons_4.png",
        "skeletons_5.png",
        "skeletons_6.png",
        "skeletons_7.png",
        "skeletons_8.png",
        "skeletons_9.png",
        "skeletons_10.png",
        "skeletons_11.png",
        "skeletons_12.png",
        "skeletons_13.png",
        "skeletons_14.png",
        "skeletons_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeletons in deck")
            return location
    return None


def check_deck_for_elite_barbs(deck_image):
    references = [
        "elite_barbs_1.png",
        "elite_barbs_2.png",
        "elite_barbs_3.png",
        "elite_barbs_4.png",
        "elite_barbs_5.png",
        "elite_barbs_6.png",
        "elite_barbs_7.png",
        "elite_barbs_8.png",
        "elite_barbs_9.png",
        "elite_barbs_10.png",
        "elite_barbs_11.png",
        "elite_barbs_12.png",
        "elite_barbs_13.png",
        "elite_barbs_14.png",
        "elite_barbs_15.png",
        "elite_barbs_16.png",
        "elite_barbs_17.png",
        "elite_barbs_18.png",
        "elite_barbs_19.png",
        "elite_barbs_20.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found elite barbs in deck")
            return location
    return None


def check_deck_for_flying_machine(deck_image):
    references = [
        "flying_machine_1.png",
        "flying_machine_2.png",
        "flying_machine_3.png",
        "flying_machine_4.png",
        "flying_machine_5.png",
        "flying_machine_6.png",
        "flying_machine_7.png",
        "flying_machine_8.png",
        "flying_machine_9.png",
        "flying_machine_10.png",
        "flying_machine_11.png",
        "flying_machine_12.png",
        "flying_machine_13.png",
        "flying_machine_14.png",
        "flying_machine_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found flying machine in deck")
            return location
    return None


def check_deck_for_e_dragon(deck_image):
    references = [
        "e_dragon_1.png",
        "e_dragon_2.png",
        "e_dragon_3.png",
        "e_dragon_4.png",
        "e_dragon_5.png",
        "e_dragon_6.png",
        "e_dragon_7.png",
        "e_dragon_8.png",
        "e_dragon_9.png",
        "e_dragon_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found e dragon in deck")
            return location
    return None


def check_deck_for_xbow(deck_image):
    references = [
        "xbow_1.png",
        "xbow_2.png",
        "xbow_3.png",
        "xbow_4.png",
        "xbow_5.png",
        "xbow_6.png",
        "xbow_7.png",
        "xbow_8.png",
        "xbow_9.png",
        "xbow_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found xbow in deck")
            return location
    return None


def check_deck_for_elixer_golem(deck_image):
    references = [
        "elixer_golem_1.png",
        "elixer_golem_2.png",
        "elixer_golem_3.png",
        "elixer_golem_4.png",
        "elixer_golem_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found elixer golem in deck")
            return location
    return None


def check_deck_for_rascals(deck_image):
    references = [
        "rascals_1.png",
        "rascals_2.png",
        "rascals_3.png",
        "rascals_4.png",
        "rascals_5.png",
        "rascals_6.png",
        "rascals_7.png",
        "rascals_8.png",
        "rascals_9.png",
        "rascals_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found rascals in deck")
            return location
    return None


def check_deck_for_skeleton_king(deck_image):
    references = [
        "skeleton_king_1.png",
        "skeleton_king_2.png",
        "skeleton_king_3.png",
        "skeleton_king_4.png",
        "skeleton_king_5.png",
        "skeleton_king_6.png",
        "skeleton_king_7.png",
        "skeleton_king_8.png",
        "skeleton_king_9.png",
        "skeleton_king_10.png",
        "skeleton_king_11.png",
        "skeleton_king_12.png",
        "skeleton_king_13.png",
        "skeleton_king_14.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton king in deck")
            return location
    return None


def check_deck_for_balloon(deck_image):
    references = [
        "balloon_1.png",
        "balloon_2.png",
        "balloon_3.png",
        "balloon_4.png",
        "balloon_5.png",
        "balloon_6.png",
        "balloon_7.png",
        "balloon_8.png",
        "balloon_9.png",
        "balloon_10.png",
        "balloon_11.png",
        "balloon_12.png",
        "balloon_13.png",
        "balloon_14.png",
        "balloon_15.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found balloon in deck")
            return location
    return None


def check_deck_for_sparky(deck_image):
    references = [
        "sparky_1.png",
        "sparky_2.png",
        "sparky_3.png",
        "sparky_4.png",
        "sparky_5.png",
        "sparky_6.png",
        "sparky_7.png",
        "sparky_8.png",
        "sparky_9.png",
        "sparky_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found sparky in deck")
            return location
    return None


def check_deck_for_golem(deck_image):
    references = [
        "golem_1.png",
        "golem_2.png",
        "golem_3.png",
        "golem_4.png",
        "golem_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found golem in deck")
            return location
    return None


def check_deck_for_barb_hut(deck_image):
    references = [
        "barb_hut_1.png",
        "barb_hut_2.png",
        "barb_hut_3.png",
        "barb_hut_4.png",
        "barb_hut_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found barb hut in deck")
            return location
    return None


def check_deck_for_bomb_tower(deck_image):
    references = [
        "bomb_tower_1.png",
        "bomb_tower_2.png",
        "bomb_tower_3.png",
        "bomb_tower_4.png",
        "bomb_tower_5.png",
        "bomb_tower_6.png",
        "bomb_tower_7.png",
        "bomb_tower_8.png",
        "bomb_tower_9.png",
        "bomb_tower_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bomb tower in deck")
            return location
    return None


def check_deck_for_mortar(deck_image):
    references = [
        "mortar_1.png",
        "mortar_2.png",
        "mortar_3.png",
        "mortar_4.png",
        "mortar_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mortar in deck")
            return location
    return None


def check_deck_for_inferno_dragon(deck_image):
    references = [
        "inferno_dragon_1.png",
        "inferno_dragon_2.png",
        "inferno_dragon_3.png",
        "inferno_dragon_4.png",
        "inferno_dragon_5.png",
        "inferno_dragon_6.png",
        "inferno_dragon_7.png",
        "inferno_dragon_8.png",
        "inferno_dragon_9.png",
        "inferno_dragon_10.png",
        "inferno_dragon_11.png",
        "inferno_dragon_12.png",
        "inferno_dragon_13.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found inferno dragon in deck")
            return location
    return None


def check_deck_for_hunter(deck_image):
    references = [
        "hunter_1.png",
        "hunter_2.png",
        "hunter_3.png",
        "hunter_4.png",
        "hunter_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found hunter in deck")
            return location
    return None


def check_deck_for_giant(deck_image):
    references = [
        "giant_1.png",
        "giant_2.png",
        "giant_3.png",
        "giant_4.png",
        "giant_5.png",
        "giant_6.png",
        "giant_7.png",
        "giant_8.png",
        "giant_9.png",
        "giant_10.png",
        "giant_11.png",
        "giant_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found giant in deck")
            return location
    return None


def check_deck_for_freeze(deck_image):
    references = [
        "freeze_1.png",
        "freeze_2.png",
        "freeze_3.png",
        "freeze_4.png",
        "freeze_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found freeze in deck")
            return location
    return None


def check_deck_for_lumberjack(deck_image):
    references = [
        "lumberjack_1.png",
        "lumberjack_2.png",
        "lumberjack_3.png",
        "lumberjack_4.png",
        "lumberjack_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found lumberjack in deck")
            return location
    return None


def check_deck_for_bowler(deck_image):
    references = [
        "bowler_1.png",
        "bowler_2.png",
        "bowler_3.png",
        "bowler_4.png",
        "bowler_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bowler in deck")
            return location
    return None


def check_deck_for_dart_goblin(deck_image):
    references = [
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
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found dart goblin in deck")
            return location
    return None


def check_deck_for_mini_pekka(deck_image):
    references = [
        "mini_pekka_1.png",
        "mini_pekka_2.png",
        "mini_pekka_3.png",
        "mini_pekka_4.png",
        "mini_pekka_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mini pekka in deck")
            return location
    return None


def check_deck_for_mega_knight(deck_image):
    references = [
        "mega_knight_1.png",
        "mega_knight_2.png",
        "mega_knight_3.png",
        "mega_knight_4.png",
        "mega_knight_5.png",
        "mega_knight_6.png",
        "mega_knight_7.png",
        "mega_knight_8.png",
        "mega_knight_9.png",
        "mega_knight_10.png",
        "mega_knight_11.png",
        "mega_knight_12.png",
        "mega_knight_13.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mega knight in deck")
            return location
    return None


def check_deck_for_elixer_pump(deck_image):
    references = [
        "elixer_pump_1.png",
        "elixer_pump_2.png",
        "elixer_pump_3.png",
        "elixer_pump_4.png",
        "elixer_pump_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found elixer pump in deck")
            return location
    return None


def check_deck_for_giant_skeleton(deck_image):
    references = [
        "giant_skeleton_1.png",
        "giant_skeleton_2.png",
        "giant_skeleton_3.png",
        "giant_skeleton_4.png",
        "giant_skeleton_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found giant skeleton in deck")
            return location
    return None


def check_deck_for_magic_archer(deck_image):
    references = [
        "magic_archer_1.png",
        "magic_archer_2.png",
        "magic_archer_3.png",
        "magic_archer_4.png",
        "magic_archer_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found magic archer in deck")
            return location
    return None


def check_deck_for_firecracker(deck_image):
    references = [
        "firecracker_1.png",
        "firecracker_2.png",
        "firecracker_3.png",
        "firecracker_4.png",
        "firecracker_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found firecracker in deck")
            return location
    return None


def check_deck_for_knight(deck_image):
    references = [
        "knight_1.png",
        "knight_2.png",
        "knight_3.png",
        "knight_4.png",
        "knight_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found knight in deck")
            return location
    return None


def check_deck_for_cannon_cart(deck_image):
    references = [
        "cannon_cart_1.png",
        "cannon_cart_2.png",
        "cannon_cart_3.png",
        "cannon_cart_4.png",
        "cannon_cart_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found cannon cart in deck")
            return location
    return None


def check_deck_for_hog(deck_image):
    references = [
        "hog_1.png",
        "hog_2.png",
        "hog_3.png",
        "hog_4.png",
        "hog_5.png",
        "hog_6.png",
        "hog_7.png",
        "hog_8.png",
        "hog_9.png",
        "hog_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found hog in deck")
            return location
    return None


def check_deck_for_fire_spirit(deck_image):
    references = [
        "fire_spirit_1.png",
        "fire_spirit_2.png",
        "fire_spirit_3.png",
        "fire_spirit_4.png",
        "fire_spirit_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found fire spirit in deck")
            return location
    return None


def check_deck_for_ice_spirit(deck_image):
    references = [
        "ice_spirit_1.png",
        "ice_spirit_2.png",
        "ice_spirit_3.png",
        "ice_spirit_4.png",
        "ice_spirit_5.png",
        "ice_spirit_6.png",
        "ice_spirit_7.png",
        "ice_spirit_8.png",
        "ice_spirit_9.png",
        "ice_spirit_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ice spirit in deck")
            return location
    return None


def check_deck_for_bandit(deck_image):
    references = [
        "bandit_1.png",
        "bandit_2.png",
        "bandit_3.png",
        "bandit_4.png",
        "bandit_5.png",
        "bandit_6.png",
        "bandit_7.png",
        "bandit_8.png",
        "bandit_9.png",
        "bandit_10.png",
        "bandit_11.png",
        "bandit_12.png",
        "bandit_13.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bandit in deck")
            return location
    return None


def check_deck_for_musketeer(deck_image):
    references = [
        "musketeer_1.png",
        "musketeer_2.png",
        "musketeer_3.png",
        "musketeer_4.png",
        "musketeer_5.png",
        "musketeer_5.png",
        "musketeer_2.png",
        "musketeer_3.png",
        "musketeer_4.png",
        "musketeer_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found musketeer in deck")
            return location
    return None


def check_deck_for_furnace(deck_image):
    references = [
        "furnace_1.png",
        "furnace_2.png",
        "furnace_3.png",
        "furnace_4.png",
        "furnace_5.png",
        "furnace_6.png",
        "furnace_7.png",
        "furnace_8.png",
        "furnace_9.png",
        "furnace_10.png",
        "furnace_11.png",
        "furnace_12.png",
        "furnace_13.png",
        "furnace_14.png",
        "furnace_15.png",
        "furnace_16.png",
        "furnace_17.png",
        "furnace_18.png",
        "furnace_19.png",
        "furnace_20.png",
        "furnace_21.png",
        "furnace_22.png",
        "furnace_23.png",
        "furnace_24.png",
        "furnace_25.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found furnace in deck")
            return location
    return None


def check_deck_for_snowball(deck_image):
    references = [
        "snowball_1.png",
        "snowball_2.png",
        "snowball_3.png",
        "snowball_4.png",
        "snowball_5.png",
        "snowball_6.png",
        "snowball_7.png",
        "snowball_8.png",
        "snowball_9.png",
        "snowball_10.png",
        "snowball_11.png",
        "snowball_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found snowball in deck")
            return location
    return None


def check_deck_for_royal_recruits(deck_image):
    references = [
        "royal_recruits_1.png",
        "royal_recruits_2.png",
        "royal_recruits_3.png",
        "royal_recruits_4.png",
        "royal_recruits_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal recruits in deck")
            return location
    return None


def check_deck_for_dark_knight(deck_image):
    references = [
        "dark_knight_1.png",
        "dark_knight_2.png",
        "dark_knight_3.png",
        "dark_knight_4.png",
        "dark_knight_5.png",
        "dark_knight_6.png",
        "dark_knight_7.png",
        "dark_knight_8.png",
        "dark_knight_9.png",
        "dark_knight_10.png",
        "dark_knight_11.png",
        "dark_knight_12.png",
        "dark_knight_13.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found dark knight in deck")
            return location
    return None


def check_deck_for_valk(deck_image):
    references = [
        "valk_1.png",
        "valk_2.png",
        "valk_3.png",
        "valk_4.png",
        "valk_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found valk in deck")
            return location
    return None


def check_deck_for_goblin_gang(deck_image):
    references = [
        "goblin_gang_1.png",
        "goblin_gang_2.png",
        "goblin_gang_3.png",
        "goblin_gang_4.png",
        "goblin_gang_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin gang in deck")
            return location
    return None


def check_deck_for_tesla(deck_image):
    references = [
        "tesla_1.png",
        "tesla_2.png",
        "tesla_3.png",
        "tesla_4.png",
        "tesla_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found tesla in deck")
            return location
    return None


def check_deck_for_royal_ghost(deck_image):
    references = [
        "royal_ghost_1.png",
        "royal_ghost_2.png",
        "royal_ghost_3.png",
        "royal_ghost_4.png",
        "royal_ghost_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal ghost in deck")
            return location
    return None


def check_deck_for_bomber(deck_image):
    references = [
        "bomber_1.png",
        "bomber_2.png",
        "bomber_3.png",
        "bomber_4.png",
        "bomber_5.png",
        "bomber_6.png",
        "bomber_7.png",
        "bomber_8.png",
        "bomber_9.png",
        "bomber_10.png",
        "bomber_11.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bomber in deck")
            return location
    return None


def check_deck_for_ram_rider(deck_image):
    references = [
        "ram_rider_1.png",
        "ram_rider_2.png",
        "ram_rider_3.png",
        "ram_rider_4.png",
        "ram_rider_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ram rider in deck")
            return location
    return None


def check_deck_for_mirror(deck_image):
    references = [
        "mirror_1.png",
        "mirror_2.png",
        "mirror_3.png",
        "mirror_4.png",
        "mirror_5.png",
        "mirror_6.png",
        "mirror_7.png",
        "mirror_8.png",
        "mirror_9.png",
        "mirror_10.png",
        "mirror_11.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mirror in deck")
            return location
    return None


def check_deck_for_poison(deck_image):
    references = [
        "poison_1.png",
        "poison_2.png",
        "poison_3.png",
        "poison_4.png",
        "poison_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found poison in deck")
            return location
    return None


def check_deck_for_royal_delivery(deck_image):
    references = [
        "royal_delivery_1.png",
        "royal_delivery_2.png",
        "royal_delivery_3.png",
        "royal_delivery_4.png",
        "royal_delivery_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal delivery in deck")
            return location
    return None


def check_deck_for_heal_spirit(deck_image):
    references = [
        "heal_spirit_1.png",
        "heal_spirit_2.png",
        "heal_spirit_3.png",
        "heal_spirit_4.png",
        "heal_spirit_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found heal spirit in deck")
            return location
    return None


def check_deck_for_ice_golem(deck_image):
    references = [
        "ice_golem_1.png",
        "ice_golem_2.png",
        "ice_golem_3.png",
        "ice_golem_4.png",
        "ice_golem_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ice golem in deck")
            return location
    return None


def check_deck_for_wall_breaker(deck_image):
    references = [
        "wall_breaker_1.png",
        "wall_breaker_2.png",
        "wall_breaker_3.png",
        "wall_breaker_4.png",
        "wall_breaker_5.png",
        "wall_breaker_6.png",
        "wall_breaker_7.png",
        "wall_breaker_8.png",
        "wall_breaker_9.png",
        "wall_breaker_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found wall breaker in deck")
            return location
    return None


def check_deck_for_guards(deck_image):
    references = [
        "guards_1.png",
        "guards_2.png",
        "guards_3.png",
        "guards_4.png",
        "guards_5.png",
        "guards_6.png",
        "guards_7.png",
        "guards_8.png",
        "guards_9.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found guards in deck")
            return location
    return None


def check_deck_for_princess(deck_image):
    references = [
        "princess_1.png",
        "princess_2.png",
        "princess_3.png",
        "princess_4.png",
        "princess_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found princess in deck")
            return location
    return None


def check_deck_for_night_witch(deck_image):
    references = [
        "night_witch_1.png",
        "night_witch_2.png",
        "night_witch_4.png",
        "night_witch_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found night witch in deck")
            return location
    return None


def check_deck_for_e_spirit(deck_image):
    references = [
        "e_spirit_1.png",
        "e_spirit_2.png",
        "e_spirit_3.png",
        "e_spirit_4.png",
        "e_spirit_5.png",
        "e_spirit_6.png",
        "e_spirit_7.png",
        "e_spirit_8.png",
        "e_spirit_9.png",
        "e_spirit_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found e spirit in deck")
            return location
    return None


def check_deck_for_ice_wizard(deck_image):
    references = [
        "ice_wizard_1.png",
        "ice_wizard_2.png",
        "ice_wizard_3.png",
        "ice_wizard_4.png",
        "ice_wizard_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ice wizard in deck")
            return location
    return None


def check_deck_for_minions(deck_image):
    references = [
        "minions_1.png",
        "minions_2.png",
        "minions_3.png",
        "minions_4.png",
        "minions_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found minions in deck")
            return location
    return None


def check_deck_for_goblins(deck_image):
    references = [
        "goblins_1.png",
        "goblins_2.png",
        "goblins_3.png",
        "goblins_4.png",
        "goblins_5.png",
        "goblins_6.png",
        "goblins_7.png",
        "goblins_8.png",
        "goblins_9.png",
        "goblins_10.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblins in deck")
            return location
    return None


def check_deck_for_mega_minion(deck_image):
    references = [
        "mega_minion_1.png",
        "mega_minion_2.png",
        "mega_minion_3.png",
        "mega_minion_4.png",
        "mega_minion_5.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mega minion in deck")
            return location
    return None


def check_deck_for_three_musketeers(deck_image):
    references = [
        "three_musketeers_1.png",
        "three_musketeers_2.png",
        "three_musketeers_3.png",
        "three_musketeers_4.png",
        "three_musketeers_5.png",
        "three_musketeers_6.png",
        "three_musketeers_7.png",
        "three_musketeers_8.png",
        "three_musketeers_9.png",
        "three_musketeers_10.png",
        "three_musketeers_11.png",
        "three_musketeers_12.png",
    ]
    locations = find_references(
        screenshot=deck_image,
        folder='deck_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found three musketeers in deck")
            return location
    return None

# endregion


def find_all_cards(deck_screenshot, comparisons):
    if check_deck_for_witch(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'witch')

    if check_deck_for_golden_knight(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'golden_knight')

    if check_deck_for_royal_hogs(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'royal_hogs')

    if check_deck_for_royal_giant(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'royal_giant')

    if check_deck_for_cannon(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'cannon')

    if check_deck_for_fireball(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'fireball')

    if check_deck_for_earthquake(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'earthquake')

    if check_deck_for_log(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'log')

    if check_deck_for_baby_dragon(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'baby_dragon')

    if check_deck_for_pekka(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'pekka')

    if check_deck_for_mother_witch(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mother_witch')

    if check_deck_for_goblin_hut(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'goblin_hut')

    if check_deck_for_mighty_miner(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mighty_miner')

    if check_deck_for_fisherman(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'fisherman')

    if check_deck_for_inferno_tower(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'inferno_tower')

    if check_deck_for_archers(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'archers')

    if check_deck_for_bats(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'bats')

    if check_deck_for_tombstone(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'tombstone')

    if check_deck_for_e_giant(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'e_giant')

    if check_deck_for_rocket(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'rocket')

    if check_deck_for_graveyard(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'graveyard')

    if check_deck_for_healer(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'healer')

    if check_deck_for_barb_barrel(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'barb_barrel')

    if check_deck_for_archer_queen(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'archer_queen')

    if check_deck_for_e_wiz(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'e_wiz')

    if check_deck_for_battle_ram(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'battle_ram')

    if check_deck_for_spear_goblins(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'spear_goblins')

    if check_deck_for_arrows(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'arrows')

    if check_deck_for_skeleton_army(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'skeleton_army')

    if check_deck_for_wizard(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'wizard')

    if check_deck_for_skeleton_dragons(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'skeleton_dragons')

    if check_deck_for_prince(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'prince')

    if check_deck_for_goblin_giant(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'goblin_giant')

    if check_deck_for_zappies(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'zappies')

    if check_deck_for_lavahound(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'lavahound')

    if check_deck_for_lightning(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'lightning')

    if check_deck_for_executioner(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'executioner')

    if check_deck_for_goblin_drill(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'goblin_drill')

    if check_deck_for_rage(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'rage')

    if check_deck_for_clone(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'clone')

    if check_deck_for_goblin_barrel(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'goblin_barrel')

    if check_deck_for_minion_hoard(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'minion_hoard')

    if check_deck_for_barbs(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'barbs')

    if check_deck_for_tornado(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'tornado')

    if check_deck_for_skeleton_barrel(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'skeleton_barrel')

    if check_deck_for_miner(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'miner')

    if check_deck_for_skeletons(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'skeletons')

    if check_deck_for_elite_barbs(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'elite_barbs')

    if check_deck_for_flying_machine(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'flying_machine')

    if check_deck_for_e_dragon(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'e_dragon')

    if check_deck_for_xbow(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'xbow')

    if check_deck_for_elixer_golem(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'elixer_golem')

    if check_deck_for_rascals(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'rascals')

    if check_deck_for_skeleton_king(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'skeleton_king')

    if check_deck_for_balloon(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'balloon')

    if check_deck_for_sparky(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'sparky')

    if check_deck_for_golem(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'golem')

    if check_deck_for_barb_hut(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'barb_hut')

    if check_deck_for_bomb_tower(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'bomb_tower')

    if check_deck_for_mortar(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mortar')

    if check_deck_for_inferno_dragon(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'inferno_dragon')

    if check_deck_for_hunter(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'hunter')

    if check_deck_for_giant(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'giant')

    if check_deck_for_freeze(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'freeze')

    if check_deck_for_lumberjack(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'lumberjack')

    if check_deck_for_bowler(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'bowler')

    if check_deck_for_dart_goblin(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'dart_goblin')

    if check_deck_for_mini_pekka(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mini_pekka')

    if check_deck_for_mega_knight(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mega_knight')

    if check_deck_for_elixer_pump(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'elixer_pump')

    if check_deck_for_giant_skeleton(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'giant_skeleton')

    if check_deck_for_magic_archer(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'magic_archer')

    if check_deck_for_firecracker(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'firecracker')

    if check_deck_for_knight(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'knight')

    if check_deck_for_cannon_cart(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'cannon_cart')

    if check_deck_for_hog(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'hog')

    if check_deck_for_fire_spirit(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'fire_spirit')

    if check_deck_for_ice_spirit(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'ice_spirit')

    if check_deck_for_bandit(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'bandit')

    if check_deck_for_musketeer(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'musketeer')

    if check_deck_for_furnace(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'furnace')

    if check_deck_for_snowball(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'snowball')

    if check_deck_for_royal_recruits(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'royal_recruits')

    if check_deck_for_dark_knight(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'dark_knight')

    if check_deck_for_valk(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'valk')

    if check_deck_for_goblin_gang(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'goblin_gang')

    if check_deck_for_tesla(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'tesla')

    if check_deck_for_royal_ghost(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'royal_ghost')

    if check_deck_for_bomber(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'bomber')

    if check_deck_for_ram_rider(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'ram_rider')

    if check_deck_for_mirror(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mirror')

    if check_deck_for_poison(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'poison')

    if check_deck_for_royal_delivery(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'royal_delivery')

    if check_deck_for_heal_spirit(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'heal_spirit')

    if check_deck_for_ice_golem(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'ice_golem')

    if check_deck_for_wall_breaker(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'wall_breaker')

    if check_deck_for_guards(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'guards')

    if check_deck_for_princess(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'princess')

    if check_deck_for_night_witch(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'night_witch')

    if check_deck_for_e_spirit(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'e_spirit')

    if check_deck_for_ice_wizard(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'ice_wizard')

    if check_deck_for_minions(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'minions')

    if check_deck_for_goblins(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'goblins')

    if check_deck_for_mega_minion(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'mega_minion')

    if check_deck_for_three_musketeers(deck_screenshot) is not None:
        comparisons = add_card_to_deck(comparisons, 'three_musketeers')

def check_if_card_in_deck(deck_list, card):
    return card in deck_list
# region hand card checks


def check_hand_for_ice_spirit(hand_screenshot):
    references = [
        "ice_spirit.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ice spirit in hand")
            return location
    return None


def check_hand_for_fire_spirit(hand_screenshot):
    references = [
        "fire_spirit.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found fire spirit in hand")
            return location
    return None


def check_hand_for_e_spirit(hand_screenshot):
    references = [
        "e_spirit.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found e spirit in hand")
            return location
    return None


def check_hand_for_mirror(hand_screenshot):
    references = [
        "mirror.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mirror in hand")
            return location
    return None


def check_hand_for_heal_spirit(hand_screenshot):
    references = [
        "heal_spirit.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found heal spirit in hand")
            return location
    return None


def check_hand_for_goblins(hand_screenshot):
    references = [
        "goblins.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblins in hand")
            return location
    return None


def check_hand_for_bomber(hand_screenshot):
    references = [
        "bomber.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bomber in hand")
            return location
    return None


def check_hand_for_spear_goblins(hand_screenshot):
    references = [
        "spear_goblins.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found spear goblins in hand")
            return location
    return None


def check_hand_for_ice_golem(hand_screenshot):
    references = [
        "ice_golem.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ice golem in hand")
            return location
    return None


def check_hand_for_bats(hand_screenshot):
    references = [
        "bats.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bats in hand")
            return location
    return None


def check_hand_for_wall_breaker(hand_screenshot):
    references = [
        "wall_breaker.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found wall breaker in hand")
            return location
    return None


def check_hand_for_rage(hand_screenshot):
    references = [
        "rage.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found rage in hand")
            return location
    return None


def check_hand_for_zap(hand_screenshot):
    references = [
        "zap.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found zap in hand")
            return location
    return None


def check_hand_for_log(hand_screenshot):
    references = [
        "log.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found log in hand")
            return location
    return None


def check_hand_for_barb_barrel(hand_screenshot):
    references = [
        "barb_barrel.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found barb barrel in hand")
            return location
    return None


def check_hand_for_snowball(hand_screenshot):
    references = [
        "snowball.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found snowball in hand")
            return location
    return None


def check_hand_for_knight(hand_screenshot):
    references = [
        "knight.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found knight in hand")
            return location
    return None


def check_hand_for_archers(hand_screenshot):
    references = [
        "archers.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found archers in hand")
            return location
    return None


def check_hand_for_minions(hand_screenshot):
    references = [
        "minions.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found minions in hand")
            return location
    return None


def check_hand_for_skeleton_army(hand_screenshot):
    references = [
        "skeleton_army.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton army in hand")
            return location
    return None


def check_hand_for_ice_wizard(hand_screenshot):
    references = [
        "ice_wizard.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ice wizard in hand")
            return location
    return None


def check_hand_for_guards(hand_screenshot):
    references = [
        "guards.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found guards in hand")
            return location
    return None


def check_hand_for_princess(hand_screenshot):
    references = [
        "princess.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found princess in hand")
            return location
    return None


def check_hand_for_miner(hand_screenshot):
    references = [
        "miner.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found miner in hand")
            return location
    return None


def check_hand_for_mega_minion(hand_screenshot):
    references = [
        "mega_minion.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mega minion in hand")
            return location
    return None


def check_hand_for_dart_goblin(hand_screenshot):
    references = [
        "dart_goblin.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found dart goblin in hand")
            return location
    return None


def check_hand_for_goblin_gang(hand_screenshot):
    references = [
        "goblin_gang.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin gang in hand")
            return location
    return None


def check_hand_for_bandit(hand_screenshot):
    references = [
        "bandit.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bandit in hand")
            return location
    return None


def check_hand_for_royal_ghost(hand_screenshot):
    references = [
        "royal_ghost.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal ghost in hand")
            return location
    return None


def check_hand_for_skeleton_barrel(hand_screenshot):
    references = [
        "skeleton_barrel.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton barrel in hand")
            return location
    return None


def check_hand_for_fisherman(hand_screenshot):
    references = [
        "fisherman.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found fisherman in hand")
            return location
    return None


def check_hand_for_firecracker(hand_screenshot):
    references = [
        "firecracker.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found firecracker in hand")
            return location
    return None


def check_hand_for_elixer_golem(hand_screenshot):
    references = [
        "elixer_golem.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found elixer golem in hand")
            return location
    return None


def check_hand_for_cannon(hand_screenshot):
    references = [
        "cannon.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found cannon in hand")
            return location
    return None


def check_hand_for_tombstone(hand_screenshot):
    references = [
        "tombstone.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found tombstone in hand")
            return location
    return None


def check_hand_for_arrows(hand_screenshot):
    references = [
        "arrows.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found arrows in hand")
            return location
    return None


def check_hand_for_goblin_barrel(hand_screenshot):
    references = [
        "goblin_barrel.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin barrel in hand")
            return location
    return None


def check_hand_for_tornado(hand_screenshot):
    references = [
        "tornado.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found tornado in hand")
            return location
    return None


def check_hand_for_clone(hand_screenshot):
    references = [
        "clone.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found clone in hand")
            return location
    return None


def check_hand_for_earthquake(hand_screenshot):
    references = [
        "earthquake.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found earthquake in hand")
            return location
    return None


def check_hand_for_royal_delivery(hand_screenshot):
    references = [
        "royal_delivery.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal delivery in hand")
            return location
    return None


def check_hand_for_valk(hand_screenshot):
    references = [
        "valk.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found valk in hand")
            return location
    return None


def check_hand_for_musketeer(hand_screenshot):
    references = [
        "musketeer.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found musketeer in hand")
            return location
    return None


def check_hand_for_baby_dragon(hand_screenshot):
    references = [
        "baby_dragon.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found baby dragon in hand")
            return location
    return None


def check_hand_for_mini_pekka(hand_screenshot):
    references = [
        "mini_pekka.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mini pekka in hand")
            return location
    return None


def check_hand_for_hog(hand_screenshot):
    references = [
        "hog.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found hog in hand")
            return location
    return None


def check_hand_for_dark_knight(hand_screenshot):
    references = [
        "dark_knight.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found dark knight in hand")
            return location
    return None


def check_hand_for_lumberjack(hand_screenshot):
    references = [
        "lumberjack.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found lumberjack in hand")
            return location
    return None


def check_hand_for_battle_ram(hand_screenshot):
    references = [
        "battle_ram.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found battle ram in hand")
            return location
    return None


def check_hand_for_inferno_dragon(hand_screenshot):
    references = [
        "inferno_dragon.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found inferno dragon in hand")
            return location
    return None


def check_hand_for_e_wiz(hand_screenshot):
    references = [
        "e_wiz.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found e wiz in hand")
            return location
    return None


def check_hand_for_hunter(hand_screenshot):
    references = [
        "hunter.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found hunter in hand")
            return location
    return None


def check_hand_for_zappies(hand_screenshot):
    references = [
        "zappies.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found zappies in hand")
            return location
    return None


def check_hand_for_magic_archer(hand_screenshot):
    references = [
        "magic_archer.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found magic archer in hand")
            return location
    return None


def check_hand_for_mighty_miner(hand_screenshot):
    references = [
        "mighty_miner.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mighty miner in hand")
            return location
    return None


def check_hand_for_skeleton_king(hand_screenshot):
    references = [
        "skeleton_king.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found skeleton king in hand")
            return location
    return None


def check_hand_for_golden_knight(hand_screenshot):
    references = [
        "golden_knight.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found golden knight in hand")
            return location
    return None


def check_hand_for_mortar(hand_screenshot):
    references = [
        "mortar.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mortar in hand")
            return location
    return None


def check_hand_for_bomb_tower(hand_screenshot):
    references = [
        "bomb_tower.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bomb tower in hand")
            return location
    return None


def check_hand_for_tesla(hand_screenshot):
    references = [
        "tesla.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found tesla in hand")
            return location
    return None


def check_hand_for_furnace(hand_screenshot):
    references = [
        "furnace.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found furnace in hand")
            return location
    return None


def check_hand_for_goblin_cage(hand_screenshot):
    references = [
        "goblin_cage.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin cage in hand")
            return location
    return None


def check_hand_for_goblin_drill(hand_screenshot):
    references = [
        "goblin_drill.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin drill in hand")
            return location
    return None


def check_hand_for_fireball(hand_screenshot):
    references = [
        "fireball.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found fireball in hand")
            return location
    return None


def check_hand_for_freeze(hand_screenshot):
    references = [
        "freeze.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found freeze in hand")
            return location
    return None


def check_hand_for_poison(hand_screenshot):
    references = [
        "poison.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found poison in hand")
            return location
    return None


def check_hand_for_giant(hand_screenshot):
    references = [
        "giant.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found giant in hand")
            return location
    return None


def check_hand_for_balloon(hand_screenshot):
    references = [
        "balloon.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found balloon in hand")
            return location
    return None


def check_hand_for_barbs(hand_screenshot):
    references = [
        "barbs.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found barbs in hand")
            return location
    return None


def check_hand_for_bowler(hand_screenshot):
    references = [
        "bowler.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found bowler in hand")
            return location
    return None


def check_hand_for_executioner(hand_screenshot):
    references = [
        "executioner.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found executioner in hand")
            return location
    return None


def check_hand_for_ram_rider(hand_screenshot):
    references = [
        "ram_rider.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found ram rider in hand")
            return location
    return None


def check_hand_for_rascals(hand_screenshot):
    references = [
        "rascals.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found rascals in hand")
            return location
    return None


def check_hand_for_cannon_cart(hand_screenshot):
    references = [
        "cannon_cart.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found cannon cart in hand")
            return location
    return None


def check_hand_for_royal_hogs(hand_screenshot):
    references = [
        "royal_hogs.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal hogs in hand")
            return location
    return None


def check_hand_for_archer_queen(hand_screenshot):
    references = [
        "archer_queen.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found archer queen in hand")
            return location
    return None


def check_hand_for_goblin_hut(hand_screenshot):
    references = [
        "goblin_hut.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin hut in hand")
            return location
    return None


def check_hand_for_inferno_tower(hand_screenshot):
    references = [
        "inferno_tower.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found inferno tower in hand")
            return location
    return None


def check_hand_for_graveyard(hand_screenshot):
    references = [
        "graveyard.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found graveyard in hand")
            return location
    return None


def check_hand_for_giant_skeleton(hand_screenshot):
    references = [
        "giant_skeleton.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found giant skeleton in hand")
            return location
    return None


def check_hand_for_royal_giant(hand_screenshot):
    references = [
        "royal_giant.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal giant in hand")
            return location
    return None


def check_hand_for_sparky(hand_screenshot):
    references = [
        "sparky.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found sparky in hand")
            return location
    return None


def check_hand_for_elite_barbs(hand_screenshot):
    references = [
        "elite_barbs.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found elite barbs in hand")
            return location
    return None


def check_hand_for_goblin_giant(hand_screenshot):
    references = [
        "goblin_giant.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found goblin giant in hand")
            return location
    return None


def check_hand_for_elixer_pump(hand_screenshot):
    references = [
        "elixer_pump.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found elixer pump in hand")
            return location
    return None


def check_hand_for_xbow(hand_screenshot):
    references = [
        "xbow.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found xbow in hand")
            return location
    return None


def check_hand_for_lightning(hand_screenshot):
    references = [
        "lightning.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found lightning in hand")
            return location
    return None


def check_hand_for_pekka(hand_screenshot):
    references = [
        "pekka.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found pekka in hand")
            return location
    return None


def check_hand_for_lavahound(hand_screenshot):
    references = [
        "lavahound.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found lavahound in hand")
            return location
    return None


def check_hand_for_royal_guards(hand_screenshot):
    references = [
        "royal_guards.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found royal guards in hand")
            return location
    return None


def check_hand_for_mega_knight(hand_screenshot):
    references = [
        "mega_knight.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found mega knight in hand")
            return location
    return None


def check_hand_for_barb_hut(hand_screenshot):
    references = [
        "barb_hut.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found barb hut in hand")
            return location
    return None


def check_hand_for_golem(hand_screenshot):
    references = [
        "golem.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found golem in hand")
            return location
    return None


def check_hand_for_three_musketeers(hand_screenshot):
    references = [
        "three_musketeers.png",
    ]
    locations = find_references(
        screenshot=hand_screenshot,
        folder='hand_cards',
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            print("Found three musketeers in hand")
            return location
    return None


# endregion

def check_for_card_in_hand(card):
    hand_screenshot = pyautogui.screenshot()
    if card in ['ice_spirit']:
        location = check_hand_for_ice_spirit(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['fire_spirit']:
        location = check_hand_for_fire_spirit(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['e_spirit']:
        location = check_hand_for_e_spirit(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['mirror']:
        location = check_hand_for_mirror(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['heal_spirit']:
        location = check_hand_for_heal_spirit(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblins']:
        location = check_hand_for_goblins(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['bomber']:
        location = check_hand_for_bomber(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['spear_goblins']:
        location = check_hand_for_spear_goblins(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['ice_golem']:
        location = check_hand_for_ice_golem(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['bats']:
        location = check_hand_for_bats(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['wall_breaker']:
        location = check_hand_for_wall_breaker(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['rage']:
        location = check_hand_for_rage(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['zap']:
        location = check_hand_for_zap(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['log']:
        location = check_hand_for_log(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['barb_barrel']:
        location = check_hand_for_barb_barrel(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['snowball']:
        location = check_hand_for_snowball(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['knight']:
        location = check_hand_for_knight(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['archers']:
        location = check_hand_for_archers(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['minions']:
        location = check_hand_for_minions(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['skeleton_army']:
        location = check_hand_for_skeleton_army(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['ice_wizard']:
        location = check_hand_for_ice_wizard(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['guards']:
        location = check_hand_for_guards(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['princess']:
        location = check_hand_for_princess(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['miner']:
        location = check_hand_for_miner(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['mega_minion']:
        location = check_hand_for_mega_minion(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['dart_goblin']:
        location = check_hand_for_dart_goblin(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblin_gang']:
        location = check_hand_for_goblin_gang(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['bandit']:
        location = check_hand_for_bandit(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['royal_ghost']:
        location = check_hand_for_royal_ghost(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['skeleton_barrel']:
        location = check_hand_for_skeleton_barrel(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['fisherman']:
        location = check_hand_for_fisherman(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['firecracker']:
        location = check_hand_for_firecracker(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['elixer_golem']:
        location = check_hand_for_elixer_golem(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['cannon']:
        location = check_hand_for_cannon(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['tombstone']:
        location = check_hand_for_tombstone(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['arrows']:
        location = check_hand_for_arrows(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblin_barrel']:
        location = check_hand_for_goblin_barrel(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['tornado']:
        location = check_hand_for_tornado(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['clone']:
        location = check_hand_for_clone(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['earthquake']:
        location = check_hand_for_earthquake(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['royal_delivery']:
        location = check_hand_for_royal_delivery(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['valk']:
        location = check_hand_for_valk(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['musketeer']:
        location = check_hand_for_musketeer(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['baby_dragon']:
        location = check_hand_for_baby_dragon(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['mini_pekka']:
        location = check_hand_for_mini_pekka(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['hog']:
        location = check_hand_for_hog(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['dark_knight']:
        location = check_hand_for_dark_knight(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['lumberjack']:
        location = check_hand_for_lumberjack(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['battle_ram']:
        location = check_hand_for_battle_ram(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['inferno_dragon']:
        location = check_hand_for_inferno_dragon(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['e_wiz']:
        location = check_hand_for_e_wiz(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['hunter']:
        location = check_hand_for_hunter(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['zappies']:
        location = check_hand_for_zappies(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['magic_archer']:
        location = check_hand_for_magic_archer(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['mighty_miner']:
        location = check_hand_for_mighty_miner(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['skeleton_king']:
        location = check_hand_for_skeleton_king(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['golden_knight']:
        location = check_hand_for_golden_knight(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['mortar']:
        location = check_hand_for_mortar(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['bomb_tower']:
        location = check_hand_for_bomb_tower(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['tesla']:
        location = check_hand_for_tesla(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['furnace']:
        location = check_hand_for_furnace(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblin_cage']:
        location = check_hand_for_goblin_cage(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblin_drill']:
        location = check_hand_for_goblin_drill(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['fireball']:
        location = check_hand_for_fireball(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['freeze']:
        location = check_hand_for_freeze(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['poison']:
        location = check_hand_for_poison(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['giant']:
        location = check_hand_for_giant(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['balloon']:
        location = check_hand_for_balloon(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['barbs']:
        location = check_hand_for_barbs(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['minions']:
        location = check_hand_for_minions(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['bowler']:
        location = check_hand_for_bowler(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['executioner']:
        location = check_hand_for_executioner(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['ram_rider']:
        location = check_hand_for_ram_rider(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['rascals']:
        location = check_hand_for_rascals(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['cannon_cart']:
        location = check_hand_for_cannon_cart(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['royal_hogs']:
        location = check_hand_for_royal_hogs(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['archer_queen']:
        location = check_hand_for_archer_queen(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblin_hut']:
        location = check_hand_for_goblin_hut(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['inferno_tower']:
        location = check_hand_for_inferno_tower(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['graveyard']:
        location = check_hand_for_graveyard(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['giant_skeleton']:
        location = check_hand_for_giant_skeleton(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['royal_giant']:
        location = check_hand_for_royal_giant(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['sparky']:
        location = check_hand_for_sparky(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['elite_barbs']:
        location = check_hand_for_elite_barbs(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['goblin_giant']:
        location = check_hand_for_goblin_giant(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['elixer_pump']:
        location = check_hand_for_elixer_pump(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['xbow']:
        location = check_hand_for_xbow(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['lightning']:
        location = check_hand_for_lightning(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['pekka']:
        location = check_hand_for_pekka(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['lavahound']:
        location = check_hand_for_lavahound(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['royal_guards']:
        location = check_hand_for_royal_guards(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['mega_knight']:
        location = check_hand_for_mega_knight(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['barb_hut']:
        location = check_hand_for_barb_hut(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['golem']:
        location = check_hand_for_golem(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]

    if card in ['three_musketeers']:
        location = check_hand_for_three_musketeers(hand_screenshot)
        if location is not None:
            return [location[1], location[0]]
