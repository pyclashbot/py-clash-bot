import time

import numpy
from pyclashbot.client import click, screenshot
from pyclashbot.image_rec import check_for_location, find_references, get_first_location, pixel_is_equal
from pyclashbot.upgrade import confirm_upgrade_arrow





def collect_mastery_rewards(logger):
    logger.log("Opening card mastery tab.")
    time.sleep(0.5)
    click(356,504)
    logger.log("Clicking first card with mastery completion.")
    time.sleep(0.5)
    click(102,216)
    logger.log("Clicking first card's rewards")
    time.sleep(0.5)
    click(90,353)
    click(90,440)
    click(90,520)

    logger.log("Returning to card page.")
    click(20,379,clicks=12,interval=0.7)
    if check_if_has_mastery_rewards():
        collect_mastery_rewards(logger)
    
    
        
    
def check_if_has_mastery_rewards():
    n=10
    button_exists=False
    while n>0:
        n=n-1
        if mastery_reward_button():
            button_exists=True
        time.sleep(0.2)

    return button_exists
    
    
def mastery_reward_button():
    iar=numpy.asarray(screenshot())
    pix1=iar[498][336]
    pix2=iar[512][337]
    pix3=iar[515][372]
       
    sent1=[255,200,80]
    sent2=[255,188,42]
    
    if (pixel_is_equal(pix1,sent1,tol=15))or(pixel_is_equal(pix2,sent1,tol=15))or(pixel_is_equal(pix3,sent1,tol=15))or(pixel_is_equal(pix1,sent2,tol=15))or(pixel_is_equal(pix2,sent2,tol=15))or(pixel_is_equal(pix3,sent2,tol=15)):
        return True
    return False