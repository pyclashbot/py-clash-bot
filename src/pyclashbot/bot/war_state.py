from bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_profile_page,
    wait_for_clash_main_menu,
)
from detection.image_rec import (
    check_for_location,
    check_line_for_color,
    find_reference,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from memu.client import click, screenshot
from utils.logger import Logger
import numpy


def war_state(vm_index: int, logger: Logger, NEXT_STATE: str):
    logger.change_status("War state")

    # if not on clash main: return
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status("Error 4069852734098 Not on clash main to begin war state")

    # if in a clan:
    if war_state_check_if_in_a_clan(vm_index, logger):
        pass

        # get to clan page
        get_to_clan_tab_from_clash_main(vm_index, logger)

        # find battle icon

        # click battle icon

        # make deck if needed

        # start battle

        # wait for battle start

        # do fight

        # when battle end, leave battle

    else:
        # return to main
        pass


def click_war_icon(vm_index, logger: Logger):
    logger.change_status("Finding a war battle icon to play in")


def find_war_icon(vm_index):
    folder = "war_battle_icon"

    image_names = make_reference_image_list(get_file_count(folder))

    locations = find_references(
        screenshot(vm_index),
        folder,
        image_names,
        tolerance=0.99,
    )

    coord = get_first_location(locations)
    return coord


def check_if_on_war_page(vm_index):
    lines = [
        check_line_for_color(
            vm_index, x1=45, y1=552, x2=64, y2=558, color=(194, 124, 14)
        ),
        check_line_for_color(
            vm_index, x1=86, y1=557, x2=108, y2=549, color=(208, 144, 2)
        ),
        check_line_for_color(
            vm_index, x1=220, y1=550, x2=239, y2=560, color=(194, 124, 13)
        ),
        check_line_for_color(
            vm_index, x1=226, y1=559, x2=285, y2=553, color=(224, 160, 8)
        ),
    ]

    return all(lines)


def war_state_check_if_in_a_clan(vm_index, logger: Logger):
    # if not on clash main, reutnr
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(f"ERROR 385423562623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status("Error 90723563485 Failure with get_to_profile_page")
        return "restart"

    # check pixels for in a clan
    in_a_clan = war_state_check_pixels_for_clan_flag(vm_index)

    # click deadspace to leave
    click(vm_index, 15, 300)
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status("Error 872356739 Failure with wait_for_clash_main_menu")
        return "restart"

    return in_a_clan


def war_state_check_pixels_for_clan_flag(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    for x in range(78, 97):
        this_pixel = iar[446][x]
        if not (pixel_is_equal([51, 51, 51], this_pixel, tol=25)):
            return True

    for y in range(437, 455):
        this_pixel = iar[y][87]
        if not (pixel_is_equal([51, 51, 51], this_pixel, tol=25)):
            return True

    return False


if __name__ == "__main__":
    pass
