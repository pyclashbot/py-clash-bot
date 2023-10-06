"""A module for uploading pastes to pastebin.com"""
from os.path import dirname, exists, isfile, join, pardir

import requests

PB_KEY_FILE = join(dirname(__file__), pardir, "__pb__")
PB_KEY = None

if exists(PB_KEY_FILE) and isfile(PB_KEY_FILE):
    with open(PB_KEY_FILE, "r", encoding="utf-8") as f:
        PB_KEY = f.read().strip()

del PB_KEY_FILE

PB_API_URL = "https://pastebin.com/api/api_post.php"


class PastebinKeyNotSet(Exception):
    """Raised when the pastebin key is not set"""

    def __init__(self, message):
        self.message = message
        super().__init__(message)


def upload_pastebin(name: str, text: str) -> str | None:
    """Uploads a paste to pastebin

    Args:
        name (str): The name of the paste
        text (str): The text of the paste

    Returns:
        str: The url of the paste
    """
    if PB_KEY is None:
        raise PastebinKeyNotSet("Pastebin key is not set")

    data = {
        "api_option": "paste",
        "api_user_key": "",  # empty string for guest
        "api_paste_private": "1",  # unlisted
        "api_paste_expire_date": "1M",  # 1 month
        "api_dev_key": PB_KEY,
        "api_paste_name": name,
        "api_paste_code": text,
    }

    response = requests.post(PB_API_URL, data, timeout=10)

    return response.text if response.ok else None
