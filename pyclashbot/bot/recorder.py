import os
import time
import shutil
import tarfile
import threading
import signal
import atexit
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
class RecorderConfig:
    """Configuration settings for the recorder system."""

    # Storage settings
    recordings_folder: str = r"recordings"
    required_free_space_low_limit: int = 15  # percent

    # Segment settings
    segment_size_limit_gb: float = 2.0  # GB - creates 4-6 files per day
    segment_rotation_check_interval: int = 10  # frames between rotation checks

    # WebP encoding settings
    webp_lossless_method: int = 6  # WebP effort level (0-6, higher = better compression)
    webp_quality: int = 100  # Not used in lossless mode, but kept for potential lossy option

    # Performance settings
    enable_verbose_logging: bool = True
    max_memory_usage_mb: int = 500  # Maximum memory for buffering before forcing rotation

    @classmethod
    def get_segment_size_bytes(cls) -> int:
        """Get segment size limit in bytes."""
        return int(cls.segment_size_limit_gb * (1024**3))


# Default configuration instance
config = RecorderConfig()

# ---------------------------------------------------------------------
# Disk Space Helpers
# ---------------------------------------------------------------------
def _get_disk_free_space_percent(path: str) -> float:
    """Check available disk space percentage for the given path.

    Handles the case where the path does not yet exist by checking the drive root.

    Returns:
        float: Free space percentage (0-100)
    """
    print(f"[DISK_CHECK] Checking disk space for path: {path}")
    try:
        p = Path(path)
        if p.exists():
            check_path = str(p)
        else:
            # Fall back to the path's anchor (drive root) or the current working drive root
            check_path = p.anchor or (Path.cwd().anchor or os.sep)

        total, used, free = shutil.disk_usage(check_path)
        free_percent = (free / total) * 100
        print(
            f"[DISK_CHECK] Total: {total//1024//1024//1024}GB, "
            f"Free: {free//1024//1024//1024}GB ({free_percent:.1f}%)"
        )
        return free_percent
    except Exception as e:
        print(f"[DISK_CHECK_ERROR] Failed to check disk space: {e}")
        # Assume space is available on error to avoid false negatives
        return 100.0


def _is_disk_space_low() -> bool:
    """Check if available disk space is below the configured limit.

    Returns:
        bool: True if disk space is critically low (< required_free_space_low_limit% free)
    """
    free_percent = _get_disk_free_space_percent(config.recordings_folder)
    is_low = free_percent < config.required_free_space_low_limit
    print(f"[DISK_SPACE_LOW] Disk space low check: {is_low} (free: {free_percent:.1f}%)")
    return is_low


# ---------------------------------------------------------------------
# TAR Segment Writer
# ---------------------------------------------------------------------
class TarSegmentWriter:
    """Manages writing frames directly to TAR archives with automatic rotation."""

    def __init__(self, base_folder: str = None, segment_size_gb: float = None):
        self.base_folder = Path(base_folder or config.recordings_folder)
        self.segment_size_limit = int((segment_size_gb or config.segment_size_limit_gb) * (1024**3))  # Convert to bytes
        self.current_tar: Optional[tarfile.TarFile] = None
        self.current_tar_path: Optional[Path] = None
        self.current_size = 0
        self.frame_counter = 0
        self.current_segment_frame_count = 0  # Track frames in current segment
        self.frames_since_flush = 0
        self.lock = threading.Lock()
        self._closed = False

        # Ensure base folder exists
        self.base_folder.mkdir(exist_ok=True)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False  # Don't suppress exceptions

    def _is_tar_corrupted(self, tar_path: Path) -> bool:
        """Check if a TAR file is corrupted or incomplete."""
        try:
            if not tar_path.exists() or tar_path.stat().st_size == 0:
                return True

            with tarfile.open(tar_path, 'r') as test_tar:
                # Try to list all members to verify integrity
                members = test_tar.getmembers()
                # Verify we can read at least the first member if any exist
                if members:
                    test_tar.extractfile(members[0])
            return False
        except Exception as e:
            print(f"[TAR_CORRUPTION_CHECK] Detected corruption in {tar_path.name}: {e}")
            return True

    def _recover_or_create_new_segment(self) -> bool:
        """Attempt to recover from corruption or create a new segment."""
        if self.current_tar_path and self._is_tar_corrupted(self.current_tar_path):
            print(f"[TAR_RECOVERY] Attempting recovery for {self.current_tar_path.name}")
            try:
                # Try to rename corrupted file for investigation
                backup_path = self.current_tar_path.with_suffix('.tar.corrupted')
                self.current_tar_path.rename(backup_path)
                print(f"[TAR_RECOVERY] Renamed corrupted file to {backup_path.name}")
            except Exception as e:
                print(f"[TAR_RECOVERY] Failed to backup corrupted file: {e}")

            # Force creation of new segment
            self.current_tar = None
            self.current_tar_path = None
            self.current_size = 0

        return self._open_new_segment()

    def _generate_segment_filename(self) -> str:
        """Generate a new segment filename with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_segment_{timestamp}.tar"

    def _open_new_segment(self) -> bool:
        """Open a new TAR segment for writing."""
        try:
            if self.current_tar is not None:
                self._close_current_segment()

            filename = self._generate_segment_filename()
            self.current_tar_path = self.base_folder / filename

            # Check if file already exists and is corrupted (shouldn't happen with timestamps, but safety check)
            if self.current_tar_path.exists() and self._is_tar_corrupted(self.current_tar_path):
                backup_path = self.current_tar_path.with_suffix('.tar.corrupted')
                self.current_tar_path.rename(backup_path)
                print(f"[TAR_SEGMENT] Moved existing corrupted file to {backup_path.name}")

            self.current_tar = tarfile.open(self.current_tar_path, 'w')
            self.current_size = 0
            self.current_segment_frame_count = 0
            self.frames_since_flush = 0

            print(f"[TAR_SEGMENT] Opened new segment: {filename}")
            return True

        except Exception as e:
            print(f"[TAR_SEGMENT_ERROR] Failed to open new segment: {e}")
            return False

    def _close_current_segment(self) -> None:
        """Close the current TAR segment with validation."""
        if self.current_tar is not None:
            try:
                # Force final flush before closing
                self._force_flush()

                # Close the TAR file
                self.current_tar.close()
                size_mb = self.current_size / (1024**2)
                print(f"[TAR_SEGMENT] Closed segment: {self.current_tar_path.name} ({size_mb:.2f} MB, {self.current_segment_frame_count} frames)")

                # Validate the closed file
                if self.current_tar_path:
                    validation_result = self._validate_closed_tar()
                    if not validation_result:
                        print(f"[TAR_SEGMENT_ERROR] TAR validation failed after closing {self.current_tar_path.name}")
                        self._handle_corrupted_tar()

            except Exception as e:
                print(f"[TAR_SEGMENT_ERROR] Error closing segment: {e}")
                if self.current_tar_path:
                    self._handle_corrupted_tar()
            finally:
                self.current_tar = None
                self.current_tar_path = None

    def _validate_closed_tar(self) -> bool:
        """Validate a closed TAR file for completeness."""
        try:
            if not self.current_tar_path.exists():
                print(f"[TAR_VALIDATION] TAR file doesn't exist: {self.current_tar_path}")
                return False

            file_size = self.current_tar_path.stat().st_size
            if file_size == 0:
                print(f"[TAR_VALIDATION] TAR file is empty: {self.current_tar_path}")
                return False

            # Try to open and read the TAR file
            with tarfile.open(self.current_tar_path, 'r') as test_tar:
                members = test_tar.getmembers()
                actual_frame_count = len(members)

                print(f"[TAR_VALIDATION] TAR contains {actual_frame_count} frames, expected {self.current_segment_frame_count}")

                # Validate frame count matches
                if actual_frame_count != self.current_segment_frame_count:
                    print(f"[TAR_VALIDATION] Frame count mismatch: expected {self.current_segment_frame_count}, got {actual_frame_count}")
                    return False

                # Validate each frame can be read
                for i, member in enumerate(members):
                    try:
                        # Try to extract the member to verify it's not truncated
                        data = test_tar.extractfile(member)
                        if data is None:
                            print(f"[TAR_VALIDATION] Failed to extract member {member.name}")
                            return False

                        frame_data = data.read()
                        if len(frame_data) != member.size:
                            print(f"[TAR_VALIDATION] Frame {member.name} is truncated: expected {member.size}, got {len(frame_data)}")
                            return False

                        # Only validate first few and last few frames to avoid performance issues
                        if i >= 3 and i < actual_frame_count - 3:
                            continue

                    except Exception as member_e:
                        print(f"[TAR_VALIDATION] Failed to validate member {member.name}: {member_e}")
                        return False

            print(f"[TAR_VALIDATION] TAR file validation passed: {self.current_tar_path.name}")
            return True

        except Exception as e:
            print(f"[TAR_VALIDATION] TAR validation error: {e}")
            return False

    def _handle_corrupted_tar(self):
        """Handle a corrupted TAR file by backing it up."""
        try:
            if self.current_tar_path and self.current_tar_path.exists():
                backup_path = self.current_tar_path.with_suffix('.tar.corrupted')
                counter = 1
                while backup_path.exists():
                    backup_path = self.current_tar_path.with_suffix(f'.tar.corrupted.{counter}')
                    counter += 1

                self.current_tar_path.rename(backup_path)
                print(f"[TAR_RECOVERY] Moved corrupted TAR to {backup_path.name}")
        except Exception as e:
            print(f"[TAR_RECOVERY] Failed to backup corrupted TAR: {e}")

    def _should_rotate_segment(self) -> bool:
        """Check if current segment should be rotated."""
        return self.current_size >= self.segment_size_limit

    def add_frame_bytes(self, frame_bytes: bytes) -> bool:
        """Add a frame as bytes to the current TAR segment with atomic writing.

        Args:
            frame_bytes: WebP encoded frame data

        Returns:
            bool: True if frame was added successfully
        """
        if self._closed:
            print(f"[TAR_SEGMENT_ERROR] Attempted to add frame to closed writer")
            return False

        if not frame_bytes or len(frame_bytes) == 0:
            print(f"[TAR_SEGMENT_ERROR] Empty frame data provided")
            return False

        with self.lock:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # Open new segment if needed or recover from corruption
                    if self.current_tar is None or self._should_rotate_segment():
                        if not self._recover_or_create_new_segment():
                            if attempt == max_retries - 1:
                                return False
                            continue

                    # Generate frame filename with timestamp and counter
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]  # milliseconds
                    frame_filename = f"frame_{timestamp}_{self.frame_counter:06d}.webp"

                    # Validate frame data integrity before writing
                    if not self._validate_frame_data(frame_bytes):
                        print(f"[TAR_SEGMENT_ERROR] Frame validation failed for {frame_filename}")
                        return False

                    # Create tarinfo from bytes
                    tarinfo = tarfile.TarInfo(name=frame_filename)
                    tarinfo.size = len(frame_bytes)
                    tarinfo.mtime = int(time.time())

                    # Atomic write operation
                    try:
                        # Create BytesIO stream for the frame
                        frame_stream = BytesIO(frame_bytes)

                        # Add to tar atomically
                        self.current_tar.addfile(tarinfo, frame_stream)

                        # Force flush immediately after each frame to prevent partial writes
                        self._force_flush()

                        # Update counters only after successful write and flush
                        self.current_size += len(frame_bytes)
                        self.frame_counter += 1
                        self.current_segment_frame_count += 1
                        self.frames_since_flush += 1

                        print(f"[TAR_SEGMENT] Added frame: {frame_filename} ({len(frame_bytes)} bytes)")
                        return True

                    except Exception as write_e:
                        print(f"[TAR_SEGMENT_ERROR] Failed atomic write for {frame_filename}: {write_e}")
                        if attempt < max_retries - 1:
                            print(f"[TAR_SEGMENT] Attempting recovery and retry...")
                            self.current_tar = None  # Force new segment
                            continue
                        return False

                except Exception as e:
                    print(f"[TAR_SEGMENT_ERROR] Frame write attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"[TAR_SEGMENT] Retrying frame write...")
                        continue
                    return False

            # If we get here, all retries failed
            print(f"[TAR_SEGMENT_ERROR] All retry attempts failed for frame")
            return False

    def _validate_frame_data(self, frame_bytes: bytes) -> bool:
        """Validate that frame data is a complete WebP image."""
        try:
            # Check minimum WebP file size and magic bytes
            if len(frame_bytes) < 12:
                return False

            # Check for WebP RIFF header
            if frame_bytes[:4] != b'RIFF':
                return False

            # Check for WebP signature
            if frame_bytes[8:12] != b'WEBP':
                return False

            # Verify the declared file size matches actual size
            declared_size = int.from_bytes(frame_bytes[4:8], byteorder='little') + 8
            if declared_size != len(frame_bytes):
                print(f"[TAR_SEGMENT_WARNING] WebP size mismatch: declared {declared_size}, actual {len(frame_bytes)}")
                return False

            return True

        except Exception as e:
            print(f"[TAR_SEGMENT_WARNING] Frame validation error: {e}")
            return False

    def _force_flush(self):
        """Force flush all buffered data to disk."""
        try:
            if self.current_tar and hasattr(self.current_tar, 'fileobj'):
                # Flush the tar file buffer
                if hasattr(self.current_tar.fileobj, 'flush'):
                    self.current_tar.fileobj.flush()

                # Force OS to write data to disk
                if hasattr(self.current_tar.fileobj, 'fileno'):
                    import os
                    os.fsync(self.current_tar.fileobj.fileno())

            print(f"[TAR_SEGMENT] Force flushed data to disk")

        except Exception as e:
            print(f"[TAR_SEGMENT_WARNING] Force flush failed: {e}")

    def close(self) -> None:
        """Close the writer and any open segments."""
        if self._closed:
            return

        with self.lock:
            try:
                self._close_current_segment()
                self._closed = True
                print(f"[TAR_SEGMENT] Writer closed properly")
            except Exception as e:
                print(f"[TAR_SEGMENT_ERROR] Error during close: {e}")
                self._closed = True


# ---------------------------------------------------------------------
# Global TAR writer instance
# ---------------------------------------------------------------------
_tar_writer: Optional[TarSegmentWriter] = None
_writer_lock = threading.Lock()


def _get_tar_writer() -> Optional[TarSegmentWriter]:
    """Get or create the global TAR writer instance."""
    global _tar_writer

    with _writer_lock:
        if _tar_writer is None:
            _tar_writer = TarSegmentWriter()
        return _tar_writer


def _encode_webp_lossless(image: np.ndarray) -> Optional[bytes]:
    """Encode a numpy array to WebP lossless bytes in memory.

    Args:
        image: BGR or RGB numpy array

    Returns:
        bytes: WebP encoded data, or None if encoding failed
    """
    try:
        # Convert image to RGB for PIL
        if image.ndim == 3 and image.shape[2] == 3:
            # Convert BGR (OpenCV) to RGB (PIL)
            rgb_image = image[..., ::-1]
        elif image.ndim == 2:
            # Expand grayscale to 3 channels
            rgb_image = np.stack([image, image, image], axis=-1)
        else:
            print(f"[WEBP_ENCODE_ERROR] Unsupported image shape: {getattr(image, 'shape', None)}")
            return None

        if rgb_image.dtype != np.uint8:
            rgb_image = rgb_image.astype(np.uint8)

        # Create PIL image and encode to WebP in memory
        pil_image = Image.fromarray(rgb_image)
        webp_buffer = BytesIO()

        # Save as WebP lossless with specified method (compression effort)
        pil_image.save(
            webp_buffer,
            format='WEBP',
            lossless=True,
            method=config.webp_lossless_method
        )

        webp_bytes = webp_buffer.getvalue()
        print(f"[WEBP_ENCODE] Encoded image to WebP: {len(webp_bytes)} bytes")
        return webp_bytes

    except Exception as e:
        print(f"[WEBP_ENCODE_ERROR] Failed to encode WebP: {e}")
        return None


# ---------------------------------------------------------------------
# Public Save API
# ---------------------------------------------------------------------
def save_image(image: np.ndarray) -> bool:
    """Save an image directly to TAR archive as WebP lossless.

    - Encodes image to WebP lossless in memory
    - Writes directly to current TAR segment
    - Automatically rotates segments based on size
    - Skips saving if disk space is critically low

    Args:
        image: BGR (HxWx3) or grayscale (HxW) numpy array

    Returns:
        bool: True if image was saved successfully
    """
    print("[SAVE_IMAGE] Starting direct TAR save process")

    try:
        # Check disk space before processing
        if _is_disk_space_low():
            print(f"[SAVE_IMAGE_SKIP] Skipping save due to low disk space (<{config.required_free_space_low_limit}% free)")
            return False

        # Encode image to WebP bytes in memory
        webp_bytes = _encode_webp_lossless(image)
        if webp_bytes is None:
            return False

        # Get TAR writer and add frame
        tar_writer = _get_tar_writer()
        if tar_writer is None:
            print(f"[SAVE_IMAGE_ERROR] Failed to get TAR writer")
            return False

        success = tar_writer.add_frame_bytes(webp_bytes)
        if success:
            print(f"[SAVE_IMAGE_SUCCESS] Saved frame to TAR archive ({len(webp_bytes)} bytes WebP)")
        else:
            print(f"[SAVE_IMAGE_ERROR] Failed to add frame to TAR archive")

        return success

    except Exception as e:
        print(f"[SAVE_IMAGE_ERROR] Unexpected error during save: {e}")
        return False


def close_recorder() -> None:
    """Close the recorder and finalize any open segments."""
    global _tar_writer

    with _writer_lock:
        if _tar_writer is not None:
            _tar_writer.close()
            _tar_writer = None
        print("[RECORDER] Closed recorder")


def configure_recorder(
    recordings_folder: Optional[str] = None,
    segment_size_gb: Optional[float] = None,
    webp_method: Optional[int] = None,
    free_space_limit: Optional[int] = None,
    verbose_logging: Optional[bool] = None
) -> None:
    """Configure recorder settings.

    Args:
        recordings_folder: Path to store recording segments
        segment_size_gb: Size limit for each segment in GB (affects file count per day)
        webp_method: WebP compression effort (0-6, higher = better compression but slower)
        free_space_limit: Minimum free disk space percentage before skipping saves
        verbose_logging: Enable detailed logging output
    """
    global _tar_writer

    if recordings_folder is not None:
        config.recordings_folder = recordings_folder
    if segment_size_gb is not None:
        config.segment_size_limit_gb = segment_size_gb
    if webp_method is not None:
        config.webp_lossless_method = max(0, min(6, webp_method))  # Clamp to valid range
    if free_space_limit is not None:
        config.required_free_space_low_limit = max(1, min(50, free_space_limit))  # Reasonable range
    if verbose_logging is not None:
        config.enable_verbose_logging = verbose_logging

    print(f"[RECORDER_CONFIG] Updated configuration:")
    print(f"  - Recordings folder: {config.recordings_folder}")
    print(f"  - Segment size: {config.segment_size_limit_gb}GB")
    print(f"  - WebP method: {config.webp_lossless_method}")
    print(f"  - Free space limit: {config.required_free_space_low_limit}%")
    print(f"  - Verbose logging: {config.enable_verbose_logging}")

    # Reset writer to apply new settings
    with _writer_lock:
        if _tar_writer is not None:
            _tar_writer.close()
            _tar_writer = None


def get_recorder_stats() -> dict:
    """Get current recorder statistics and status.

    Returns:
        dict: Recorder status information
    """
    stats = {
        "config": {
            "recordings_folder": config.recordings_folder,
            "segment_size_gb": config.segment_size_limit_gb,
            "webp_method": config.webp_lossless_method,
            "free_space_limit": config.required_free_space_low_limit,
        },
        "status": {
            "writer_active": _tar_writer is not None,
            "disk_space_ok": not _is_disk_space_low(),
        }
    }

    if _tar_writer is not None:
        stats["current_segment"] = {
            "size_mb": _tar_writer.current_size / (1024**2),
            "frame_count": _tar_writer.frame_counter,
            "filename": _tar_writer.current_tar_path.name if _tar_writer.current_tar_path else None,
        }

    return stats


# ---------------------------------------------------------------------
# Signal Handling for Graceful Shutdown
# ---------------------------------------------------------------------
def _signal_handler(signum, frame):
    """Handle termination signals by gracefully closing the recorder."""
    print(f"[RECORDER_SHUTDOWN] Received signal {signum}, closing recorder gracefully...")
    close_recorder()


def register_signal_handlers():
    """Register signal handlers for graceful shutdown. Called by main application."""
    try:
        signal.signal(signal.SIGINT, _signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, _signal_handler)  # Termination signal
        print("[RECORDER_SIGNAL] Registered signal handlers for graceful shutdown")
    except Exception as e:
        print(f"[RECORDER_SIGNAL_ERROR] Failed to register signal handlers: {e}")


def register_exit_handler():
    """Register atexit handler for cleanup. Called by main application."""
    try:
        atexit.register(close_recorder)
        print("[RECORDER_EXIT] Registered atexit handler for cleanup")
    except Exception as e:
        print(f"[RECORDER_EXIT_ERROR] Failed to register exit handler: {e}")


# Signal handlers will be registered by the main application
