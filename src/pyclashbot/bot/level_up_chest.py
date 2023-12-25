import numpy
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import screenshot


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
    print(check_for_level_up_chest(vm_index))
