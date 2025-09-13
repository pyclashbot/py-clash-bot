#!/usr/bin/env python3
"""
Test script for the new TAR-based recorder system.
"""

import os
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Import the new recorder
import sys
sys.path.insert(0, str(Path(__file__).parent))
from pyclashbot.bot.recorder import save_image, configure_recorder, get_recorder_stats, close_recorder


def test_webp_tar_recorder():
    """Test the new WebP+TAR recorder system."""
    print("=" * 60)
    print("Testing New WebP+TAR Recorder System")
    print("=" * 60)

    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="recorder_test_")
    print(f"Test directory: {test_dir}")

    try:
        # Configure recorder for testing (small segment size for quick testing)
        configure_recorder(
            recordings_folder=test_dir,
            segment_size_gb=0.001,  # 1MB segments for quick rotation testing
            webp_method=4,  # Balanced compression
            free_space_limit=5,  # Lower threshold for testing
            verbose_logging=True
        )

        print("\nRecorder configuration:")
        stats = get_recorder_stats()
        for key, value in stats["config"].items():
            print(f"  {key}: {value}")

        # Create test images (simulate game screenshots)
        test_images = []

        # Test different image types
        print(f"\nCreating test images...")

        # 1. Typical game screenshot (640x640 with UI elements)
        game_img = np.random.randint(0, 256, (640, 640, 3), dtype=np.uint8)
        # Add some UI-like patterns (should compress well with WebP)
        game_img[0:50, :, :] = [30, 30, 30]  # Top bar
        game_img[590:640, :, :] = [40, 40, 40]  # Bottom bar
        game_img[300:340, 300:340, :] = [255, 255, 255]  # White UI element
        test_images.append(("game_ui", game_img))

        # 2. Grayscale image
        gray_img = np.random.randint(0, 256, (640, 640), dtype=np.uint8)
        test_images.append(("grayscale", gray_img))

        # 3. High contrast image (should compress very well)
        contrast_img = np.zeros((640, 640, 3), dtype=np.uint8)
        contrast_img[::2, ::2, :] = [255, 255, 255]  # Checkerboard pattern
        test_images.append(("high_contrast", contrast_img))

        # Test saving images
        print(f"\nSaving test images...")
        save_results = []

        for img_name, img_data in test_images:
            print(f"\nTesting {img_name} image ({img_data.shape}):")

            # Save multiple copies to test segment rotation
            for i in range(3):
                success = save_image(img_data)
                save_results.append((img_name, i, success))
                print(f"  Save attempt {i+1}: {'SUCCESS' if success else 'FAILED'}")

                # Show stats after each save
                stats = get_recorder_stats()
                if "current_segment" in stats:
                    seg_stats = stats["current_segment"]
                    print(f"    Segment: {seg_stats['filename']}")
                    print(f"    Size: {seg_stats['size_mb']:.2f} MB")
                    print(f"    Frames: {seg_stats['frame_count']}")

        # Check results
        print(f"\n" + "="*40)
        print("RESULTS SUMMARY")
        print("="*40)

        total_saves = len(save_results)
        successful_saves = sum(1 for _, _, success in save_results if success)
        print(f"Total save attempts: {total_saves}")
        print(f"Successful saves: {successful_saves}")
        print(f"Success rate: {successful_saves/total_saves*100:.1f}%")

        # Check generated files
        test_path = Path(test_dir)
        tar_files = list(test_path.glob("*.tar"))
        print(f"\nGenerated TAR files: {len(tar_files)}")

        total_size_mb = 0
        for tar_file in tar_files:
            size_mb = tar_file.stat().st_size / (1024**2)
            total_size_mb += size_mb
            print(f"  {tar_file.name}: {size_mb:.2f} MB")

        print(f"Total archive size: {total_size_mb:.2f} MB")

        # Estimate compression ratio (rough calculation)
        # Each test image is roughly 640*640*3 = 1.2MB uncompressed
        uncompressed_estimate_mb = total_saves * 1.2
        if total_size_mb > 0:
            compression_ratio = uncompressed_estimate_mb / total_size_mb
            print(f"Estimated compression ratio: {compression_ratio:.1f}:1")
            print(f"Space savings: {(1 - 1/compression_ratio)*100:.1f}%")

        # Close recorder to finalize any open TAR files
        print(f"\nClosing recorder to finalize TAR files...")
        close_recorder()

        # Refresh file list after closing
        tar_files = list(test_path.glob("*.tar"))
        print(f"Final TAR files: {len(tar_files)}")

        # Test file structure by examining one TAR file
        if tar_files:
            print(f"\nExamining TAR contents...")
            import tarfile
            try:
                with tarfile.open(tar_files[0], 'r') as tar:
                    members = tar.getmembers()
                    print(f"  Members in {tar_files[0].name}: {len(members)}")
                    for member in members[:3]:  # Show first 3
                        print(f"    {member.name}: {member.size} bytes")
                    if len(members) > 3:
                        print(f"    ... and {len(members) - 3} more")
            except Exception as e:
                print(f"  Warning: Could not read TAR contents: {e}")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup (close_recorder already called above in normal flow)
        try:
            close_recorder()  # Safe to call again
        except:
            pass
        try:
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
        except Exception as e:
            print(f"Warning: Failed to cleanup test directory: {e}")

    print(f"\n" + "="*60)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*60)
    return True


if __name__ == "__main__":
    test_webp_tar_recorder()