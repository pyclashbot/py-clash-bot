import numpy
import time

from pyclashbot.detection.image_rec import find_references, pixel_is_equal
from pyclashbot.memu.client import click, get_file_count, make_reference_image_list, screenshot


def open_chests(logger):
    logger.change_status("Opening chests")

    # check which chests exist
    existing_chests_array = check_for_chests()

    # identify locations of chests
    chest_coord_list = [
        [78, 554],
        [162, 549],
        [263, 541],
        [349, 551],
    ]

    # for each chest that exists
    # click current chest
    # check if unlock appears
    # if unlock appears unlock the chest
    # else click dead space 15 times to skip thru rewards
    # then close this chest menu.
    index = 0
    for chest in existing_chests_array:
        if chest:
            logger.change_status("Handling chest number: " + str(index + 1))
            # click chest
            chest_coord = chest_coord_list[index]
            click(chest_coord[0], chest_coord[1])

            if check_if_unlock_chest_button_exists_with_delay():
                print("Unlocked a chest", index + 1)
                logger.add_chest_unlocked()
                click(210, 465)
            else:
                print("Skipping through rewards for chest index: ", index + 1)
                click(20, 556, clicks=15, interval=0.45)

            # close chest menu
            print("Closing chest index", index + 1)
            click(20, 556)

        index += 1

    logger.change_status("Done collecting chests.")


def check_for_chests():
    # returns an array of 4 bools each representing a chest slot
    # true means hsa chest, false means no chest
    return_bool_list = []

    # make a list of 4 pixels each representing a chest
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[572][92],
        iar[567][155],
        iar[568][269],
        iar[566][329],
    ]

    # print this pixel list
    # print_pix_list(pix_list)

    for pix in pix_list:
        if pixel_is_equal(pix, [27, 110, 146], tol=25):
            return_bool_list.append(False)
        else:
            return_bool_list.append(True)

    print("chest_exists_bool_list", return_bool_list)

    # return this list
    return return_bool_list

def check_if_unlock_chest_button_exists():
    # method to find the 2v2 quickmatch button in the party mode menu
    current_image = screenshot()
    reference_folder = "unlock_chest_button"

    references = make_reference_image_list(
        get_file_count(
            "unlock_chest_button",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    return any(location is not None for location in locations)




def check_if_unlock_chest_button_exists_with_delay():
    start_time=time.time()
    while True:
        if time.time()-start_time>3:
            return False
        if check_if_unlock_chest_button_exists():
            return True