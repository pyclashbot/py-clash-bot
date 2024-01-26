import time

import random
import pygame
from pygame.locals import QUIT
from pyclashbot.detection.image_rec import (
    make_reference_image_list,
    get_file_count,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.detection.image_rec import screenshot

DOT_RADIUS = 5
ENEMY_TROOP_IMAGE_REC_TOLERANCE=0.98

def flip_all_coords(locations):
    new_coord_list = []

    for location in locations:
        if location is None:
            continue
        new_coord = [location[1], location[0]]
        new_coord_list.append(new_coord)

    return new_coord_list


def draw_icons(screen, active_dots):
    screen.fill((230, 230, 230))  # Clear the screen
    for dot in active_dots:
        pygame.draw.circle(screen, dot["color"], dot["location"], DOT_RADIUS)

    pygame.display.flip()  # Update the display


def update_dots(active_dots):
    # Update the lifespan of each active dot
    for dot in active_dots:
        dot["lifespan"] -= 1

    # Remove dots whose lifespan has expired
    active_dots[:] = [dot for dot in active_dots if dot["lifespan"] > 0]


def add_dot(active_dots, location, lifespan, color):
    # Add a new dot with specified location, lifespan, and color
    active_dots.append({"location": location, "lifespan": lifespan, "color": color})


def find_enemy_troops(vm_index):
    folder = "enemy_troop_icon"

    names = make_reference_image_list(get_file_count(folder))
    locations: list[list[int] | None] = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=ENEMY_TROOP_IMAGE_REC_TOLERANCE,
    )

    if get_first_location(locations) is None:
        return None

    return flip_all_coords(locations)


def remove_trash_coords(locations):
    if locations is None:
        return locations

    bad_coords = [
        [276, 114],
        [231, 66],
        [197, 15],
        [69, 538],
        [39, 43],
        [349, 497],
        [153, 622],
        [133, 14],
        [100, 114],
    ]

    tolerance_range = 15
    # Use list comprehension to create a new list with valid coordinates
    filtered_locations = [
        location
        for location in locations
        if not any(
            abs(location[0] - bad_coord[0]) < tolerance_range
            and abs(location[1] - bad_coord[1]) < tolerance_range
            for bad_coord in bad_coords
        )
    ]

    return filtered_locations


def classify_pixel(pixel):
    blue_colors = [
        (10, 85, 163),
        (51, 127, 199),
        (12, 45, 92),
    ]

    red_colors = [
        (93, 13, 13),
        (173, 29, 29),
        (204, 35, 35),
    ]

    tolerance = 50

    for color in blue_colors:
        if pixel_is_equal(pixel, color, tolerance):
            return "blue"

    for color in red_colors:
        if pixel_is_equal(pixel, color, tolerance):
            return "red"

    return "unknown"


def classify_coordinate(iar, coord):
    pixels = []

    x_range = 6  # pixels
    y_range = 6  # pixels

    left_side_range = x_range / 2
    bottom_size_range = y_range / 2

    for x in range(int(coord[0] - left_side_range), int(coord[0] + left_side_range)):
        for y in range(
            int(coord[1] - bottom_size_range), int(coord[1] + bottom_size_range)
        ):
            pixel = iar[y][x]
            pixels.append(pixel)

    colors = []
    for pixel in pixels:
        colors.append(classify_pixel(pixel))

    red_color_count = 0
    blue_color_count = 0

    for color in colors:
        if color == "red":
            red_color_count += 1
        elif color == "blue":
            blue_color_count += 1

    # print(f"Found {blue_color_count} blues / {len(colors)}")
    # print(f"Found {red_color_count} reds / {len(colors)}")
    if red_color_count * 0.7 > blue_color_count:
        return "red"

    return "blue"


def classify_locations(vm_index, locations):
    import numpy

    iar = numpy.asarray(screenshot(vm_index))

    if locations is None:
        return None

    classified_locations = []
    for location in locations:
        color = classify_coordinate(iar, coord=(location[0], location[1]))
        classified_locations.append([location[0], location[1], color])

    return classified_locations


def troop_visualizer_thread(vm_index):
    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 419, 633
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Enemy Troop Detection")

    # Red dot radius

    # List to store active dots with their remaining lifespan
    active_dots = []

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        locations = remove_trash_coords(find_enemy_troops(vm_index))
        locations_with_color = classify_locations(vm_index, locations)
        if locations is not None:
            # print(locations_with_color)
            for location_with_color in locations_with_color:
                # if color is blue, dont draw
                # if location_with_color[2] == "blue":
                #     continue
                print(location_with_color)
                # print(choose_play_side(logger,vm_index))
                add_dot(
                    active_dots,
                    location_with_color[:2],  # Use [:2] to get only the location
                    lifespan=20,
                    color=location_with_color[2],
                )  # Set lifespan to 60 frames (1 second)

        update_dots(active_dots)
        draw_icons(screen, active_dots)

        clock.tick(60)  # Limit frames per second


def remove_blue_locations(locations):
    if locations is None:
        return None

    filtered_locations = []
    for location in locations:
        if location[2] == "blue":
            continue
        filtered_locations.append(location)

    return filtered_locations


def choose_play_side(logger, vm_index):
    timeout = 1.33 # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        locations = remove_trash_coords(find_enemy_troops(vm_index))
        # locations = classify_locations(vm_index, locations)
        # locations = remove_blue_locations(locations)

    # middle x coord
    middle_x = 209

    if locations is None:
        logger.change_status(f"No troops detected... choosing random side {str(time.time() - start_time)[:5]}s")
        return random.choice(["left", "right"])

    left_count = 0
    right_count = 0

    for location in locations:
        if location[0] < middle_x:
            left_count += 1
        else:
            right_count += 1

    # if locations count is 3 or below, just choose a random side
    if len(locations) < 3:
        logger.change_status(f"No troops detected... choosing random side {str(time.time() - start_time)[:5]}s")
        return random.choice(["left", "right"])

    if left_count > right_count:
        logger.change_status(f"Choosing left side: {left_count}L | {right_count}R {str(time.time() - start_time)[:5]}s")
        return "left"

    logger.change_status(f"Choosing right side: {left_count}L | {right_count}R {str(time.time() - start_time)[:5]}s")
    return "right"


if __name__ == "__main__":
    troop_visualizer_thread(12)
    # from pyclashbot.utils.logger import Logger
    # while 1:
        # (choose_play_side(Logger(None,None),12))
