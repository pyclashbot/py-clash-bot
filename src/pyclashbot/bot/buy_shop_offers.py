import time

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_shop_page_from_clash_main,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_first_location,
    get_file_count,
    make_reference_image_list,
)
from pyclashbot.memu.client import (
    screenshot,
    click,
    scroll_down_slowly_in_shop_page,
)

from pyclashbot.utils.logger import Logger


def search_for_free_purchases(vm_index):
    """method to find the free offer icon image in the shop pages"""

    folder_name = "free_offer_icon"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.9,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def buy_free_offer(vm_index):
    coord = search_for_free_purchases(vm_index)

    if coord is None:
        return False

    # click the location of the free offer icon
    click(vm_index, coord[0], coord[1])

    # click the second 'buy' button
    click(vm_index, 200, 433)

    # click deadspace to close this offer
    click(vm_index, 15, 200, clicks=10)


def search_for_gold_purchases(vm_index):
    """method to find the offers for gold icon image in the shop pages"""

    folder_name = "offers_for_gold"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.9,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def buy_offers_from_this_shop_page(vm_index, gold_buy_toggle, free_offers_toggle):
    coord = None

    if gold_buy_toggle:
        coord = search_for_gold_purchases(vm_index)

    # if no gold purchases, find a free purchase
    if coord is None and free_offers_toggle:
        coord = search_for_free_purchases(vm_index)

    # if there are no purchases at this point, return False
    if coord is None:
        return False

    # click the location of the 'cards for gold' icon
    click(vm_index, coord[0], coord[1])
    time.sleep(2)

    # click the second 'buy' button
    click(vm_index, 200, 433)
    click(vm_index, 204, 394)
    time.sleep(2)

    # click deadspace to close this offer
    click(vm_index, 15, 200, clicks=10)
    time.sleep(1)
    return True


def buy_shop_offers_state(
    vm_index: int,
    logger: Logger,
    gold_buy_toggle: bool,
    free_offers_toggle: bool,
    next_state: str,
):
    print("Entering buy_shop_offers_state()")
    print(f"gold_buy_toggle: {gold_buy_toggle}")
    print(f"free_offers_toggle: {free_offers_toggle}")

    logger.add_shop_buy_attempt()

    # if not on clash main, return False
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main to being buying offers. Returning restart"
        )
        return "restart"

    # get to shop page
    logger.change_status("Getting to shop page to buy offers")
    if get_to_shop_page_from_clash_main(vm_index, logger) is False:
        logger.change_status("Failed to get to shop page to buy offers")
        return "restart"

    # scroll incrementally while searching for rewards, clicking and buying any rewards found
    start_time = time.time()
    timeout = 90
    logger.change_status("Starting to buy offers")
    while 1:
        if time.time() - start_time > timeout:
            break

        # scroll a little
        scroll_down_slowly_in_shop_page(vm_index)
        time.sleep(0.33)

        if gold_buy_toggle:
            while (
                buy_offers_from_this_shop_page(
                    vm_index, gold_buy_toggle, free_offers_toggle
                )
                is True
            ):
                logger.change_status("Bought an offer from the shop!")
                logger.add_shop_buy()

    # get to clash main from shop page
    click(vm_index, 245, 596)
    time.sleep(4)

    # if not on clash main, return False
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status("Not on clash main after buying offers. Returning restart")
        return "restart"

    return next_state


if __name__ == "__main__":
    pass
