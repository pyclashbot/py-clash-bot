from os import system
from os.path import join
from tempfile import TemporaryDirectory
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


def download_from_url(url, output_path):
    """download a file from a url to an output path with progress bar

    Args:
        url (str): download url
        output_path (Union[str,bytes]): path to download file to
    """
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urlretrieve(url, filename=output_path, reporthook=t.update_to)


def get_asset_info(api_url) -> dict[str, str]:
    """get infromation from github release assset

    Args:
        api_url (str): url to make api request

    Returns:
        dict[str,str]: asset information
    """
    response = get(api_url)
    asset = response.json()['assets'][0]
    return asset


def install_latest_release():
    """install the latest release from github
    """
    api_url = "https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest"
    asset_info = get_asset_info(api_url)
    download_url = asset_info['browser_download_url']
    name = asset_info['name']

    with TemporaryDirectory() as dirpath:
        temp_download_path = join(dirpath, name)
        download_from_url(download_url, temp_download_path)
        msi_install = f"msiexec.exe /i {temp_download_path} /passive"
        system(msi_install)


if __name__ == '__main__':
    install_latest_release()
