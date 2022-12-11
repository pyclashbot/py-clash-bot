import os
import time

from pyscreeze import screenshot


# method to get this file location
def get_image_log_directory():
    return os.path.dirname(os.path.realpath(__file__)) + "\image_log"


# method to delete all files in a given directory
def clear_image_log():
    directory = get_image_log_directory()
    for file in os.listdir(directory):
        print("Removing ", file)
        os.remove(directory + "\\" + file)


# method to save an image to a given directory
def save_image(image, name):
    directory = get_image_log_directory()
    image.save(directory + "\\" + name + ".png")


# method to save an image to the image log
def save_image_to_image_log(logger):
    save_image(image=screenshot(), name=logger.calc_time_since_start())
