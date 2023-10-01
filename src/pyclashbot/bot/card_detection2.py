
import numpy

from pyclashbot.memu.client import save_screenshot, screenshot



def detect_cards():
    pass

if __name__ == '__main__':
    vm_index=8
    # iar = numpy.asarray(screenshot(vm_index))

    save_screenshot(vm_index)
