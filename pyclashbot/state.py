import time

from pyclashbot.client import (check_quit_key_press, click, refresh_screen, screenshot)

from pyclashbot.image_rec import (check_for_location, find_reference,
                                  find_references)


# region state checking





def check_state(logger):
    time.sleep(3)

    #add a check for memu main
    
    # if on regular main menu
    if check_if_on_clash_main_menu():
        logger.log("On clash main")
        return "clash_main"
    # if on clan chat page
    if check_if_on_clan_chat_page():
        logger.log("On clan chat page")
        return_to_clash_main_menu()
        time.sleep(2)
        if check_if_on_clash_main_menu():
            return "clash_main"
        else:
            return "restart"
    # if anywhere in clash home pages
    if check_if_on_clash_home():
        logger.log("Detected that we're somewhere on the clash home")
        return_to_clash_main_menu()
        time.sleep(2)
        if check_if_on_clash_main_menu():
            return"clash_main"
        else:
            return"restart"
    # if in a battle
    if check_if_in_battle():
        logger.log("In a fight")
        return "fighting"
    return None


def check_if_on_level_up_screen(logger):
    current_image = screenshot()
    reference_folder = "level_up_screen"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
    ]
    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return True
    return False


def check_if_on_clash_main_menu():
    current_image = screenshot()
    reference_folder = "clash_main_menu"
    references = [
        "clash_main_1.png",
        "clash_main_2.png",
        "clash_main_3.png",
        "clash_main_4.png",
        "clash_main_5.png"
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    return check_for_location(locations)


def check_if_on_clan_chat_page():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=refresh_screen(),
        folder="check_if_on_clan_chat_page",
        names=references,
        tolerance=0.97
    )

    return check_for_location(locations)


def check_if_on_clash_home():
    current_image = screenshot()
    reference_folder = "clash_home_images"
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
    return check_for_location(locations)


def check_if_in_battle():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png"
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97
    )

    return check_for_location(locations)


# endregion

# region state changing

def open_clash(logger):
    orientate_window()
    time.sleep(1)
    check_quit_key_press()
    logger.log("opening clash")

    coords = find_reference(
        screenshot=refresh_screen(),
        folder="logo",
        name="clash_logo.png",
        tolerance=0.97
    )

    if coords is None:
        logger.log("Clash logo wasn't found")
        return "quit"
    click(x=coords[1], y=coords[0])
    # return coords

    if wait_for_clash_main_menu(logger) == "quit":
        return "quit"


def wait_for_clash_main_menu(logger):
    n = 0
    while not check_if_on_clash_main_menu():

        check_quit_key_press()
        # handle if stuck on trophy progression page
        if check_if_on_trophy_progession_rewards_page():
            logger.log(
                "Bot appears to be stuck on trophy progression rewards menu. Closing that.")
            click(212, 633)
            time.sleep(0.5)
        time.sleep(3)
        logger.log(f"Waiting for clash main menu/{n}")
        n = n + 1
        if n > 20:
            logger.log("Waiting longer than a minute for clash main menu")
            return "quit"
        if check_if_on_level_up_screen(logger):
            click(208, 560)
            time.sleep(2)

        click(10, 170)


def return_to_clash_main_menu():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "main_menu_golden1.png",
        "main_menu_golden2.png",
        "main_menu_golden3.png",
        "main_menu_golden4.png",
        "main_menu_golden5.png",
        "main_menu_golden6.png",
        "main_menu_golden7.png",
        "main_menu_golden8.png",
        "main_menu_golden9.png",
        "main_menu_golden10.png",
        "main_menu_golden11.png",
        "main_menu_golden12.png",
        "main_menu_golden13.png",
        "main_menu_golden14.png",
        "main_menu_golden15.png",
        "main_menu_golden16.png",
        "main_menu_golden17.png",
        "main_menu_golden18.png",
        "main_menu_golden19.png",
        "main_menu_golden20.png",
        "main_menu_golden21.png",
        "main_menu_golden22.png",
        "main_menu_golden23.png",
        "main_menu_golden24.png",
        "main_menu_golden25.png",
        "main_menu_golden26.png",
        "main_menu_golden27.png",
        "main_menu_golden28.png",
        "main_menu_golden29.png",
        "main_menu_golden30.png",
        "main_menu_golden31.png",
        "main_menu_golden32.png",
        "main_menu_golden33.png",
        "main_menu_golden34.png",
        "main_menu_golden35.png",
        "main_menu_golden36.png",
        "main_menu_golden37.png",
        "main_menu_golden38.png",
        "main_menu_golden39.png",
        "main_menu_golden40.png",
        "main_menu_golden41.png",
        "main_menu_golden42.png",
        "main_menu_golden43.png",
        "main_menu_golden44.png",
        "main_menu_golden45.png",
        "main_menu_golden46.png",
        "main_menu_golden47.png",
        "main_menu_golden48.png",
        "main_menu_golden49.png",
        "main_menu_golden50.png",
        "main_menu_golden51.png",
        "main_menu_golden52.png",
        "main_menu_golden53.png",
        "main_menu_golden54.png",
        "main_menu_golden55.png",
        "main_menu_golden56.png",
        "main_menu_golden57.png",
        "main_menu_golden58.png",
        "main_menu_golden59.png",
        "main_menu_golden60.png",
        "main_menu_golden61.png",
        "main_menu_golden62.png",
        "main_menu_golden63.png",
        "main_menu_golden64.png",
        "main_menu_golden65.png",
        "main_menu_golden66.png",
        "main_menu_golden67.png",
        "main_menu_golden68.png",
        "main_menu_golden69.png",
        "g1.png",
        "g2.png",
        "g3.png",
        "g4.png",
        "g5.png",
        "g6.png",
        "g7.png",
        "g8.png",
        "g9.png",
        "g10.png",
        "g11.png",
        "g12.png",
        "g13.png",
        "g14.png",
        "g15.png",
        "g16.png",
        "g17.png",
        "g18.png",
        "g19.png",
        "g20.png",
        "g21.png",
        "g22.png",
        "g23.png",
        "g24.png",
        "g25.png",
        "g26.png",
        "g27.png",
        "g28.png",
        "g29.png",
        "g30.png",
        "g31.png",
        "g32.png",
        "g33.png",
        "g34.png",
        "g35.png",
        "g36.png",
        "g37.png",
        "g38.png",
        "g39.png",
        "g40.png",
        "g41.png",
        "g42.png",
        "g43.png",
        "g44.png",
        "g45.png",
        "g46.png",
        "g47.png",
        "g48.png",
        "g49.png",
        "g50.png",
        "g51.png",
        "g52.png",
        "g53.png",
        "g54.png",
        "g55.png",
        "g56.png",
        "g57.png",
        "g58.png",
        "g59.png",
        "g60.png",
    ]
    locations = find_references(
        screenshot=refresh_screen(),
        folder="return_to_clash_main",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            click(location[1], location[0])
            return


def check_if_on_trophy_progession_rewards_page():
    current_image = screenshot()
    reference_folder = "trophy_progression_rewards"
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
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return True  # found a location
    return False


def check_if_in_a_clan_from_main(logger):
    logger.log("Checking if you're in a clan")
    click(315, 630, 3, 1)
    time.sleep(2)
    current_image = screenshot()
    reference_folder = "not_in_a_clan"
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
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    click(175, 630)
    time.sleep(1)
    for location in locations:
        if location is not None:
            logger.log("You're not in a clan")
            time.sleep(1)
            return_to_clash_main_menu()
            time.sleep(1)
            return False  # found a location
    logger.log("You're in a clan")
    time.sleep(1)
    time.sleep(1)
    return True


def refresh_clan_tab(logger):
    check_quit_key_press()
    click(300, 630)
    return_to_clash_main_menu()
    time.sleep(3)
    check_quit_key_press()

# endregion
