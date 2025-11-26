"""Webhook utility for sending deck screenshots and data to external endpoints."""

import io
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

# Webhook URL configuration
# Set this to your webhook URL to automatically send deck screenshots when captured
# Leave empty or None to disable webhook functionality
DECK_SCREENSHOT_WEBHOOK_URL: str | None = None

# Example:
# DECK_SCREENSHOT_WEBHOOK_URL = "https://your-webhook-url.com/api/deck-screenshots"


def send_image_to_webhook(
    image_data: bytes,
    webhook_url: str,
    filename: str = "deck_screenshot.png",
    additional_data: dict[str, Any] | None = None,
    timeout: int = 10,
) -> bool:
    """Send an image to a webhook endpoint using multipart/form-data.

    Args:
        image_data: Image bytes (PNG format)
        webhook_url: Webhook endpoint URL
        filename: Filename for the image
        additional_data: Optional dictionary of additional fields to send
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    if not webhook_url or not webhook_url.strip():
        return False

    try:
        # Parse URL to validate it
        parsed = urlparse(webhook_url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Create multipart/form-data request
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        crlf = b"\r\n"
        
        # Build multipart body parts
        body_parts = []
        
        # Add image file
        body_parts.append(f"--{boundary}".encode("utf-8"))
        body_parts.append(
            f'Content-Disposition: form-data; name="image"; filename="{filename}"'.encode("utf-8")
        )
        body_parts.append(b"Content-Type: image/png")
        body_parts.append(b"")
        body_parts.append(image_data)  # Binary image data
        
        # Add additional data fields if provided
        if additional_data:
            for key, value in additional_data.items():
                body_parts.append(f"--{boundary}".encode("utf-8"))
                body_parts.append(f'Content-Disposition: form-data; name="{key}"'.encode("utf-8"))
                body_parts.append(b"")
                body_parts.append(str(value).encode("utf-8"))
        
        body_parts.append(f"--{boundary}--".encode("utf-8"))
        
        # Join all parts with CRLF
        final_body = crlf.join(body_parts)

        # Create request
        request = Request(webhook_url, data=final_body)
        request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        request.add_header("Content-Length", str(len(final_body)))

        # Send request
        with urlopen(request, timeout=timeout) as response:
            # Check if status code indicates success (200-299)
            if 200 <= response.getcode() < 300:
                return True
            return False

    except (HTTPError, URLError, ValueError, Exception) as e:
        # Silently fail - don't interrupt bot operation
        return False


def send_json_to_webhook(
    data: dict[str, Any],
    webhook_url: str,
    timeout: int = 10,
) -> bool:
    """Send JSON data to a webhook endpoint.

    Args:
        data: Dictionary of data to send as JSON
        webhook_url: Webhook endpoint URL
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    if not webhook_url or not webhook_url.strip():
        return False

    try:
        # Parse URL to validate it
        parsed = urlparse(webhook_url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Create JSON request
        json_data = json.dumps(data).encode("utf-8")

        request = Request(webhook_url, data=json_data)
        request.add_header("Content-Type", "application/json")
        request.add_header("Content-Length", str(len(json_data)))

        # Send request
        with urlopen(request, timeout=timeout) as response:
            # Check if status code indicates success (200-299)
            if 200 <= response.getcode() < 300:
                return True
            return False

    except (HTTPError, URLError, ValueError, Exception) as e:
        # Silently fail - don't interrupt bot operation
        return False


def send_deck_screenshot_webhook(
    image_data: bytes,
    webhook_url: str,
    timestamp: str | None = None,
    play_coord: tuple[int, int] | None = None,
    card_index: int | None = None,
) -> bool:
    """Send deck screenshot to webhook with optional metadata.

    Args:
        image_data: Image bytes (PNG format)
        webhook_url: Webhook endpoint URL
        timestamp: Optional timestamp string
        play_coord: Optional play coordinates tuple (x, y)
        card_index: Optional card index

    Returns:
        True if successful, False otherwise
    """
    additional_data = {}
    if timestamp:
        additional_data["timestamp"] = timestamp
    if play_coord:
        additional_data["play_coord_x"] = play_coord[0]
        additional_data["play_coord_y"] = play_coord[1]
    if card_index is not None:
        additional_data["card_index"] = card_index

    filename = f"deck_{timestamp or 'screenshot'}.png"
    return send_image_to_webhook(image_data, webhook_url, filename, additional_data)

