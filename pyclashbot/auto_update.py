import sys
from glob import iglob
from os import makedirs, remove, environ
from subprocess import call
from os.path import dirname, exists, join
from urllib.request import urlretrieve

from requests import get
from tqdm import tqdm


class DownloadProgressBar(tqdm):
    """a class to display a download progress bar

    Args:
        tqdm (_type_): _description_
    """

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_from_url(url, cache_dir, file_name):
    """download a file from a url to an output path with progress bar

    Args:
        url (str): download url
        output_path (Union[str,bytes]): path to download file to
    """
    if not exists(join(cache_dir, file_name)):
        print(f'Latest version to install: {file_name}')
        remove_previous_downloads(cache_dir)
        with DownloadProgressBar(
                unit='B',
                unit_scale=True,
                miniters=1,
                desc=url.split('/')[-1]) as t:
            urlretrieve(
                url,
                filename=join(cache_dir, file_name),
                reporthook=t.update_to
            )
        return True
    return False


def remove_previous_downloads(cache_dir):
    """remove previous downloads from cache dir

    Args:
        cache_dir (str): cache director
    """
    for previous_install in iglob(join(cache_dir, '*.msi')):
        remove(previous_install)


def get_asset_info(api_url) -> dict[str, str]:
    """get infromation from github release assset

    Args:
        api_url (str): url to make api request

    Returns:
        dict[str,str]: asset information
    """
    response = get(api_url)
    return response.json()['assets'][0]


def install_msi(cache_dir, file_name):
    """install msi from directory and file name

    Args:
        cache_dir (str): cache directory
        file_name (str): file name

    Returns:
        bool: Whether or not install finished
    """
    try:
        print(f"Installing latest version: {file_name}")
        print("Program will exit after update. Please restart to continue.")
        msi_exec_path = join(environ['WINDIR'], 'SYSTEM32', 'msiexec.exe')
        install_call = f"{msi_exec_path} /i {join(cache_dir,file_name)} /passive"
        return 0 == call(install_call, shell=False)
    finally:
        return False


def make_cache():
    """get cache directory. make one if necessary.

    Returns:
        str: cache directory
    """
    cache_dir = join(dirname(__file__), 'cache')
    if not exists(cache_dir):
        makedirs(cache_dir)
    return cache_dir


def install_latest_release():
    """install the latest release from github

    Returns:
        bool: Whether or not new update was installed.
    """
    # if running in a frozen executable
    if getattr(sys, "frozen", False):
        print('Checking for new version to install.')

        # make api request to github to get information about latest asset
        api_url = "https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest"
        asset_info = get_asset_info(api_url)
        download_url = asset_info['browser_download_url']
        file_name = asset_info['name']

        # download latest asset to cache (create dir if necessary)
        cache_dir = make_cache()
        if download_from_url(download_url, cache_dir, file_name):
            return install_msi(cache_dir, file_name)
        else:
            print('Already latest version, continuing.')
            return False

    print('Not running from cx_freeze install, cannot auto update.')
    print('Try running \'pip install --force-reinstall --upgrade py-clash-bot\'.')
    return False


if __name__ == '__main__':
    install_latest_release()
