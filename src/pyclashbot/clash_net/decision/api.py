"""Functions to interact with the ClashNet API."""

from __future__ import annotations

import json
from typing import IO, TYPE_CHECKING, Callable, Literal

import requests

if TYPE_CHECKING:
    from requests.models import Response

API_URL = "https://clashnet.pyclashbot.app/api/v1/decision"

RequestMethod = Literal["GET", "POST"]


REQUEST_METHODS: dict[RequestMethod, Callable[..., requests.Response]] = {
    "GET": requests.get,
    "POST": requests.post,
}


Endpoint = Literal["/fight"]


def make_request(
    endpoint: Endpoint,
    method: RequestMethod,
    token: str,
    payload: str | None = None,
    files: dict[str, IO[bytes]] | None = None,
) -> Response:
    """Make a request to the ClashNet API.

    Args:
    ----
        endpoint (Endpoint): The endpoint to make the request to.
        method (RequestMethod): The HTTP method to use.
        token (str): The API token to use.
        payload (str, optional): The payload to send. Defaults to None.
        files (dict[str, IO[bytes]], optional): The files to send. Defaults to None.

    Returns:
    -------
        Response: The response from the API.

    """
    headers = {"Authorization": f"Bearer {token}"}

    kwargs = {
        "url": f"{API_URL}/{endpoint}",
        "headers": headers,
    }

    if payload is not None:
        kwargs["json"] = json.dumps(payload)

    if files is not None:
        kwargs["files"] = files

    return REQUEST_METHODS[method](**kwargs)
