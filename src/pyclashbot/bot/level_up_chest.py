
import numpy
from pyclashbot.memu.client import screenshot

def check_for_level_up_chest(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[9][9],
        iar[9][22],
        iar[12][16],
        iar[23][16],
    ]

    for i,p in enumerate(pixels):
        print(p)


def collect_bannerbox_chest():


    pass


if __name__ == '__main__':
    vm_index=11
    check_for_level_up_chest(vm_index)
