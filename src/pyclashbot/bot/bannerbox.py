from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, save_screenshot, screenshot
from pyclashbot.utils.logger import Logger
import time

BANNERBOX_ICON_ON_CLASH_MAIN_PAGE = (350, 195)
FIRST_100_TICKETS_PURCHASE_BUTTON = (303, 576)
SECOND_100_TICKETS_PURCHASE_BUTTON = (209, 466)



def collect_bannerbox_rewards_state(vm_index:int,logger:Logger,next_state:str):
    if collect_bannerbox_rewards(vm_index, logger):
        return next_state
    return 'restart'


def collect_bannerbox_rewards(vm_index, logger: Logger) -> bool :
    logger.change_status("Collecting bannerbox rewards")

    # if not in clash main, return false
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status("Not in clash main menu")
        return False

    # click bannerbox button on clash main
    click(
        vm_index,
        BANNERBOX_ICON_ON_CLASH_MAIN_PAGE[0],
        BANNERBOX_ICON_ON_CLASH_MAIN_PAGE[1],
    )
    time.sleep(4)

    # click the '100 tickets' purchase button
    click(
        vm_index,
        FIRST_100_TICKETS_PURCHASE_BUTTON[0],
        FIRST_100_TICKETS_PURCHASE_BUTTON[1],
    )
    time.sleep(4)

    # check if the second '100 tickets' purchase button is Red or not
    if not check_if_can_purchase_100_tickets_bannerbox(vm_index):
        logger.change_status('Bannerbox not available.')

        # click deadspace a bunch, then return
        click(vm_index, 10, 250, clicks=10, interval=0.33)
        return True

    logger.change_status('Bannerbox is available! Buying it...')

    #click the second '100 tickets' purchase button
    click(
        vm_index,
        SECOND_100_TICKETS_PURCHASE_BUTTON[0],
        SECOND_100_TICKETS_PURCHASE_BUTTON[1],
    )

    #click deadspace until back on clash main
    logger.change_status('Skipping through bannerbox rewards...')
    deadspace_click_timeout = 30#s
    deadspace_click_start_time = time.time()
    while check_if_on_clash_main_menu(vm_index) is not True:
        #timeout check
        if time.time() -deadspace_click_start_time >deadspace_click_timeout:
            return False

        #click deadspace
        click(vm_index, 10, 250, clicks=5, interval=0.33)

    #return true if everything went well
    return True



def check_if_can_purchase_100_tickets_bannerbox(vm_index):
    iar = screenshot(vm_index)

    pixels = [
        iar[467][172],
        iar[473][172],
        iar[468][188],
    ]
    colors = [
        [0, 0, 255],
        [0, 1, 255],
        [2, 11, 250],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return True

    return False


if __name__ == "__main__":
    collect_bannerbox_rewards_state(11,Logger(),'next_state')
