

from os.path import dirname, join
import time
from matplotlib import pyplot as plt
import numpy
from PIL import Image


from pyclashbot.client import draw_picture, get_avg_coord, get_image, orientate_window, screenshot
from pyclashbot.image_rec import pixel_is_equal


def get_board_screenshot():
    #print("getting board ss")
    # screenshot board
    region = [70, 130, 280, 380]
    ss = screenshot(region)

    # open black images
    folder = "draw_images"

    name = "black_tower_cover.png"
    cover_tower_image = get_image(name=name, folder=folder)

    name = "black_king_tower_cover.png"
    cover_king_tower_image = get_image(name=name, folder=folder)

    name = "cover_river_image.png"
    cover_river_image = get_image(name=name, folder=folder)

    # define coords for pasting
    tower_1_paste_coords = (29, 25)
    tower_2_paste_coords = (205, 25)
    king_tower_paste_coords = (80, 0)
    river_paste_coords = (0, 181)

    # paste images in their spots
    ss.paste(im=cover_tower_image, box=tower_1_paste_coords)
    ss.paste(im=cover_tower_image, box=tower_2_paste_coords)
    ss.paste(im=cover_king_tower_image, box=king_tower_paste_coords)
    ss.paste(im=cover_river_image, box=river_paste_coords)

    return ss


def get_red_pix_from_ss(ss):
    #print("getting red pix")
    # region=[70,130,280,380]
    # width=280
    # height=380

    red_pix_list = []
    sentinel_1 = [168, 50, 50]
    sentinel_2 = [235, 43, 43]
    sentinel_3 = [255, 55, 68]
    sentinel_4 = [196, 37, 37]

    iar = numpy.asarray(ss)
    x_index = 279
    while x_index > 0:
        y_index = 379
        while y_index > 0:
            current_pix = iar[y_index][x_index]
            current_coord = [x_index, y_index]

            # print(current_coord)
            # print(current_pix)

            if (pixel_is_equal(current_pix, sentinel_1, tol=20)) or (pixel_is_equal(current_pix, sentinel_2, tol=20)) or (pixel_is_equal(current_pix, sentinel_3, tol=20)) or (pixel_is_equal(current_pix, sentinel_4, tol=20)):
                #print("Found positive pixel")
                if red_pix_list == []:
                    red_pix_list = [current_coord]
                else:
                    red_pix_list.append(current_coord)

            y_index = y_index-1
        x_index = x_index-1

    return red_pix_list


def show_red_pix(pix_list):
    #print("Showing pixels")
    draw_picture(pix_list)


def find_enemy_2():
    # use board scanner methods to find red coords of red pixels and find the avg coord
    red_pix_list = get_red_pix_from_ss(get_board_screenshot())
    if red_pix_list is not None:
        avg_coord = get_avg_coord(red_pix_list)
        if (avg_coord is not None):
            # adjust the coordinates so they're usable for the fight bot
            avg_coord = [avg_coord[0]+70, avg_coord[1]+130]
            return avg_coord
    return None

# orientate_window()
# time.sleep(1)
# region=[70,130,280,380]
# iar=numpy.asarray(screenshot(region))
# plt.imshow(iar)
# plt.show()
