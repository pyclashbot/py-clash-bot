from image_rec import compare_images
from PIL import Image
from os.path import join


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


def find_all_cards(deck_image, comparisons):
    # three_musketeers
    comparisons = find_three_musketeers(deck_image, comparisons)
    # mega_minion
    comparisons = find_mega_minion(deck_image, comparisons)
    # goblins
    comparisons = find_goblins(deck_image, comparisons)
    # minions
    comparisons = find_minions(deck_image, comparisons)
    # ice_wizard
    comparisons = find_ice_wizard(deck_image, comparisons)
    # e_spirit
    comparisons = find_e_spirit(deck_image, comparisons)
    # night_witch
    comparisons = find_night_witch(deck_image, comparisons)
    # princess
    comparisons = find_princess(deck_image, comparisons)
    # guards
    comparisons = find_guards(deck_image, comparisons)
    # wall_breaker
    comparisons = find_wall_breaker(deck_image, comparisons)
    # ice_golem
    comparisons = find_ice_golem(deck_image, comparisons)
    # heal_spirit
    comparisons = find_heal_spirit(deck_image, comparisons)
    # royal_delivery
    comparisons = find_royal_delivery(deck_image, comparisons)
    # poison
    comparisons = find_poison(deck_image, comparisons)
    # mirror
    comparisons = find_mirror(deck_image, comparisons)
    # ram_rider
    comparisons = find_ram_rider(deck_image, comparisons)
    # bomber
    comparisons = find_bomber(deck_image, comparisons)
    # royal_ghost
    comparisons = find_royal_ghost(deck_image, comparisons)
    # tesla
    comparisons = find_tesla(deck_image, comparisons)
    # goblin_gang
    comparisons = find_goblin_gang(deck_image, comparisons)
    # valk
    comparisons = find_valk(deck_image, comparisons)
    # dark_knight
    comparisons = find_dark_knight(deck_image, comparisons)
    # royal_recruits
    comparisons = find_royal_recruits(deck_image, comparisons)
    # snowball
    comparisons = find_snowball(deck_image, comparisons)
    # zap
    comparisons = find_zap(deck_image, comparisons)
    # witch
    comparisons = find_witch(deck_image, comparisons)
    # furnace
    comparisons = find_furnace(deck_image, comparisons)
    # musketeer
    comparisons = find_musketeer(deck_image, comparisons)
    # bandit
    comparisons = find_bandit(deck_image, comparisons)
    # ice_spirit
    comparisons = find_ice_spirit(deck_image, comparisons)
    # fire_spirit
    comparisons = find_fire_spirit(deck_image, comparisons)
    # hog
    comparisons = find_hog(deck_image, comparisons)
    # cannon_cart
    comparisons = find_cannon_cart(deck_image, comparisons)
    # knight
    comparisons = find_knight(deck_image, comparisons)
    # firecracker
    comparisons = find_firecracker(deck_image, comparisons)
    # magic_archer
    comparisons = find_magic_archer(deck_image, comparisons)
    # giant_skeleton
    comparisons = find_giant_skeleton(deck_image, comparisons)
    # elixer_pump
    comparisons = find_elixer_pump(deck_image, comparisons)
    # mega_knight
    comparisons = find_mega_knight(deck_image, comparisons)
    # mini_pekka
    comparisons = find_mini_pekka(deck_image, comparisons)
    # dart_goblin
    comparisons = find_dart_goblin(deck_image, comparisons)
    # bowler
    comparisons = find_bowler(deck_image, comparisons)
    # lumberjack
    comparisons = find_lumberjack(deck_image, comparisons)
    # freeze
    comparisons = find_freeze(deck_image, comparisons)
    # giant
    comparisons = find_giant(deck_image, comparisons)
    # hunter
    comparisons = find_hunter(deck_image, comparisons)
    # inferno_dragon
    comparisons = find_inferno_dragon(deck_image, comparisons)
    # mortar
    comparisons = find_mortar(deck_image, comparisons)
    # bomb_tower
    comparisons = find_bomb_tower(deck_image, comparisons)
    # barb_hut
    comparisons = find_barb_hut(deck_image, comparisons)
    # golem
    comparisons = find_golem(deck_image, comparisons)
    # sparky
    comparisons = find_sparky(deck_image, comparisons)
    # balloon
    comparisons = find_balloon(deck_image, comparisons)
    # skeleton_king
    comparisons = find_skeleton_king(deck_image, comparisons)
    # rascals
    comparisons = find_rascals(deck_image, comparisons)
    # elixer_golem
    comparisons = find_elixer_golem(deck_image, comparisons)
    # xbow
    comparisons = find_xbow(deck_image, comparisons)
    # e_dragon
    comparisons = find_e_dragon(deck_image, comparisons)
    # flying_machine
    comparisons = find_flying_machine(deck_image, comparisons)
    # elite_barbs
    comparisons = find_elite_barbs(deck_image, comparisons)
    # skeletons
    comparisons = find_skeletons(deck_image, comparisons)
    # miner
    comparisons = find_miner(deck_image, comparisons)
    # skeleton_barrel
    comparisons = find_skeleton_barrel(deck_image, comparisons)
    # tornado
    comparisons = find_tornado(deck_image, comparisons)
    # barbs
    comparisons = find_barbs(deck_image, comparisons)
    # minion_hoard
    comparisons = find_minion_hoard(deck_image, comparisons)
    # goblin_barrel
    comparisons = find_goblin_barrel(deck_image, comparisons)
    # clone
    comparisons = find_clone(deck_image, comparisons)
    # rage
    comparisons = find_rage(deck_image, comparisons)
    # goblin_drill
    comparisons = find_goblin_drill(deck_image, comparisons)
    # executioner
    comparisons = find_executioner(deck_image, comparisons)
    # lightning
    comparisons = find_lightning(deck_image, comparisons)
    # lavahound
    comparisons = find_lavahound(deck_image, comparisons)
    # zappies
    comparisons = find_zappies(deck_image, comparisons)
    # goblin_giant
    comparisons = find_goblin_giant(deck_image, comparisons)
    # prince
    comparisons = find_prince(deck_image, comparisons)
    # skeleton_dragons
    comparisons = find_skeleton_dragons(deck_image, comparisons)
    # wizard
    comparisons = find_wizard(deck_image, comparisons)
    # skeleton_army
    comparisons = find_skeleton_army(deck_image, comparisons)
    # arrows
    comparisons = find_arrows(deck_image, comparisons)
    # spear_goblins
    comparisons = find_spear_goblins(deck_image, comparisons)
    # battle_ram
    comparisons = find_battle_ram(deck_image, comparisons)
    # e_wiz
    comparisons = find_e_wiz(deck_image, comparisons)
    # archer_queen
    comparisons = find_archer_queen(deck_image, comparisons)
    # barb_barrel
    comparisons = find_barb_barrel(deck_image, comparisons)
    # healer
    comparisons = find_healer(deck_image, comparisons)
    # graveyard
    comparisons = find_graveyard(deck_image, comparisons)
    # rocket
    comparisons = find_rocket(deck_image, comparisons)
    # e_giant
    comparisons = find_e_giant(deck_image, comparisons)
    # tombstone
    comparisons = find_tombstone(deck_image, comparisons)
    # bats
    comparisons = find_bats(deck_image, comparisons)
    # archers
    comparisons = find_archers(deck_image, comparisons)
    # inferno_tower
    comparisons = find_inferno_tower(deck_image, comparisons)
    # fisherman
    comparisons = find_fisherman(deck_image, comparisons)
    # mighty_miner
    comparisons = find_mighty_miner(deck_image, comparisons)
    # goblin_hut
    comparisons = find_goblin_hut(deck_image, comparisons)
    # mother_witch
    comparisons = find_mother_witch(deck_image, comparisons)
    # pekka
    comparisons = find_pekka(deck_image, comparisons)
    # baby_dragon
    comparisons = find_baby_dragon(deck_image, comparisons)
    # log
    comparisons = find_log(deck_image, comparisons)
    # earthquake
    comparisons = find_earthquake(deck_image, comparisons)
    # fireball
    comparisons = find_fireball(deck_image, comparisons)
    # cannon
    comparisons = find_cannon(deck_image, comparisons)
    # royal_giant
    comparisons = find_royal_giant(deck_image, comparisons)
    # royal_hogs
    comparisons = find_royal_hogs(deck_image, comparisons)
    # golden_knight
    comparisons = find_golden_knight(deck_image, comparisons)
    return comparisons


def find_zap(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zap_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found zap in deck")
            comparisons = add_card_to_deck(comparisons, "zap")
    return comparisons


def find_witch(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "witch_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found witch in deck")
            comparisons = add_card_to_deck(comparisons, "witch")
    return comparisons


def find_golden_knight(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golden_knight_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golden_knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golden_knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golden_knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golden_knight_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found golden_knight in deck")
            comparisons = add_card_to_deck(comparisons, "golden_knight")
    return comparisons


def find_royal_hogs(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_hogs_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found royal_hogs in deck")
            comparisons = add_card_to_deck(comparisons, "royal_hogs")
    return comparisons


def find_royal_giant(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_giant_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found royal_giant in deck")
            comparisons = add_card_to_deck(comparisons, "royal_giant")
    return comparisons


def find_cannon(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_14.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found cannon in deck")
            comparisons = add_card_to_deck(comparisons, "cannon")
    return comparisons


def find_fireball(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fireball_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found fireball in deck")
            comparisons = add_card_to_deck(comparisons, "fireball")
    return comparisons


def find_earthquake(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "earthquake_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found earthquake in deck")
            comparisons = add_card_to_deck(comparisons, "earthquake")
    return comparisons


def find_log(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "log_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found log in deck")
            comparisons = add_card_to_deck(comparisons, "log")
    return comparisons


def find_baby_dragon(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "baby_dragon_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found baby_dragon in deck")
            comparisons = add_card_to_deck(comparisons, "baby_dragon")
    return comparisons


def find_pekka(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_3.png")), 0.97) is not None:
            n = 1

        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "pekka_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found pekka in deck")
            comparisons = add_card_to_deck(comparisons, "pekka")
    return comparisons


def find_mother_witch(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mother_witch_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mother_witch in deck")
            comparisons = add_card_to_deck(comparisons, "mother_witch")
    return comparisons


def find_goblin_hut(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_1.png")), 0.97) is not None:
            # print("1************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_2.png")), 0.97) is not None:
            # print("2************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_3.png")), 0.97) is not None:
            # print("3************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_4.png")), 0.97) is not None:
            # print("4************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_5.png")), 0.97) is not None:
            # print("5************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_6.png")), 0.97) is not None:
            # print("6************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_7.png")), 0.97) is not None:
            # print("7************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_8.png")), 0.97) is not None:
            # print("8************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_9.png")), 0.97) is not None:
            # print("9************")
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_hut_10.png")), 0.97) is not None:
            # print("10************")
            n = 1
        if n == 1:
            print("Found goblin_hut in deck")
            comparisons = add_card_to_deck(comparisons, "goblin_hut")
    return comparisons


def find_mighty_miner(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mighty_miner_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mighty_miner in deck")
            comparisons = add_card_to_deck(comparisons, "mighty_miner")
    return comparisons


def find_fisherman(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fisherman_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found fisherman in deck")
            comparisons = add_card_to_deck(comparisons, "fisherman")
    return comparisons


def find_inferno_tower(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_tower_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found inferno_tower in deck")
            comparisons = add_card_to_deck(comparisons, "inferno_tower")
    return comparisons


def find_archers(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archers_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found archers in deck")
            comparisons = add_card_to_deck(comparisons, "archers")
    return comparisons


def find_bats(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bats_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found bats in deck")
            comparisons = add_card_to_deck(comparisons, "bats")
    return comparisons


def find_tombstone(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tombstone_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found tombstone in deck")
            comparisons = add_card_to_deck(comparisons, "tombstone")
    return comparisons


def find_e_giant(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_giant_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found e_giant in deck")
            comparisons = add_card_to_deck(comparisons, "e_giant")
    return comparisons


def find_rocket(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_1.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_2.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_3.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_4.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_5.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_6.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_7.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_8.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_9.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_10.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_11.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_12.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_13.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_14.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rocket_15.png")), 0.90) is not None:
            n = 1
        if n == 1:
            print("Found rocket in deck")
            comparisons = add_card_to_deck(comparisons, "rocket")
    return comparisons


def find_graveyard(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_1.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_2.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_3.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_4.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_5.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_6.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_7.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_8.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_9.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_10.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_11.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_12.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_13.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_14.png")), 0.90) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "graveyard_15.png")), 0.90) is not None:
            n = 1
        if n == 1:
            print("Found graveyard in deck")
            comparisons = add_card_to_deck(comparisons, "graveyard")
    return comparisons


def find_healer(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "healer_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found healer in deck")
            comparisons = add_card_to_deck(comparisons, "healer")
    return comparisons


def find_barb_barrel(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_barrel_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found barb_barrel in deck")
            comparisons = add_card_to_deck(comparisons, "barb_barrel")
    return comparisons


def find_archer_queen(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "archer_queen_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found archer queen in deck")
            comparisons = add_card_to_deck(comparisons, "archer_queen")
    return comparisons


def find_e_wiz(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_wiz_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found e_wiz in deck")
            comparisons = add_card_to_deck(comparisons, "e_wiz")
    return comparisons


def find_battle_ram(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "battle_ram_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found battle_ram in deck")
            comparisons = add_card_to_deck(comparisons, "battle_ram")
    return comparisons


def find_spear_goblins(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "spear_goblins_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found spear_goblins in deck")
            comparisons = add_card_to_deck(comparisons, "spear_goblins")
    return comparisons


def find_arrows(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "arrows_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found arrows in deck")
            comparisons = add_card_to_deck(comparisons, "arrows")
    return comparisons


def find_skeleton_army(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_army_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found skeleton_army in deck")
            comparisons = add_card_to_deck(comparisons, "skeleton_army")
    return comparisons


def find_wizard(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_15.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_16.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_17.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wizard_18.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found wizard in deck")
            comparisons = add_card_to_deck(comparisons, "wizard")
    return comparisons


def find_skeleton_dragons(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_dragons_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found skeleton_dragons in deck")
            comparisons = add_card_to_deck(comparisons, "skeleton_dragons")
    return comparisons


def find_prince(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "prince_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found prince in deck")
            comparisons = add_card_to_deck(comparisons, "prince")
    return comparisons


def find_goblin_giant(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_15.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_giant_16.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found goblin_giant in deck")
            comparisons = add_card_to_deck(comparisons, "goblin_giant")
    return comparisons


def find_zappies(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "zappies_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found zappies in deck")
            comparisons = add_card_to_deck(comparisons, "zappies")
    return comparisons


def find_lavahound(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lavahound_14.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found lavahound in deck")
            comparisons = add_card_to_deck(comparisons, "lavahound")
    return comparisons


def find_lightning(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lightning_13.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found lightning in deck")
            comparisons = add_card_to_deck(comparisons, "lightning")
    return comparisons


def find_executioner(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "executioner_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found executioner in deck")
            comparisons = add_card_to_deck(comparisons, "executioner")
    return comparisons


def find_goblin_drill(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_drill_7.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found goblin_drill in deck")
            comparisons = add_card_to_deck(comparisons, "goblin_drill")
    return comparisons


def find_rage(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rage_11.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found rage in deck")
            comparisons = add_card_to_deck(comparisons, "rage")
    return comparisons


def find_clone(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "clone_13.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found clone in deck")
            comparisons = add_card_to_deck(comparisons, "clone")
    return comparisons


def find_goblin_barrel(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_barrel_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found goblin_barrel in deck")
            comparisons = add_card_to_deck(comparisons, "goblin_barrel")
    return comparisons


def find_minion_hoard(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minion_hoard_14.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found minion_hoard in deck")
            comparisons = add_card_to_deck(comparisons, "minion_hoard")
    return comparisons


def find_barbs(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barbs_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found barbs in deck")
            comparisons = add_card_to_deck(comparisons, "barbs")
    return comparisons


def find_tornado(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tornado_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found tornado in deck")
            comparisons = add_card_to_deck(comparisons, "tornado")
    return comparisons


def find_skeleton_barrel(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_barrel_14.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found skeleton_barrel in deck")
            comparisons = add_card_to_deck(comparisons, "skeleton_barrel")
    return comparisons


def find_miner(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "miner_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found miner in deck")
            comparisons = add_card_to_deck(comparisons, "miner")
    return comparisons


def find_skeletons(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeletons_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found skeletons in deck")
            comparisons = add_card_to_deck(comparisons, "skeletons")
    return comparisons


def find_elite_barbs(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_15.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_16.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_17.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_18.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_19.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elite_barbs_20.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found elite_barbs in deck")
            comparisons = add_card_to_deck(comparisons, "elite_barbs")
    return comparisons


def find_flying_machine(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "flying_machine_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found flying_machine in deck")
            comparisons = add_card_to_deck(comparisons, "flying_machine")
    return comparisons


def find_e_dragon(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_dragon_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found e_dragon in deck")
            comparisons = add_card_to_deck(comparisons, "e_dragon")
    return comparisons


def find_xbow(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "xbow_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found xbow in deck")
            comparisons = add_card_to_deck(comparisons, "xbow")
    return comparisons


def find_elixer_golem(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_golem_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found elixer_golem in deck")
            comparisons = add_card_to_deck(comparisons, "elixer_golem")
    return comparisons


def find_rascals(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "rascals_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found rascals in deck")
            comparisons = add_card_to_deck(comparisons, "rascals")
    return comparisons


def find_skeleton_king(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "skeleton_king_14.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found skeleton_king in deck")
            comparisons = add_card_to_deck(comparisons, "skeleton_king")
    return comparisons


def find_balloon(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "balloon_15.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found balloon in deck")
            comparisons = add_card_to_deck(comparisons, "balloon")
    return comparisons


def find_sparky(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "sparky_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found sparky in deck")
            comparisons = add_card_to_deck(comparisons, "sparky")
    return comparisons


def find_golem(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golem_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golem_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golem_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golem_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "golem_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found golem in deck")
            comparisons = add_card_to_deck(comparisons, "golem")
    return comparisons


def find_barb_hut(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_hut_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_hut_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_hut_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_hut_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "barb_hut_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found barb_hut in deck")
            comparisons = add_card_to_deck(comparisons, "barb_hut")
    return comparisons


def find_bomb_tower(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomb_tower_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found bomb_tower in deck")
            comparisons = add_card_to_deck(comparisons, "bomb_tower")
    return comparisons


def find_mortar(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mortar_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mortar_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mortar_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mortar_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mortar_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mortar in deck")
            comparisons = add_card_to_deck(comparisons, "mortar")
    return comparisons


def find_inferno_dragon(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "inferno_dragon_13.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found inferno_dragon in deck")
            comparisons = add_card_to_deck(comparisons, "inferno_dragon")
    return comparisons


def find_hunter(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hunter_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hunter_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hunter_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hunter_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hunter_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found hunter in deck")
            comparisons = add_card_to_deck(comparisons, "hunter")
    return comparisons


def find_giant(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found giant in deck")
            comparisons = add_card_to_deck(comparisons, "giant")
    return comparisons


def find_freeze(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "freeze_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "freeze_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "freeze_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "freeze_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "freeze_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found freeze in deck")
            comparisons = add_card_to_deck(comparisons, "freeze")
    return comparisons


def find_lumberjack(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "lumberjack_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found lumberjack in deck")
            comparisons = add_card_to_deck(comparisons, "lumberjack")
    return comparisons


def find_bowler(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bowler_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bowler_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bowler_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bowler_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bowler_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found bowler in deck")
            comparisons = add_card_to_deck(comparisons, "bowler")
    return comparisons


def find_dart_goblin(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dart_goblin_8.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found dart_goblin in deck")
            comparisons = add_card_to_deck(comparisons, "dart_goblin")
    return comparisons


def find_mini_pekka(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mini_pekka_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mini_pekka in deck")
            comparisons = add_card_to_deck(comparisons, "mini_pekka")
    return comparisons


def find_mega_knight(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_knight_13.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mega_knight in deck")
            comparisons = add_card_to_deck(comparisons, "mega_knight")
    return comparisons


def find_elixer_pump(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_pump_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_pump_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_pump_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_pump_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "elixer_pump_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found elixer_pump in deck")
            comparisons = add_card_to_deck(comparisons, "elixer_pump")
    return comparisons


def find_giant_skeleton(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_skeleton_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_skeleton_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_skeleton_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_skeleton_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "giant_skeleton_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found giant_skeleton in deck")
            comparisons = add_card_to_deck(comparisons, "giant_skeleton")
    return comparisons


def find_magic_archer(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "magic_archer_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "magic_archer_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "magic_archer_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "magic_archer_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "magic_archer_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found magic_archer in deck")
            comparisons = add_card_to_deck(comparisons, "magic_archer")
    return comparisons


def find_firecracker(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "firecracker_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found firecracker in deck")
            comparisons = add_card_to_deck(comparisons, "firecracker")
    return comparisons


def find_knight(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "knight_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found knight in deck")
            comparisons = add_card_to_deck(comparisons, "knight")
    return comparisons


def find_cannon_cart(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_cart_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_cart_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_cart_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_cart_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "cannon_cart_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found cannon_cart in deck")
            comparisons = add_card_to_deck(comparisons, "cannon_cart")
    return comparisons


def find_hog(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "hog_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found hog in deck")
            comparisons = add_card_to_deck(comparisons, "hog")
    return comparisons


def find_fire_spirit(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "fire_spirit_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found fire_spirit in deck")
            comparisons = add_card_to_deck(comparisons, "fire_spirit")
    return comparisons


def find_ice_spirit(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_spirit_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found ice_spirit in deck")
            comparisons = add_card_to_deck(comparisons, "ice_spirit")
    return comparisons


def find_bandit(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bandit_13.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found bandit in deck")
            comparisons = add_card_to_deck(comparisons, "bandit")
    return comparisons


def find_musketeer(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "musketeer_5.png")), 0.97) is not None:
            n = 1

        if n == 1:
            print("Found musketeer in deck")
            comparisons = add_card_to_deck(comparisons, "musketeer")
    return comparisons


def find_furnace(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_13.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_14.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_15.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_16.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_17.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_18.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_19.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_20.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_21.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_22.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_23.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_24.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "furnace_25.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found furnace in deck")
            comparisons = add_card_to_deck(comparisons, "furnace")
    return comparisons


def find_snowball(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "snowball_12.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found snowball in deck")
            comparisons = add_card_to_deck(comparisons, "snowball")
    return comparisons


def find_royal_recruits(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_recruits_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found royal_recruits in deck")
            comparisons = add_card_to_deck(comparisons, "royal_recruits")
    return comparisons


def find_dark_knight(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_12.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "dark_knight_13.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found dark_knight in deck")
            comparisons = add_card_to_deck(comparisons, "dark_knight")
    return comparisons


def find_valk(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "valk_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found valk in deck")
            comparisons = add_card_to_deck(comparisons, "valk")
    return comparisons


def find_goblin_gang(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblin_gang_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found goblin_gang in deck")
            comparisons = add_card_to_deck(comparisons, "goblin_gang")
    return comparisons


def find_tesla(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "tesla_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found tesla in deck")
            comparisons = add_card_to_deck(comparisons, "tesla")
    return comparisons


def find_royal_ghost(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_ghost_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found royal_ghost in deck")
            comparisons = add_card_to_deck(comparisons, "royal_ghost")
    return comparisons


def find_bomber(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "bomber_11.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found bomber in deck")
            comparisons = add_card_to_deck(comparisons, "bomber")
    return comparisons


def find_ram_rider(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ram_rider_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found ram_rider in deck")
            comparisons = add_card_to_deck(comparisons, "ram_rider")
    return comparisons


def find_mirror(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mirror_11.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mirror in deck")
            comparisons = add_card_to_deck(comparisons, "mirror")
    return comparisons


def find_poison(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "poison_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found poison in deck")
            comparisons = add_card_to_deck(comparisons, "poison")
    return comparisons


def find_royal_delivery(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "royal_delivery_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found royal_delivery in deck")
            comparisons = add_card_to_deck(comparisons, "royal_delivery")
    return comparisons


def find_heal_spirit(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "heal_spirit_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found heal_spirit in deck")
            comparisons = add_card_to_deck(comparisons, "heal_spirit")
    return comparisons


def find_ice_golem(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_golem_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found ice_golem in deck")
            comparisons = add_card_to_deck(comparisons, "ice_golem")
    return comparisons


def find_wall_breaker(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "wall_breaker_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found wall_breaker in deck")
            comparisons = add_card_to_deck(comparisons, "wall_breaker")
    return comparisons


def find_guards(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "guards_9.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found guards in deck")
            comparisons = add_card_to_deck(comparisons, "guards")
    return comparisons


def find_princess(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "princess_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found princess in deck")
            comparisons = add_card_to_deck(comparisons, "princess")
    return comparisons


def find_night_witch(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "night_witch_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found night_witch in deck")
            comparisons = add_card_to_deck(comparisons, "night_witch")
    return comparisons


def find_e_spirit(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "e_spirit_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found e_spirit in deck")
            comparisons = add_card_to_deck(comparisons, "e_spirit")
    return comparisons


def find_ice_wizard(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "ice_wizard_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found ice_wizard in deck")
            comparisons = add_card_to_deck(comparisons, "ice_wizard")
    return comparisons


def find_minions(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "minions_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found minions in deck")
            comparisons = add_card_to_deck(comparisons, "minions")
    return comparisons


def find_goblins(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "goblins_10.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found goblins in deck")
            comparisons = add_card_to_deck(comparisons, "goblins")
    return comparisons


def find_mega_minion(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "mega_minion_5.png")), 0.97) is not None:
            n = 1
        if n == 1:
            print("Found mega_minion in deck")
            comparisons = add_card_to_deck(comparisons, "mega_minion")
    return comparisons


def find_three_musketeers(deck_image, comparisons):
    if 1 == 1:
        n = 0
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_1.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_2.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_3.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_4.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_5.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_6.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_7.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_8.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_9.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_10.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_11.png")), 0.97) is not None:
            n = 1
        if compare_images(deck_image, Image.open(join("pyclashbot", "reference_images", "deck_cards", "three_musketeers_12.png")), 0.97) is not None:
            n = 1

        if n == 1:
            print("Found three_musketeers in deck")
            comparisons = add_card_to_deck(comparisons, "three_musketeers")
    return comparisons
