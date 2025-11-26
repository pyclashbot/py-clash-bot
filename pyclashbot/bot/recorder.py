import csv
import json
import os
import time

import cv2
import numpy as np
from PIL import Image

from pyclashbot.utils.webhook import DECK_SCREENSHOT_WEBHOOK_URL, send_deck_screenshot_webhook

top_folder = r"recordings"

# Deck region for capturing deck area (x1, y1, x2, y2)
DECK_REGION = (80, 520, 400, 633)


def is_valid_play_input(play_coord, card_index):
    coords_max_limit = 700
    coords_low_limit = 0
    card_indices = [0, 1, 2, 3]

    if not isinstance(play_coord, tuple) or len(play_coord) != 2:
        print("[!] Warning. Your play coordinates are not a tuple of two integers.")
        return False

    if not (coords_low_limit <= play_coord[0] <= coords_max_limit):
        print(f"[!] Warning. Your play coordinates X are out of bounds: {play_coord[0]}")
        return False

    if not (coords_low_limit <= play_coord[1] <= coords_max_limit):
        print(f"[!] Warning. Your play coordinates Y are out of bounds: {play_coord[1]}")
        return False

    if card_index not in card_indices:
        print(f"[!] Warning. Your card index is not valid: {card_index}")
        return False

    return True


def save_play(play_coord, card_index, emulator=None):
    os.makedirs(top_folder, exist_ok=True)

    if not is_valid_play_input(play_coord, card_index):
        return False

    timestamp = int(time.time())
    fp = f"{top_folder}/play_{timestamp}.json"
    if os.path.exists(fp):
        return False

    data = {"play_coord": play_coord, "card_index": card_index}

    with open(fp, "w") as f:
        json.dump(data, f)
    print("Saved a fight play to", fp)

    # Capture deck screenshot if emulator is provided
    if emulator is not None:
        try:
            screenshot = emulator.screenshot()
            if screenshot is not None and screenshot.size > 0:
                height, width = screenshot.shape[:2]
                x1, y1, x2, y2 = DECK_REGION
                
                # Validate crop region is within screenshot bounds
                if 0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height:
                    deck_crop = screenshot[y1:y2, x1:x2]
                    if deck_crop.size > 0:
                        deck_fp = f"{top_folder}/deck_{timestamp}.png"
                        success = cv2.imwrite(deck_fp, deck_crop)
                        if success:
                            print("Saved deck screenshot to", deck_fp)
                            
                            # Optionally send to webhook if configured
                            if DECK_SCREENSHOT_WEBHOOK_URL:
                                try:
                                    # Encode image to PNG bytes
                                    _, encoded_img = cv2.imencode(".png", deck_crop)
                                    if encoded_img is not None:
                                        image_bytes = encoded_img.tobytes()
                                        send_deck_screenshot_webhook(
                                            image_bytes,
                                            DECK_SCREENSHOT_WEBHOOK_URL,
                                            timestamp=str(timestamp),
                                            play_coord=play_coord,
                                            card_index=card_index,
                                        )
                                except Exception as e:
                                    # Silently fail - don't interrupt play recording
                                    pass
        except Exception as e:
            # Silently fail - don't interrupt play recording if deck screenshot fails
            print(f"[!] Warning: Failed to save deck screenshot: {e}")

    return True


def save_win_loss(result: str):
    if type(result) is not str:
        print("[!] Warning. Result must be a string.")
        return False

    valid_results = ["win", "loss"]
    if result not in valid_results:
        print(f"[!] Warning. Result must be one of {valid_results}.")
        return False

    os.makedirs(top_folder, exist_ok=True)
    timestamp = int(time.time())
    fp = f"{top_folder}/result_{timestamp}.txt"
    if os.path.exists(fp):
        return False
    print("Saved a fight result to", fp)
    with open(fp, "w") as f:
        f.write(result)


def save_image(image: np.ndarray):
    print("Saving a fight image")
    os.makedirs(top_folder, exist_ok=True)

    timestamp = int(time.time())
    fp = f"{top_folder}/fight_image_{timestamp}.png"
    if os.path.exists(fp):
        print(f"[!] Warning. Fight image file {fp} already exists.")
        return False

    # Convert BGR (OpenCV) to RGB (PIL)
    rgb_image = image[..., ::-1]
    pil_image = Image.fromarray(rgb_image)
    pil_image.save(fp)
    print("Saved a fight image to", fp)
    return True


def to_csv():
    header = ["image_file", "play_coord_x", "play_coord_y", "card_index", "result"]
    rows = []

    files = os.listdir(top_folder)
    remaining_image_files = [f for f in files if f.startswith("fight_image_") and f.endswith(".png")]
    remaining_play_files = [f for f in files if f.startswith("play_") and f.endswith(".json")]
    result_files = [f for f in files if f.startswith("result_") and f.endswith(".txt")]

    # go fight by fight
    results_timestamps = []
    for results_file in result_files:
        result_timestamp = results_file.split("_")[1].split(".")[0]
        results_timestamps.append(result_timestamp)

    def get_image_files_before_timestamp(timestamp, range_length: int):
        files = [f for f in remaining_image_files if int(f.split("_")[2].split(".")[0]) <= int(timestamp)]
        return [f for f in files if int(f.split("_")[2].split(".")[0]) > int(timestamp) - range_length]

    def get_play_files_before_timestamp(timestamp, range_length: int):
        files = [f for f in remaining_play_files if int(f.split("_")[1].split(".")[0]) <= int(timestamp)]
        return [f for f in files if int(f.split("_")[1].split(".")[0]) > int(timestamp) - range_length]

    def extract_timestamp_from_filename(file_name):
        # fight_image_1754003855.png
        # play_1754004137.json
        # result_1754004114.txt
        try:
            parts = file_name.split("_")
            if len(parts) < 1:
                return None
            timestamp_part = parts[-1].split(".")[0]
            return int(timestamp_part)
        except Exception as e:
            print(f"[!] Warning! Could not extract timestamp from file name {file_name}: {e}")
            return None

    def find_images_in_range(play_timestamp, range_length: int, image_file_names):
        cutoff = play_timestamp - range_length

        timestamp2image_name = {}
        for image_file_name in image_file_names:
            image_timestamp = extract_timestamp_from_filename(image_file_name)

            if image_timestamp is None:
                continue

            if image_timestamp > cutoff and image_timestamp < play_timestamp:
                timestamp2image_name[image_timestamp] = image_file_name
            #     print('This image timestamp is in range:', image_timestamp, 'of this target_timestamp:', play_timestamp)
            # else:
            #     print('This image timestamp is out of range:', image_timestamp, 'from this target_timestamp:', play_timestamp)

        # sort the dict by timestamp
        sorted_timestamp2image_name = dict(sorted(timestamp2image_name.items(), key=lambda item: item[0]))

        # return the image names
        return list(sorted_timestamp2image_name.values())

    def find_no_play_images(image_files, play_files, buffer_seconds=6):
        no_play_image_files = []

        for image_file in image_files:
            image_timestamp = extract_timestamp_from_filename(image_file)
            if image_timestamp is None:
                continue

            close_to_play = False
            for play_file in play_files:
                play_timestamp = extract_timestamp_from_filename(play_file)
                if play_timestamp is None:
                    continue

                if abs(image_timestamp - play_timestamp) < buffer_seconds:
                    close_to_play = True
                    continue

            if not close_to_play:
                no_play_image_files.append(image_file)

        return no_play_image_files

    def timestamp2results_file(timestmap):
        fp = f"{top_folder}/result_{timestmap}.txt"
        if os.path.exists(fp):
            return fp

    def read_result(results_file):
        with open(results_file) as f:
            result = f.read().strip()
            return result

    # go results file by results file
    # mapping each image and play to the result
    play_rows_added = 0
    no_play_rows_added = 0
    results_timestamps = sorted(set(results_timestamps))
    for result_timestamp in results_timestamps:
        results_file = timestamp2results_file(result_timestamp)
        result = read_result(results_file)

        # grab the ones in range
        images = get_image_files_before_timestamp(result_timestamp, range_length=400)
        plays = get_play_files_before_timestamp(result_timestamp, range_length=400)

        print(f"This results timestamp: {result_timestamp}")
        print(f"\t-Has {len(images)} images and {len(plays)} plays")

        # delete them from the lists
        for image in images:
            remaining_image_files.remove(image)
        for play in plays:
            remaining_play_files.remove(play)

        # extract the plays where a play was made
        for play in plays:
            play_timestamp = extract_timestamp_from_filename(play)
            file_names = find_images_in_range(play_timestamp, 3, images)
            if not file_names:
                print(f"\t-Found no images for this play timestamp: {play_timestamp}")
                continue
            most_recent_image = file_names[-1]
            print(f"\tPlay: {play}, Most Recent Image: {most_recent_image}")
            play_data = json.load(open(f"{top_folder}/{play}"))
            print(f"Play play_coord: {play_data['play_coord']}")
            print("Type of play data[play_coord]:", type(play_data["play_coord"]))
            row = [
                most_recent_image,
                play_data["play_coord"][0],
                play_data["play_coord"][1],
                play_data["card_index"],
                result,
            ]
            rows.append(row)
            play_rows_added += 1

        no_play_images = find_no_play_images(images, plays, buffer_seconds=5)
        for no_play_image in no_play_images:
            print(
                f"\tNo play: Image found in results ts: {result_timestamp}:",
                no_play_image,
            )
            row = [
                no_play_image,
                None,  # No play coordinates
                None,  # No card index
                None,  # No card index
                result,
            ]
            rows.append(row)
            no_play_rows_added += 1

    print("\n---CSV Stats---")
    print(f"\t-Created a total of {len(rows)} rows")
    print(f"\t-Created a total of {play_rows_added} play rows")
    print(f"\t-Created a total of {no_play_rows_added} no play images")
    print(f"\t-Using {len(results_timestamps)} results files")

    csv_extraction_path = r"recordings/recordings.csv"

    with open(csv_extraction_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\t-Created the csv file at {csv_extraction_path}")


if __name__ == "__main__":
    print("\n" * 50)
    to_csv()
