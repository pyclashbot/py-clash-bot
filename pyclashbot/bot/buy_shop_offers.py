import time

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_shop_page_from_clash_main,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)

from pyclashbot.utils.logger import Logger

SHOP_BUY_TIMEOUT = 35


def buy_shop_offers_state(
    emulator,
    logger: Logger,
    gold_buy_toggle: bool,
    free_offers_toggle: bool,
    next_state: str,
):
    print("Entering buy_shop_offers_state()")
    print(f"gold_buy_toggle: {gold_buy_toggle}")
    print(f"free_offers_toggle: {free_offers_toggle}")

    # if not on clash main, return False
    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status(
            "Not on clash main to being buying offers. Returning restart",
        )
        return "restart"

    # run the main buying function
    if (
        buy_shop_offers_main(
            emulator,
            logger,
            gold_buy_toggle,
            free_offers_toggle,
        )
        is not True
    ):
        logger.change_status("Failed to buy offers. Returning restart")
        return "restart"

    time.sleep(3)

    # if not on clash main, return False
    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status("Not on clash main after buying offers. Returning restart")
        return "restart"

    return next_state


def scroll_all_the_way_in_shop_page(emulator, direction):
    """Method for scrolling down even faster when interacting with a
    scrollable menu using the left side of the screen
    """
    for _ in range(13):
        if direction == "up":
            emulator.swipe(66, 60, 66, 400)
        else:
            emulator.swipe(66, 400, 66, 60)

    # click deadspace to stop the scroll


def scroll_slowly_in_shop_page(emulator, direction):
    """Method for scrolling down even faster when interacting with a
    scrollable menu using the left side of the screen
    """
    if direction == "down":
        emulator.swipe(66, 400, 66, 200)
    else:
        emulator.swipe(66, 200, 66, 400)

    # click deadspace to stop the scroll
    emulator.click(10, 200)


def buy_shop_offers_main(
    emulator,
    logger: Logger,
    gold_buy_toggle: bool,
    free_offers_toggle: bool,
) -> bool:
    # get to shop page
    logger.change_status("Getting to shop page to buy offers")
    if get_to_shop_page_from_clash_main(emulator, logger) is False:
        logger.change_status("Failed to get to shop page to buy offers")
        return False

    # scroll all the way to the top
    scroll_all_the_way_in_shop_page(emulator, direction="down")

    # scroll incrementally while searching for rewards, clicking and buying any rewards found
    purchase_total = 0
    start_time = time.time()
    done_buying = False
    logger.change_status("Starting to buy offers")
    while 1 and done_buying is False:
        if time.time() - start_time > SHOP_BUY_TIMEOUT:
            break

        # scroll a little
        logger.change_status("Searching for offers to buy")
        print("Time taken in shop: ", str(time.time() - start_time)[:5])
        scroll_slowly_in_shop_page(emulator, direction="up")
        time.sleep(1)

        if gold_buy_toggle or free_offers_toggle:
            while (
                buy_offers_from_this_shop_page(
                    emulator,
                    logger,
                    gold_buy_toggle,
                    free_offers_toggle,
                )
                is True
                and done_buying is False
            ):
                purchase_total += 1
                logger.change_status("Bought an offer from the shop!")
                start_time = time.time()

                # if only free offers are toggled, AND purchase total is 1, then it's done
                if free_offers_toggle and not gold_buy_toggle and purchase_total == 1:
                    print("only free offers toggles and purchase total is 1, breaking")
                    done_buying = True
                    break

                # if both modes are toggled, and total is 6, break
                if gold_buy_toggle and free_offers_toggle and purchase_total == 6:
                    print("both modes toggled and purchase total is 6, breaking")
                    done_buying = True
                    break

                # if only gold offers are toggled, and purchase total is 6, break
                if gold_buy_toggle and not free_offers_toggle and purchase_total == 5:
                    print("only gold offers toggled and purchase total is 6, breaking")
                    done_buying = True
                    break

    logger.change_status("Done buying offers. Returning to clash main")

    # get to clash main from shop page
    emulator.click(245, 596)
    time.sleep(4)

    return True


def search_for_free_purchases(emulator):
    """Method to find the free offer icon image in the shop pages"""
    folder_name = "free_offer_icon"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        emulator.screenshot(),
        folder_name,
        names,
        0.9,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def search_for_gold_purchases(emulator):
    """Method to find the offers for gold icon image in the shop pages"""
    folder_name = "offers_for_gold"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        emulator.screenshot(),
        folder_name,
        names,
        0.9,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def buy_offers_from_this_shop_page(
    emulator,
    logger: Logger,
    gold_buy_toggle,
    free_offers_toggle,
):
    coord = None

    if gold_buy_toggle:
        coord = search_for_gold_purchases(emulator)

    # if no gold purchases, find a free purchase
    if coord is None and free_offers_toggle:
        coord = search_for_free_purchases(emulator)

    # if there are no purchases at this point, return False
    if coord is None:
        return False

    # click the location of the 'cards for gold' icon
    emulator.click(coord[0], coord[1])
    time.sleep(2)

    # click the second 'buy' button
    emulator.click(200, 433)
    emulator.click(204, 394)
    logger.add_shop_offer_collection()

    # click deadspace to close this offer
    while not check_if_on_shop_page(emulator):
        emulator.click(15, 200)

    return True


def check_if_on_shop_page(emulator):
    iar = numpy.asarray(emulator.screenshot())

    pixels = [
        iar[582][19],
        iar[599][108],
        iar[595][13],
    ]
    colors = [
        [138, 103, 70],
        [143, 109, 74],
        [142, 108, 73],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True





if __name__ == "__main__":
    pass
