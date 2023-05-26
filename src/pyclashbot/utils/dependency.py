""" dependency.py
    This file contains the functions to install dependencies.

    Martin Miglio 2022
"""


from os import environ, listdir, makedirs, pathsep, remove
from os.path import exists, expandvars, getsize, join, normpath
from socket import gaierror
from subprocess import call
from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKey, QueryValueEx

from requests import get
from requests.exceptions import ConnectionError as RequestsConnectionError

MODULE_NAME = "py-clash-bot"

top_level = join(expandvars("%appdata%"), MODULE_NAME)

# region Common


def get_download_size(url: str) -> int | None:
    """gets the size of a download

    Args:
        url (str): url of item to download

    Returns:
        int: size of download in bytes
    """
    r = get(url, headers=None, stream=True, timeout=10)
    return int(r.headers.get("Content-Length", "0")) or None


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
    # if file doesnt exist or has a different size that the one on the server
    file_path = join(output_dir, file_name)
    download_size = get_download_size(url)
    if not exists(file_path) or download_size != getsize(file_path):
        try:
            print(f"Downloading {file_name} from {url} ({download_size} bytes)")
            r = get(url, headers=None, stream=True, allow_redirects=True, timeout=10)
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded {file_name} to {file_path}")
            return file_path
        except (RequestsConnectionError, gaierror):
            print(f"Connection error while trying to download {url} to {file_path}")
            return None
    print(f"File already downloaded from {url}.")
    return file_path


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
    try:
        print(f"Running installer {path}, please follow the installation prompts.")
        return call(path, shell=False) == 0
    except FileNotFoundError:
        print(f"Installer {path} not found.")
        return False
    except OSError:
        print(f"Installer {path} is corrupt or inaccessible.")
        return False


# endregion


# region MEmu


def get_memu_link() -> list[str] | None:
    """retrieves the link to the latest memu download

    Returns:
        list[str] | None: returns a a list of strings as [url, name of file] or None if not found
    """
    return [
        r"https://dl.memuplay.com/download/MEmu-setup-abroad-sdk.exe",
        "MEmu-setup-abroad-sdk.exe",
    ]


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


def install_memu() -> None:
    """installs memu"""
    memu_link = get_memu_link()
    if memu_link is not None:
        # delete old memu installers if they exist
        for file in listdir(make_cache()):
            if file.startswith("MEmu-setup-abroad-sdk"):
                remove(join(make_cache(), file))
        memu_installer_path = download_from_url(
            memu_link[0], make_cache(), memu_link[1]
        )
        if memu_installer_path is not None:
            run_installer(memu_installer_path)


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


def setup_memu() -> str:
    """define the environmental variables related to memu, install memu if neccessary"""
    # install memu if not found
    if not check_memu():
        install_memu()
        setup_memu()

    # get memu path
    memu_path = get_memu_path()

    # setup environment variables
    environ["MEMU_PATH"] = memu_path

    # add memuc to path
    memuc_path = join(memu_path, "memuc.exe")
    environ["PATH"] += pathsep + memuc_path

    # return the path to the memuconsole executable
    return join(memu_path, "MemuConsole.exe")


# endregion
if __name__ == "__main__":
    memu_path_s = setup_memu()
    print(f"MEmu path: {memu_path_s}")
