from pyclashbot.utils.logger import Logger
from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import screenshot, click
import numpy
import time


def collect_level_up_chest(vm_index, logger):
    logger.change_status("Checking level up chest")

    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main for collect_level_up_chest(). Returning False"
        )
        return False

    if not check_for_level_up_chest(vm_index):
        logger.change_status("No level up chest")
        return True

    # click level up chest
    print("Clicking level up chest icon")
    click(vm_index, 17, 16)
    time.sleep(2)

    # click the level up chest
    logger.change_status("Collecting this level up chest")
    click(vm_index, 115, 125)
    time.sleep(2)

    # click deadspace until back on clash main
    timeout = 30  # s
    start_time = time.time()
    while not check_if_on_clash_main_menu(vm_index):
        # timeout check
        if time.time() - start_time > timeout:
            logger.change_status("Timed out waiting for level up chest to be collected")
            return False

        print("Clicking deadspace to skip thru rewards")
        click(vm_index, 19, 327)
        time.sleep(1)

    return True


def check_for_level_up_chest(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[9][9],
        iar[9][22],
        iar[12][16],
        iar[23][16],
    ]

    colors = [
        [245, 195, 79],
        [246, 215, 63],
        [108, 211, 247],
        [221, 169, 39],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=15):
            return True

    return False


if __name__ == "__main__":
    vm_index = 12
    logger = Logger()
    collect_level_up_chest(vm_index, logger)
