import threading
import os
import time
from PIL import Image
import numpy as np


class Recorder:
    def __init__(self, emulator):
        self.emulator = emulator
        self.save_path = "recordings"
        os.makedirs(self.save_path, exist_ok=True)
        self.interval = 1.7  # seconds between screenshots
        self._recording_thread = None
        self._stop_event = threading.Event()

    def save_image(self, image, subfolder_name):
        # Convert numpy array to PIL Image if needed
        if isinstance(image, np.ndarray):
            # Convert BGR to RGB if needed
            if image.shape[-1] == 3:
                image = image[..., ::-1]  # BGR to RGB
            image = Image.fromarray(image)

        # Make subfolder
        subfolder_path = os.path.join(self.save_path, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)

        # Craft path
        image_index = len(os.listdir(subfolder_path)) + 1
        image_path = os.path.join(subfolder_path, f"image_{image_index}.png")

        # Save to path
        image.save(image_path)

    def get_image(self):
        return self.emulator.screenshot()

    def _record(self, subfolder_name):
        while not self._stop_event.is_set():
            try:
                image = self.get_image()
                self.save_image(image, subfolder_name)
                time.sleep(self.interval)
            except Exception as e:
                print(f"[!] Recording error: {e}")
                break

    def start(self):
        # Determine subfolder name like fight_1, fight_2, ...
        index = 1
        while os.path.exists(os.path.join(self.save_path, f"fight_{index}")):
            index += 1
        subfolder_name = f"fight_{index}"

        # Reset stop event and start recording thread
        self._stop_event.clear()
        self._recording_thread = threading.Thread(
            target=self._record, args=(subfolder_name,), daemon=True
        )
        self._recording_thread.start()
        print(f"[✓] Started recording to '{subfolder_name}'")

    def stop(self):
        # Signal the thread to stop and wait for it
        if self._recording_thread and self._recording_thread.is_alive():
            self._stop_event.set()
            self._recording_thread.join()
            print("[✓] Recording stopped.")


if __name__ == "__main__":
    from pyclashbot.emulators.google_play import GooglePlayEmulatorController

    emulator = GooglePlayEmulatorController()
    recorder = Recorder(emulator)
    import time

    recorder.start()

    for i in range(10):
        time.sleep(1)
        print(f"Recording... {i + 1}")

    recorder.stop()
