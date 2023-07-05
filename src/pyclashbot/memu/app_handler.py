"""
This module contains functions for handling the installation
of APKs on a virtual machine using PyMemuc.
"""


import time
from os import environ, listdir, makedirs, startfile
from os.path import exists, join

from pymemuc import PyMemuc, PyMemucError, PyMemucException

from utils.logger import Logger


pmc = PyMemuc(debug=False)

APPS = {
    "clash_royale": "com.supercell.clashroyale",
    "drony": "org.sandroproxy.drony",
}

MODULE_NAME = "pyclashbot"

apk_dir = join(environ["APPDATA"], MODULE_NAME, "apks")

# if dir doesnt exist, create it
if not exists(apk_dir):
    print("No apks found. Creating apks folder")
    makedirs(apk_dir)


class APKFile:
    """Represents an APK file"""

    def __init__(self, path: str):
        self.path = path
        self.package_id = read_package_id(path)

    def __repr__(self):
        return f"APKFile: {self.path} - {self.package_id}"


def open_apks_folder():
    """Opens the apks folder in the file explorer"""
    startfile(apk_dir)


def read_apks(logger: Logger) -> list[APKFile]:
    """Reads the appdata pyclashbot/apks/ folder and returns a list of apks"""
    files = listdir(apk_dir)
    apks = [APKFile(join(apk_dir, file)) for file in files if file.endswith(".apk")]
    logger.change_status(f"Found {len(apks)} apks in {apk_dir}")
    for apk in apks:
        logger.change_status(repr(apk))
    return apks


class APKParserError(Exception):
    """Raised when an error occurs parsing an APK"""

    def __init__(self, message):
        self.message = message


def read_package_id(apk_path: str):
    """Reads the package id from the given apk"""
    # with APK.from_file(apk_path) as apk:
    #     apk.parse_resouce()
    #     return str(apk.get_package_name())

    return apk_path 


def install_apks(logger: Logger, vm_index: int):
    """
    Installs all apks in the appdata pyclashbot/apks/ folder
    and returns a list of installed apps
    """
    logger.change_status(f"Installing apks on VM {vm_index}")
    for apk in read_apks(logger):
        try:
            app_list = pmc.get_app_info_list_vm(vm_index=vm_index)
            if apk.package_id in app_list:
                continue
            logger.change_status(f"Installing {apk.package_id} on VM {vm_index}")
            while True:
                pmc.install_apk_vm(apk.path, vm_index)
                time.sleep(5)
                app_list = pmc.get_app_info_list_vm(vm_index=vm_index)
                if any(app.startswith(apk.package_id) for app in app_list):
                    break
            logger.change_status(f"Installed {apk} on VM {vm_index}")
        except PyMemucException as err:
            logger.change_status(f"Failed to install {apk} on VM {vm_index}")
            logger.error(f"Error: {err}")
            raise err
    logger.change_status(f"Installed all apks on VM {vm_index}")

    return pmc.get_app_info_list_vm(vm_index=vm_index)


def check_for_app_install(apk_base_name: str, logger: Logger, vm_index: int):
    """
    Checks if the given app is installed on the given VM.
    If it is not installed, raises a FileNotFoundError.
    """

    # get list of installed apps
    while True:
        try:
            installed_apps = pmc.get_app_info_list_vm(vm_index=vm_index)
            break
        except PyMemucError:
            logger.change_status(f"Waiting for VM {vm_index} to start to check for app install")
            time.sleep(1)

    found = [app for app in installed_apps if app.startswith(apk_base_name)]

    if not found:
        logger.change_status(f"{apk_base_name} is not installed. Please install it")
        raise FileNotFoundError(f"{apk_base_name} is not installed on VM {vm_index}")


def check_for_clash_royale_installed(logger: Logger, vm_index: int):
    """Checks if Clash Royale is installed on all VMs."""
    logger.change_status(f"Checking if Clash Royale is installed on VM {vm_index}")
    check_for_app_install(APPS["clash_royale"], logger, vm_index)
    logger.change_status(f"Clash Royale is installed on VM {vm_index}")

    return True


def check_for_drony_installed(logger: Logger, vm_index: int):
    """Checks if Drony is installed on all VMs."""
    logger.change_status(f"Checking if Drony is installed on VM {vm_index}")
    check_for_app_install(APPS["drony"], logger, vm_index)
    logger.change_status(f"Drony is installed on VM {vm_index}")

    return True


if __name__ == "__main__":
    test_logger = Logger()
    # read app list and package ids
    print(read_apks(test_logger))
