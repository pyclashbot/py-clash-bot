
import numpy

from pyclashbot.client import screenshot


def check_if_has_level_up_rewards():
    #starts on clash main ends on clash main
    iar=numpy.asarray(screenshot())
    
    pix_list=[]
    color=[]
    
    for pix in pix_list:
        if not pixel_is_equal(pix,color): return False
    return True
    
    pass