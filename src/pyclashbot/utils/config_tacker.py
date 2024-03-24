import time
import os
import datetime


def get_appdata_dir():
    return os.environ.get("APPDATA")


top_folder_dir = os.path.join(get_appdata_dir(), "py-clash-bot")
config_folder_dir = os.path.join(top_folder_dir, "config")
config_file_dir = os.path.join(config_folder_dir, "config.txt")


def folder_exists(folder_path):
    return os.path.exists(folder_path) and os.path.isdir(folder_path)


def file_exists(file_path):
    return os.path.exists(file_path) and os.path.isfile(file_path)


def create_txt_file(file_path):
    with open(file_path, "w") as f:
        pass  # Creating an empty file


def append_to_txt_file(file_path, content):
    with open(file_path, "a") as f:
        f.write(content + "\n")  # Adding content to the end of the file


def read_txt_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


def convert_time_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def set_time_of_last_config(time_to_set = time.time()):
    # delete config file
    if file_exists(config_file_dir):
        os.remove(config_file_dir)

    # create new config file
    create_txt_file(config_file_dir)

    # append time to config file
    append_to_txt_file(config_file_dir, str(time.time()))


def file_setup():
    if not folder_exists(top_folder_dir):
        print(f"Made pyclashbot folder at: {top_folder_dir}")
        os.mkdir(top_folder_dir)

    if not folder_exists(config_folder_dir):
        print(f"Made config folder at: {config_folder_dir}")
        os.mkdir(config_folder_dir)

    if not file_exists(config_file_dir):
        print(f"Made config file at: {config_file_dir}")
        create_txt_file(config_file_dir)


def get_time_since_last_config():
    set_time = read_txt_file(config_file_dir)
    if set_time == "":
        return 1000000000
    return time.time() - float(set_time)


file_setup()
