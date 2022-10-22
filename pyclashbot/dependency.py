""" dependency.py
    This file contains the functions to install dependencies.
    Callables:
        setup_tsrct() -> str, tesseract executable path, sets up tesseract environment variables
        setup_ahk() -> str, ahk executable path, sets up ahk environment variables
        setup_memu() -> str, memu executable path, sets up memu environment variables

    Martin Miglio 2022
"""


from os import environ, makedirs, pathsep
from os.path import exists, expandvars, join, normpath
from socket import gaierror
from subprocess import call
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryValueEx

from requests import get
from requests.exceptions import ConnectionError
from tqdm import tqdm

module_name = "py-clash-bot"

top_level = join(expandvars("%appdata%"), module_name)

# region Common


def get_dependency_dict() -> dict[str, list[str] | None]:
    """creates a dictionary of dependencies

    Returns: dict[str, list[str] | None]: a dictionary of dependencies
    """
    dependency_dict = {
        # "tesseract": get_tsrct_link(),
        "ahk": get_ahk_link(),
        "memu": get_memu_link(),
    }

    return dependency_dict


def download_from_url(url: str, output_dir: str, file_name: str) -> str | None:
    # sourcery skip: extract-method
    """Downloads a file from a url to a directory with a specified file name

    Args:
        url (str): url of item to download
        output_dir (str): directory to save file
        file_name (str): name of file to save

    Raises:
        ValueError: thrown when url does not specify an http or https endpoint

    Returns:
        str | None: returns the path to the file or None if not downloaded
    """
    if not url.lower().startswith("http"):
        raise ValueError from None
    if not exists(join(output_dir, file_name)):
        # remove_previous_downloads(cache_dir)
        try:
            r = get(url, headers=None, stream=True)
            total_size_in_bytes = int(r.headers.get("content-length", 0))
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
            with open(join(output_dir, file_name), "wb") as f:
                for data in r.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                raise ConnectionError
            return join(output_dir, file_name)
        except (ConnectionError, gaierror):
            print(
                f"Connection error while trying to download {url} to {join(output_dir, file_name)}"
            )
            return None
    print(f"File already downloaded from {url}.")
    return join(output_dir, file_name)


def make_cache() -> str:
    """creates a cache directory for downloaded installer

    Returns:
        str: the path to the cache directory
    """
    cache_dir = join(top_level, "cache")
    if not exists(cache_dir):
        makedirs(cache_dir)
    return cache_dir


def run_installer(path: str) -> bool:
    """runs a specified installer executable

    Args:
        path (str): path to installer executable

    Returns:
        bool: if install was successful
    """
    return call(path, shell=False) == 0


def install_from_dict(dependencies: dict[str, list[str] | None]) -> None:
    """installs a list of dependencies from a supplied dictionary

    Args:
        dependencies (dict[str, list[str]  |  None]): a dictioinary of dependencies names and their url
    """
    cache_dir = make_cache()
    for name, download_info in dependencies.items():
        if download_info is not None:
            file_url = download_info[0]
            file_name = download_info[1]
            print(f"Downloading {name} from {file_url} to {cache_dir}.")
            installer_path = download_from_url(file_url, cache_dir, file_name)
            if installer_path is not None:
                print(f"Executing {installer_path}")
                run_installer(installer_path)
        else:
            print(f"Download for {name} is not found.")


def install_dependencies() -> None:
    """install the defined dependencies"""
    dependency_dict = get_dependency_dict()
    install_from_dict(dependency_dict)


# endregion


# region autohotkey


def get_ahk_link() -> list[str] | None:
    """retrieves the link to the latest tesseract download

    Returns:
        list[str] | None: returns a a list of strings as [url, name of file] or None if not found
    """
    url = r"https://www.autohotkey.com/download/ahk-install.exe"
    return [url, "ahk-install.exe"]


def get_ahk_path() -> str:
    """gets the path to the ahk install directory

    Returns:
        str: path to ahk install directory
    """
    try:
        akey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AutoHotKey"
        areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        akey = OpenKey(areg, akey)
    except FileNotFoundError:
        akey = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\AutoHotKey"
        areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        akey = OpenKey(areg, akey)
    return str(normpath(QueryValueEx(akey, "DisplayIcon")[0]))


def setup_ahk() -> str:
    """sets up ahk environment variables"""
    # add ahk to path
    try:
        ahk_dir = get_ahk_path()
    except FileNotFoundError:
        install_dependencies()
        ahk_dir = get_ahk_path()
    if ahk_dir != "":
        environ["PATH"] += pathsep + ahk_dir
    return ahk_dir


def check_ahk() -> bool:
    """checks if ahk is installed

    Returns:
        bool: if ahk is installed
    """
    try:
        get_ahk_path()
        return True
    except FileNotFoundError:
        return False


# endregion


# region MEmu


def get_memu_link() -> list[str] | None:
    """retrieves the link to the latest tesseract download

    Returns:
        list[str] | None: returns a a list of strings as [url, name of file] or None if not found
    """
    url = r"https://dl.memuplay.com/download/MEmu-setup-abroad-sdk.exe"
    return [url, "MEmu-setup-abroad-sdk.exe"]


def get_memu_path() -> str:
    """locate the path of the memu directory

    Returns:
        str: the path of the memu directory
    """
    try:
        akey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MEmu"
        areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        akey = OpenKey(areg, akey)
    except FileNotFoundError:
        akey = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\MEmu"
        areg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        akey = OpenKey(areg, akey)
    return str(join(normpath(QueryValueEx(akey, "InstallLocation")[0]), "Memu"))


def setup_memu() -> str:
    """define the environmental variables related to memu, install memu if neccessary"""
    try:
        memu_path = get_memu_path()
    except FileNotFoundError:
        install_dependencies()
        memu_path = get_memu_path()
    environ["MEMU_PATH"] = memu_path

    # add memuc to path
    memuc_path = join(memu_path, "memuc.exe")
    environ["PATH"] += pathsep + memuc_path

    return join(memu_path, "MemuConsole.exe")


def check_memu() -> bool:
    """checks if memu is installed

    Returns:
        bool: if memu is installed
    """
    try:
        get_memu_path()
        return True
    except FileNotFoundError:
        return False


# endregion


if __name__ == "__main__":
    # setup dependencies
    ahk_path_s = setup_ahk()
    memu_path_s = setup_memu()

    # print the install paths
    print(f"AutoHotKey path: {ahk_path_s}")
    print(f"MEmu path: {memu_path_s}")

    # check dependencies
    print(f"AHK: {check_ahk()}")
    print(f"MEMU: {check_memu()}")
