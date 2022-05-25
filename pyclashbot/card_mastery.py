import time
from pyclashbot.client import click, screenshot
from pyclashbot.image_rec import check_for_location, find_references, get_first_location
from pyclashbot.upgrade import confirm_upgrade_arrow


# def check_if_has_mastery_rewards():
#     references = [
#         "0.png",
#         "1.png",
#         "2.png",
#         "3.png",
#         "4.png",
#         "5.png",
#         "6.png",
#         "7.png",
#         "8.png",
#         "9.png",
#         "10.png",
#         "11.png",
#         "12.png",
#         "13.png",
#         "14.png",
#         "15.png",
#         "16.png",
#         "17.png",
#         "18.png",
#         "19.png",
#         "20.png",
#         "31.png",
#         "32.png",
#         "33.png",
#         "34.png",
#         "35.png",
#         "36.png",
#     ]

#     region = [0, 0, 500, 700]
#     locations = find_references(
#         screenshot=screenshot(region),
#         folder="card_mastery_reward_icon",
#         names=references,
#         tolerance=0.97
#     )
#     return check_for_location(locations)

def collect_mastery_rewards(logger):
    logger.log("Collecting mastery rewards")
    click(354,507)
    time.sleep(0.2)
    click(99,224)
    time.sleep(0.2)
    
    coords=check_if_has_mastery_rewards()
    if coords is not None:
        click(coords[1],coords[0])
        click(10,90,interval=1,clicks=5)
        
    
def check_if_has_mastery_rewards():
    references = [
        "0.png",
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
    ]

    region = [0, 0, 500, 700]
    locations = find_references(
        screenshot=screenshot(region),
        folder="claim_mastery_reward",
        names=references,
        tolerance=0.97
    )
    return get_first_location(locations)
