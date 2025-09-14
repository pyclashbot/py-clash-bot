"""Graphics API detection module for PyClashBot.

This module detects available graphics APIs on the system and provides
smart defaults for emulator configurations.
"""

import ctypes
import logging
import platform
from dataclasses import dataclass


@dataclass
class GraphicsCapabilities:
    """Container for detected graphics API capabilities."""

    directx11_available: bool = False
    directx12_available: bool = False
    vulkan_available: bool = False
    opengl_available: bool = False
    system_info: dict[str, str] = None

    def __post_init__(self):
        if self.system_info is None:
            self.system_info = {}

    @property
    def directx_available(self) -> bool:
        """Returns True if any DirectX version is available."""
        return self.directx11_available or self.directx12_available

    @property
    def available_apis(self) -> list[str]:
        """Returns a list of available graphics API names."""
        apis = []
        if self.directx_available:
            apis.append("directx")
        if self.opengl_available:
            apis.append("opengl")
        if self.vulkan_available:
            apis.append("vulkan")
        return apis

    def is_api_available(self, api_name: str) -> bool:
        """Check if a specific API is available."""
        api_name = api_name.lower()
        if api_name in ["directx", "dx"]:
            return self.directx_available
        elif api_name in ["opengl", "gl"]:
            return self.opengl_available
        elif api_name in ["vulkan", "vk", "vlcn"]:
            return self.vulkan_available
        return False


class GraphicsDetector:
    """Detects available graphics APIs using DLL loading."""

    _cached_capabilities: GraphicsCapabilities | None = None

    @classmethod
    def detect_capabilities(cls, force_refresh: bool = False) -> GraphicsCapabilities:
        """Detect available graphics APIs with caching.

        Args:
            force_refresh: If True, bypass cache and re-detect

        Returns:
            GraphicsCapabilities object with detection results
        """
        if cls._cached_capabilities is not None and not force_refresh:
            return cls._cached_capabilities

        logging.info("Detecting graphics API capabilities...")

        capabilities = GraphicsCapabilities()

        # Collect system information
        capabilities.system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
        }

        # Only perform DLL detection on Windows
        if platform.system() != "Windows":
            logging.warning(f"Graphics API detection only supported on Windows, detected: {platform.system()}")
            # On non-Windows systems, assume OpenGL is available as fallback
            capabilities.opengl_available = True
            cls._cached_capabilities = capabilities
            return capabilities

        # Detect DirectX 11
        try:
            ctypes.cdll.LoadLibrary("d3d11.dll")
            capabilities.directx11_available = True
            logging.info("DirectX 11 detected: Available")
        except OSError as e:
            capabilities.directx11_available = False
            logging.info(f"DirectX 11 detected: Not available ({e})")

        # Detect DirectX 12
        try:
            ctypes.cdll.LoadLibrary("d3d12.dll")
            capabilities.directx12_available = True
            logging.info("DirectX 12 detected: Available")
        except OSError as e:
            capabilities.directx12_available = False
            logging.info(f"DirectX 12 detected: Not available ({e})")

        # Detect Vulkan
        try:
            ctypes.cdll.LoadLibrary("vulkan-1.dll")
            capabilities.vulkan_available = True
            logging.info("Vulkan detected: Available")
        except OSError as e:
            capabilities.vulkan_available = False
            logging.info(f"Vulkan detected: Not available ({e})")

        # Detect OpenGL
        try:
            ctypes.cdll.LoadLibrary("opengl32.dll")
            capabilities.opengl_available = True
            logging.info("OpenGL detected: Available")
        except OSError as e:
            capabilities.opengl_available = False
            logging.info(f"OpenGL detected: Not available ({e})")

        # Log summary
        available_apis = capabilities.available_apis
        if available_apis:
            logging.info(f"Graphics APIs available: {', '.join(available_apis)}")
        else:
            logging.warning("No graphics APIs detected! This may cause emulator issues.")

        # Cache the results
        cls._cached_capabilities = capabilities
        return capabilities

    @classmethod
    def get_best_default_api(cls, emulator_type: str = "generic") -> str:
        """Get the best available graphics API for the given emulator type.

        Args:
            emulator_type: Type of emulator ("memu", "bluestacks", "googleplay", or "generic")

        Returns:
            String name of the best available graphics API
        """
        capabilities = cls.detect_capabilities()

        # Define priority order per emulator type
        priority_orders = {
            "memu": ["directx", "opengl", "vulkan"],
            "bluestacks": ["directx", "opengl", "vulkan"],
            "googleplay": ["directx", "vulkan", "opengl"],
            "generic": ["directx", "opengl", "vulkan"],
        }

        priority_order = priority_orders.get(emulator_type.lower(), priority_orders["generic"])

        # Find the first available API in priority order
        for api in priority_order:
            if capabilities.is_api_available(api):
                logging.info(f"Selected best graphics API for {emulator_type}: {api}")
                return api

        # Fallback if nothing is detected (shouldn't happen on Windows)
        fallback = "opengl"
        logging.warning(f"No graphics APIs detected, falling back to: {fallback}")
        return fallback

    @classmethod
    def get_available_apis_for_emulator(cls, emulator_type: str) -> list[str]:
        """Get list of available graphics APIs for a specific emulator type.

        Args:
            emulator_type: Type of emulator ("memu", "bluestacks", "googleplay")

        Returns:
            List of available API names for the emulator
        """
        capabilities = cls.detect_capabilities()

        # Define which APIs each emulator supports
        emulator_support = {
            "memu": ["directx", "opengl"],
            "bluestacks": ["directx", "opengl", "vulkan"],
            "googleplay": ["directx", "vulkan", "opengl"],
        }

        supported_apis = emulator_support.get(emulator_type.lower(), ["directx", "opengl", "vulkan"])
        available_apis = []

        for api in supported_apis:
            if capabilities.is_api_available(api):
                available_apis.append(api)

        logging.info(f"Available APIs for {emulator_type}: {available_apis}")
        return available_apis

    @classmethod
    def validate_api_selection(cls, api_name: str, emulator_type: str = "generic") -> bool:
        """Validate that a graphics API selection is available and supported.

        Args:
            api_name: Name of the graphics API to validate
            emulator_type: Type of emulator to validate against

        Returns:
            True if the API is available and supported, False otherwise
        """
        available_apis = cls.get_available_apis_for_emulator(emulator_type)
        is_valid = api_name.lower() in [api.lower() for api in available_apis]

        if not is_valid:
            logging.warning(f"Graphics API '{api_name}' is not available for {emulator_type}")
            logging.info(f"Available options: {available_apis}")

        return is_valid

    @classmethod
    def get_corrected_api(cls, api_name: str, emulator_type: str = "generic") -> str:
        """Get a corrected API name if the requested one is not available.

        Args:
            api_name: Requested graphics API name
            emulator_type: Type of emulator

        Returns:
            Corrected API name (may be the same if valid, or a fallback)
        """
        if cls.validate_api_selection(api_name, emulator_type):
            return api_name

        # Return the best available alternative
        corrected = cls.get_best_default_api(emulator_type)
        logging.info(f"Corrected graphics API from '{api_name}' to '{corrected}' for {emulator_type}")
        return corrected


def detect_graphics_capabilities() -> GraphicsCapabilities:
    """Convenience function to detect graphics capabilities.

    Returns:
        GraphicsCapabilities object with detection results
    """
    return GraphicsDetector.detect_capabilities()


def get_default_graphics_api(emulator_type: str = "generic") -> str:
    """Convenience function to get the best default graphics API.

    Args:
        emulator_type: Type of emulator

    Returns:
        String name of the best available graphics API
    """
    return GraphicsDetector.get_best_default_api(emulator_type)


if __name__ == "__main__":
    # Demo/test code
    print("Graphics API Detection Demo")
    print("=" * 40)

    capabilities = detect_graphics_capabilities()

    print(f"DirectX available: {'YES' if capabilities.directx_available else 'NO'}")
    if capabilities.directx11_available:
        print("  - DirectX 11: Available")
    if capabilities.directx12_available:
        print("  - DirectX 12: Available")
    print(f"Vulkan available:  {'YES' if capabilities.vulkan_available else 'NO'}")
    print(f"OpenGL available:  {'YES' if capabilities.opengl_available else 'NO'}")

    print("\nSystem Info:")
    for key, value in capabilities.system_info.items():
        print(f"  {key}: {value}")

    print("\nRecommended defaults:")
    for emulator in ["memu", "bluestacks", "googleplay"]:
        default_api = get_default_graphics_api(emulator)
        print(f"  {emulator}: {default_api}")
