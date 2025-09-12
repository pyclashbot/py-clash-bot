import os
import time
import shutil
import zipfile
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
top_folder = r"recordings"
zip_folder = r"recordings_compressed"

# Global variables for background compression management
_compression_executor = None
_compression_lock = threading.Lock()
_is_compression_running = False

required_free_space_low_limit = 15  # percent
# Folder considered "too large" when it exceeds this size (in GB).
# Keep downstream logic consistent with this (sampling target uses same limit).
raw_recordings_too_large_limit_gb = 5  # 5 GB

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
    free_percent = _get_disk_free_space_percent(top_folder)
    is_low = free_percent < required_free_space_low_limit
    print(f"[DISK_SPACE_LOW] Disk space low check: {is_low} (free: {free_percent:.1f}%)")
    return is_low


# ---------------------------------------------------------------------
# Folder Size Helpers
# ---------------------------------------------------------------------
def _get_recordings_folder_size() -> int:
    """Get the total size of the recordings folder in bytes.

    Returns:
        int: Total size in bytes
    """
    print(f"[FOLDER_SIZE] Calculating size of {top_folder}")
    total_size = 0
    try:
        if not os.path.exists(top_folder):
            print("[FOLDER_SIZE] Recordings folder does not exist yet (size = 0)")
            return 0

        for dirpath, dirnames, filenames in os.walk(top_folder):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    size = os.path.getsize(filepath)
                    total_size += size

        size_gb = total_size / (1024**3)
        print(f"[FOLDER_SIZE] Total recordings folder size: {size_gb:.4f} GB ({total_size} bytes)")
        return total_size
    except Exception as e:
        print(f"[FOLDER_SIZE_ERROR] Failed to calculate folder size: {e}")
        return 0


def _is_recordings_folder_too_large() -> bool:
    """Check if recordings folder exceeds the configured size limit.

    Returns:
        bool: True if folder size > raw_recordings_too_large_limit_gb
    """
    size_bytes = _get_recordings_folder_size()
    size_gb = size_bytes / (1024**3)
    is_large = size_gb > raw_recordings_too_large_limit_gb
    print(f"[FOLDER_TOO_LARGE] Too large? {is_large} (size: {size_gb:.4f} GB, limit: {raw_recordings_too_large_limit_gb} GB)")
    return is_large


# ---------------------------------------------------------------------
# Zip / Compression Helpers
# ---------------------------------------------------------------------
def _ensure_zip_folder() -> None:
    """Ensure the destination zip folder exists."""
    try:
        os.makedirs(zip_folder, exist_ok=True)
    except Exception as e:
        print(f"[ZIP_FOLDER_ERROR] Failed to create zip folder '{zip_folder}': {e}")
        raise


def _get_next_zip_index() -> int:
    """Find the next available zip file index.

    Returns:
        int: Next available index for zip_N.zip filename
    """
    print(f"[ZIP_INDEX] Finding next zip file index in {zip_folder}")
    existing_indices = []

    try:
        # Ensure zip folder exists (so we can list it safely)
        _ensure_zip_folder()

        for filename in os.listdir(zip_folder):
            if filename.startswith("zip_") and filename.endswith(".zip"):
                try:
                    # Extract number from zip_N.zip
                    index_str = filename[4:-4]  # Remove "zip_" prefix and ".zip" suffix
                    index = int(index_str)
                    existing_indices.append(index)
                    print(f"[ZIP_INDEX] Found existing zip file: {filename} (index: {index})")
                except ValueError:
                    print(f"[ZIP_INDEX] Skipping invalid zip filename: {filename}")
                    continue

        next_index = max(existing_indices, default=-1) + 1
        print(f"[ZIP_INDEX] Next zip file index: {next_index}")
        return next_index

    except Exception as e:
        print(f"[ZIP_INDEX_ERROR] Failed to determine next zip index: {e}")
        return 0


def _sample_files_for_compression(target_size_gb: float = 0.1):
    """Sample files from recordings folder for compression.

    Args:
        target_size_gb: Target size in GB to sample. If None, uses the configured limit.

    Returns:
        list[str]: List of file paths to compress
    """
    print(f"[SAMPLING] Sampling files for compression (target: {target_size_gb} GB)")
    target_size_bytes = target_size_gb * (1024**3)

    try:
        if not os.path.exists(top_folder):
            print(f"[SAMPLING] Recordings folder doesn't exist")
            return []

        # Gather candidates recursively
        candidate_files = []
        for dirpath, _, filenames in os.walk(top_folder):
            for filename in filenames:
                # Include only selected patterns; extend as needed
                if (filename.startswith("fight_image_") and filename.endswith(".png")) or \
                   (filename.startswith("result_") and filename.endswith(".txt")):
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        size = os.path.getsize(filepath)
                        candidate_files.append((filepath, size))

        print(f"[SAMPLING] Found {len(candidate_files)} candidate files")

        if not candidate_files:
            return []

        # Shuffle to get random sampling
        random.shuffle(candidate_files)

        # Select files up to the target size (allow slight overshoot if still under 80% before last pick)
        selected_files = []
        current_size = 0

        for filepath, size in candidate_files:
            if current_size + size <= target_size_bytes:
                selected_files.append(filepath)
                current_size += size
            elif current_size < target_size_bytes * 0.8:
                selected_files.append(filepath)
                current_size += size
                break

        selected_size_gb = current_size / (1024**3)
        print(f"[SAMPLING] Selected {len(selected_files)} files ({selected_size_gb:.4f} GB)")
        return selected_files

    except Exception as e:
        print(f"[SAMPLING_ERROR] Failed to sample files: {e}")
        return []


def _compress_files_to_zip(files_to_compress) -> bool:
    """Compress selected files into a zip archive.

    Args:
        files_to_compress: List of file paths to compress

    Returns:
        bool: True if compression succeeded
    """
    if not files_to_compress:
        print(f"[COMPRESSION] No files to compress")
        return False

    # Ensure destination folder exists
    _ensure_zip_folder()

    zip_index = _get_next_zip_index()
    zip_filename = f"zip_{zip_index}.zip"
    zip_path = os.path.join(zip_folder, zip_filename)

    print(f"[COMPRESSION] Starting compression of {len(files_to_compress)} files to {zip_filename}")

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in files_to_compress:
                if os.path.isfile(file_path):
                    # Use just the filename in the zip (not the full path)
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
                    print(f"[COMPRESSION] Added to zip: {arcname}")

        # Verify zip was created successfully
        if os.path.exists(zip_path):
            zip_size = os.path.getsize(zip_path)
            zip_size_mb = zip_size / (1024**2)
            print(f"[COMPRESSION] Successfully created {zip_filename} ({zip_size_mb:.2f} MB)")

            # Delete original files after successful compression
            deleted_count = 0
            for file_path in files_to_compress:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"[COMPRESSION] Deleted original file: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"[COMPRESSION_ERROR] Failed to delete {file_path}: {e}")

            print(f"[COMPRESSION] Compression complete. Deleted {deleted_count} original files")
            return True
        else:
            print(f"[COMPRESSION_ERROR] Zip file was not created successfully")
            return False

    except Exception as e:
        print(f"[COMPRESSION_ERROR] Failed to create zip file: {e}")
        return False


# ---------------------------------------------------------------------
# Background Task Orchestration
# ---------------------------------------------------------------------
def _background_compression_task():
    """Background task to handle file compression."""
    global _is_compression_running

    print(f"[BG_COMPRESSION] Background compression task started")

    try:
        with _compression_lock:
            _is_compression_running = True

        # Sample files for compression (target size coheres with configured limit)
        files_to_compress = _sample_files_for_compression()

        if files_to_compress:
            # Perform compression
            success = _compress_files_to_zip(files_to_compress)
            if success:
                print(f"[BG_COMPRESSION] Background compression completed successfully")
            else:
                print(f"[BG_COMPRESSION] Background compression failed")
        else:
            print(f"[BG_COMPRESSION] No files selected for compression")

    except Exception as e:
        print(f"[BG_COMPRESSION_ERROR] Background compression task failed: {e}")
    finally:
        with _compression_lock:
            _is_compression_running = False
        print(f"[BG_COMPRESSION] Background compression task finished")


def _start_background_compression():
    """Start background compression if not already running."""
    global _compression_executor, _is_compression_running

    print(f"[BG_COMPRESSION_START] Checking if background compression needed")

    with _compression_lock:
        if _is_compression_running:
            print(f"[BG_COMPRESSION_START] Background compression already running, skipping")
            return

    # Initialize executor if needed (use only 1 thread to be unobtrusive)
    if _compression_executor is None:
        _compression_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="compression")
        print(f"[BG_COMPRESSION_START] Created compression thread pool")

    # Submit compression task
    print(f"[BG_COMPRESSION_START] Submitting background compression task")
    future = _compression_executor.submit(_background_compression_task)

    # Add callback to handle completion
    def compression_done_callback(fut):
        try:
            fut.result()  # This will raise any exception that occurred
        except Exception as e:
            print(f"[BG_COMPRESSION_CALLBACK_ERROR] Background compression failed: {e}")

    future.add_done_callback(compression_done_callback)


# ---------------------------------------------------------------------
# Public Save API
# ---------------------------------------------------------------------
def save_image(image: np.ndarray) -> bool:
    """Save an image into the recordings folder and optionally trigger background compression.

    - If disk space is low, triggers background compression and skips saving.
    - If recordings folder exceeds the configured size, triggers background compression.
    - Uses millisecond-precision timestamp to avoid filename collisions.
    - Accepts BGR (HxWx3) arrays. Grayscale (HxW) will be expanded to 3 channels.
    """
    print("[SAVE_IMAGE] Starting image save process")

    # If disk space is low, trigger compression and skip saving
    if _is_disk_space_low():
        print(f"[SAVE_IMAGE_SKIP] Skipping image save due to low disk space (<{required_free_space_low_limit}% free)")
        _start_background_compression()  # ensure we still attempt to free space
        return False

    # Check if recordings folder is too large and trigger compression
    if _is_recordings_folder_too_large():
        print(
            f"[SAVE_IMAGE] Recordings folder > {raw_recordings_too_large_limit_gb} GB, "
            "starting background compression"
        )
        _start_background_compression()

    # Ensure recordings directory exists
    print("[SAVE_IMAGE] Creating recordings directory")
    os.makedirs(top_folder, exist_ok=True)

    # Build a collision-resistant filename (millisecond precision + small random suffix)
    ts_ms = int(time.time() * 1000)
    suffix = random.randint(1000, 9999)
    fp = f"{top_folder}/fight_image_{ts_ms}_{suffix}.png"

    print(f"[SAVE_IMAGE] Target file: {fp}")

    # Convert image to RGB for PIL
    try:
        if image.ndim == 3 and image.shape[2] == 3:
            # Convert BGR (OpenCV) to RGB (PIL)
            rgb_image = image[..., ::-1]
        elif image.ndim == 2:
            # Expand grayscale to 3 channels
            rgb_image = np.stack([image, image, image], axis=-1)
        else:
            print(f"[SAVE_IMAGE_ERROR] Unsupported image shape: {getattr(image, 'shape', None)}")
            return False

        if rgb_image.dtype != np.uint8:
            # Safest approach: cast to uint8; adjust here if you require scaling
            rgb_image = rgb_image.astype(np.uint8)

        pil_image = Image.fromarray(rgb_image)
    except Exception as e:
        print(f"[SAVE_IMAGE_ERROR] Failed to prepare image for saving: {e}")
        return False

    # Write to disk
    try:
        print(f"[SAVE_IMAGE] Writing image to disk")
        pil_image.save(fp)
    except Exception as e:
        print(f"[SAVE_IMAGE_ERROR] Failed to save image file: {e}")
        return False

    # Verify file was saved
    if os.path.exists(fp):
        file_size = os.path.getsize(fp)
        print(f"[SAVE_IMAGE_SUCCESS] Saved fight image to {fp} ({file_size} bytes)")
        return True
    else:
        print(f"[SAVE_IMAGE_ERROR] Failed to save image file (missing after write)")
        return False
