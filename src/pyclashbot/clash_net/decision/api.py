"""Functions to interact with the ClashNet API."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Self

import cv2
import websockets
from clashnetlib.implements.fight_decision_maker import FightDecision

if TYPE_CHECKING:
    from types import TracebackType

    import numpy as np


class FightDecisionAPIAsync:
    """A class to interact with the ClashNet API as a context manager."""

    CLASHNET_API_URL = "ws://localhost:5001/ws/decision/fight"

    def __init__(self) -> None:
        """Initialize the FightDecisionAPI instance."""
        logging.debug("Initializing FightDecisionAPIAsync context manager.")
        self.websocket: websockets.WebSocketClientProtocol | None = None

    async def __aenter__(self) -> Self:
        """Establish a WebSocket connection to the ClashNet API."""
        logging.debug("Establishing WebSocket connection to ClashNet API.")
        self.websocket = await websockets.connect(self.CLASHNET_API_URL)
        logging.debug("WebSocket connection established.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and close the WebSocket connection.

        Args:
        ----
            exc_type (type[BaseException] | None): The exception type.
            exc (BaseException | None): The exception instance.
            tb (TracebackType | None): The traceback object.

        """
        if not self.websocket:
            return
        logging.debug("Closing WebSocket connection to ClashNet API.")
        await self.websocket.close()

    async def get_decision(self, image: np.ndarray) -> FightDecision:
        """Send an image to the ClashNet API and returns the fight decision.

        Args:
        ----
            image (np.ndarray): The image to be sent to the API.

        Returns:
        -------
            FightDecision: The decision returned by the API.

        """
        if not self.websocket:
            message = "WebSocket connection not established."
            raise ValueError(message)

        logging.debug("Encoding image as PNG.")
        _, im_arr = cv2.imencode(".png", image)
        image_data = im_arr.tobytes()

        logging.debug("Sending image to ClashNet API.")
        await self.websocket.send(image_data)

        logging.debug("Receiving response from ClashNet API.")
        response = await self.websocket.recv()

        response_json = json.loads(response)

        logging.debug("Response received from ClashNet API.")
        return FightDecision(response_json)


class FightDecisionAPI:
    """A class to interact with the ClashNet API synchronously through a context manager.

    Example Usage:
    ```python
    from pyclashbot.clash_net.decision.api import FightDecisionAPI

    with FightDecisionAPI() as api:
        decision = api.get_decision(image)
        print(decision)

    ```
    """

    def __init__(self) -> None:
        """Initialize the FightDecisionAPI instance."""
        self.loop = asyncio.new_event_loop()
        self.api = FightDecisionAPIAsync()

    def __enter__(self) -> Self:
        """Enter the context manager."""
        self.loop.run_until_complete(self.api.__aenter__())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the context manager."""
        self.loop.run_until_complete(self.api.__aexit__(exc_type, exc, tb))

    def get_decision(self, image: np.ndarray) -> FightDecision:
        """Get a fight decision from the ClashNet API.

        Args:
        ----
            image (np.ndarray): The image to be sent to the API.

        Returns:
        -------
            FightDecision: The decision returned by the API.

        """
        return self.loop.run_until_complete(self.api.get_decision(image))
