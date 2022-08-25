import unittest
from os.path import dirname, join
from urllib.error import HTTPError

from pyclashbot.auto_update import (download_from_url, get_asset_info,
                                    remove_previous_downloads)

# the url to test github api and downloading features
api_url = "https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest"


class AutoUpdateTest(unittest.TestCase):
    def test_github_api(self):
        asset_info = get_asset_info(api_url)
        download_url = asset_info['browser_download_url']
        file_name = asset_info['name']
        self.assertTrue(
            download_url is not None and file_name is not None and file_name.endswith("msi"))

    def test_download_from_url(self):
        asset_info = get_asset_info(api_url)
        download_url = asset_info['browser_download_url']
        file_name = asset_info['name']
        cache_dir = join(dirname(__file__), 'assets')
        try:
            installed = download_from_url(download_url, cache_dir, file_name)
            remove_previous_downloads(cache_dir)
            self.assertTrue(installed)
        except HTTPError as err:
            if err.code == 503:  # Handle when egress limit for github api is reached
                print("Egress limit reached, cannot test download_from_url.")
            else:
                raise  # Raise uncaught http errors


if __name__ == '__main__':
    unittest.main()
