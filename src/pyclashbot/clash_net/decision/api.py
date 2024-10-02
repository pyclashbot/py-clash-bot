"""Functions to interact with the ClashNet API."""

import asyncio
import json

import cv2
import numpy as np
import websockets
from clashnetlib.implements.fight_decision_maker import FightDecision

CLASHNET_API_URL = "ws://localhost:5001"

async def get_api_decision_async(image: np.ndarray) -> FightDecision:
    """Send an image to the ClashNet API and returns the fight decision.

    Args:
        image (np.ndarray): The image to be sent to the API.

    Returns:
        FightDecision: The decision returned by the API.

    """
    async with websockets.connect(CLASHNET_API_URL) as websocket:
        _, im_arr = cv2.imencode(".png", image)
        image_data = im_arr.tobytes()

        await websocket.send(image_data)

        response = await websocket.recv()

        response_json = json.loads(response)

        return FightDecision(response_json)



def get_api_decision(image: np.ndarray) -> FightDecision:
    """Send an image to the ClashNet API and returns the fight decision.

    Args:
        image (np.ndarray): The image to be sent to the API.

    Returns:
        FightDecision: The decision returned by the API.

    """
    return asyncio.run(get_api_decision_async(image))
