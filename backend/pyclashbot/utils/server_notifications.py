"""This module reads notifications from the server and to be displayed in the gui"""

from typing import TypedDict

import requests

SERVER_NOTIFICATIONS_URL = "https://pyclashbot.app/api/notification"
TIMEOUT = 5

Notification = TypedDict(
    "Notification",
    {
        "date": str,
        "header": str,
        "body": str,
        "level": str,
    },
)


def get_latest_notification() -> Notification | None:
    """Get the latest notification from the server."""
    response = requests.get(
        SERVER_NOTIFICATIONS_URL, params={"latest": True}, timeout=TIMEOUT
    )
    if response.status_code != 200:
        return None
    # parse reponse into a notification
    notification: Notification = response.json()
    return notification


if __name__ == "__main__":
    print(get_latest_notification())
