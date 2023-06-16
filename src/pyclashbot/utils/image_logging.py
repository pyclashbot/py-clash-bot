import os

from pyclashbot.memu.client import screenshot

MAX_FILE_COUNT = 100


# method to get this file location
def get_image_log_directory():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "image_log")


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


# method to parse the name of the image so it can be saved
def parse_name_for_image(name):
    return_string = ""
    for char in name:
        if char != ":":
            return_string = return_string + char
        else:
            return_string = return_string + "_"
    return return_string


# method to save the current screen image to the log
def save_this_screen_image_to_log(logger):
    name = logger.calc_time_since_start()
    name = parse_name_for_image(name)
    print("saving image with name ", name)
    save_image(image=screenshot(), name=name)
    if count_files_in_directory() > MAX_FILE_COUNT:
        delete_oldest_file_in_directory()


# method to delete the oldest file in a directory
def delete_oldest_file_in_directory():
    directory = get_image_log_directory()
    oldest_file = None
    oldest_file_time = None
    for file in os.listdir(directory):
        file_time = os.path.getmtime(os.path.join(directory, file))
        if oldest_file_time is None or file_time < oldest_file_time:
            oldest_file = file
            oldest_file_time = file_time
    if oldest_file is not None:
        print("Removing ", oldest_file)
        os.remove(os.path.join(directory, oldest_file))


# method to count the amount of files in a directory
def count_files_in_directory():
    directory = get_image_log_directory()
    count = 0
    for _ in os.listdir(directory):
        count = count + 1
    return count
